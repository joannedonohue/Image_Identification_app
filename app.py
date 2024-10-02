import base64
import requests
import streamlit as st
import io
from PIL import Image


# Need to have a config.py file with the following variables:
# open_api_key = "YOUR_OPENAI API KEY"
# groq_key = "YOUR_GROQ API KEY"

from config import open_api_key, groq_key

from groq import Groq
      
def encode_image_to_base64(image):
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")  # You can change this format to PNG or others
    return base64.b64encode(buffer.getvalue()).decode()      

def groq_llama_question_image(image_base64, question):
    
  client = Groq(
      api_key=groq_key,
  )

  chat_completion = client.chat.completions.create(
      messages=[
          {
              "role": "user",
              "content": [
              {
                "type": "text",
                "text": question
              },                
              {
                "type": "image_url",
                "image_url": {
                  "url": f"data:image/jpeg;base64,{image_base64}"
                }
              }
              ]
          }
      ],
      model="llama-3.2-11b-vision-preview",
  )
  
  try:
    print(chat_completion.choices[0].message.content)
  except:
    return "Error"
  
  return chat_completion.choices[0].message.content

def gpt4_question_image(image_base64, question):
  
  headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {open_api_key}"
  }

  payload = {    
    "model": "gpt-4o-mini",
    
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": question
          },
          {
            "type": "image_url",
            "image_url": {
              "url": f"data:image/jpeg;base64,{image_base64}"
            }
          }
        ]
      }
    ],
    "max_tokens": 300
  }

  response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
  
  response = response.json()
    
  try:
    print(response['choices'][0]['message']['content'])
  except:
    return "Error"
  
  return response['choices'][0]['message']['content']

if __name__ == "__main__":
  
  st.set_page_config(layout="wide")
  
  image = None
  
  with st.sidebar:
    
    st.markdown('# Models')
    
    selected_model = st.selectbox('s', ['Llama', 'GPT-4'], label_visibility='hidden')
  
  st.title('Image Analysis')
  st.divider()
    
  question = "Analyze this advertising campaign"
  
  col1, col2 = st.columns(2)
  
  
  with col1:
    uploaded_file = st.file_uploader("Image File(s)", type=["jpg", "png"], accept_multiple_files=False, help="Upload an image file")
    
  with col2:
    # check if the file is an image
    if uploaded_file:
      
      image = Image.open(uploaded_file)     
      st.image(image)
        
  with col1:
    button_container = st.container()

    question = st.text_input('Question', question)
    
      
  if button_container.button('Ask a question!', type="primary"):
    
    if image:

      with col1:

        with st.spinner('Analyzing...'):     
                        
          encoded_image = encode_image_to_base64(image)
                      
          if selected_model == 'Llama':
            response = groq_llama_question_image(encoded_image, question)
          else:
            response = gpt4_question_image(encoded_image, question)
            
          st.markdown(response)
          

