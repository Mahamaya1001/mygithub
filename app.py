import streamlit as st
import os
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
from streamlit_option_menu import option_menu

# Step 1: Load API Key from .env
load_dotenv()
google_api_key = os.getenv("API_KEY")

# Step 2: Configure GenAI
genai.configure(api_key=google_api_key)

# Step 3: Load Gemini Pro Model
def gemini_pro():
    return genai.GenerativeModel('gemini-pro')

# Step 4: Design Frontend
st.set_page_config(
    page_title="Chat with Gemini Model",
    page_icon="☕",
    layout="centered",
    initial_sidebar_state="expanded"
)

def roleForStreamlit(user_role):
    if user_role == 'model':
        return 'assistant'
    else:
        return user_role
    
# Creating a side bar in Streamlit
with st.sidebar:
    user_picked = option_menu(
        "Google Gemini AI",
        ["ChatBot", "Image Captioning"],
        menu_icon="wings",
        icons=["chat-dots-fill", "image-fill"],
        default_index=0
    )

if user_picked == 'ChatBot':
    model = gemini_pro()

    if "chat_history" not in st.session_state:
        st.session_state['chat_history'] = model.start_chat(history=[])

    st.title("👱‍♂️ Talk Bot")  

    # Display the chat history
    for message in st.session_state.chat_history.history:
        with st.chat_message(roleForStreamlit(message.role)):
            st.markdown(message.parts[0].text)

    # For getting User Input
    user_input = st.chat_input("Message TalkBot")  
    if user_input:
        st.chat_message("user").markdown(user_input) 
        response = st.session_state.chat_history.send_message(user_input) 

        # Extract the text from the response object 
        response_text = response.candidates[0].content.parts[0].text
        with st.chat_message("assistant"):
            st.markdown(response_text)

#Add the Image Captioning section here()  
# Step 5:Load Gemini Vision Model
def gemini_vision():
    model=genai.GenerativeModel('gemini-pro-vision')  
    return model

#get response from vision pro model
def gemini_vision_response(model, prompt, image):
    response= model.generate_content([prompt, image])
    return response.text

if user_picked == 'Image Captioning':
    # Load Gemini Vision Pro Model
    model = gemini_vision()
    st.title("☔ Image Captioning")

    #Upload an Image
    image_file = st.file_uploader("Upload an image", type=['jpg', 'jpeg','png'])

    user_prompt= st.text_input("Enter the prompt for image captioning")

    if st.button("Generate Caption"):
        
        load_image = Image.open(image_file)
        colLeft, colRight = st.columns(2)

        with colLeft:
            st.image(load_image.resize((800,500)))

        caption_response = gemini_vision_response(model, user_prompt, load_image) 

        with colRight:
            st.info(caption_response)   





