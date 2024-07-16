import os
import streamlit as st
import google.generativeai as genai
from PIL import Image
import re  # this is required for regular expression operation (eg: @, #, +)
from dotenv import load_dotenv
load_dotenv()

#Step1: Fetch API key. This is another method which faster than previous methods
genai.configure(api_key=os.getenv("api_key"))

#step2: load pro vision gemini
def get_gemini_response(input,image,prompt):#input is captioning, imgage is uploading it
    model=genai.GenerativeModel('gemini-pro-vision') #this is for images
    response=model.generate_content([input,image[0],prompt])
    return response.text

#step3: allowing user to upload the image
def input_image_setup(upload_file):
    if upload_file is not None:
        bytes_data=upload_file.getvalue()

        image_parts=[
            {
                "mime_type":upload_file.type, #mime is key upload_file is data
                "data":bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded") #if the uploaded file is empty

#step4: initialize & configure steamlit application
st.set_page_config(page_title="Gemini Health app") #1st try to run this & check the page title

st.header("Gemini Health App")

input=st.text_input("Input Prompt : ", key="input")
upload_file=st.file_uploader("Choose an Image...", type=["jpg","jpeg","png"])

image=""

if upload_file is not None: 
    image=Image.open(upload_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

submit=st.button("Submit") # Run this to check for any errors

#step5: Prompt Creation
input_prompt="""
You are an expert in nutritionist where you need to see food items from the image and calculate 
total calories, also provide the details of every food items which calories intake is below format

1. Item 1  - no of calories
2. Item 2  - no of calories
-----------------------
-----------------------
"""
#Step6: operations once submit button is clicked
if submit:
    image_data=input_image_setup(upload_file)
    response=get_gemini_response(input_prompt,image_data,input)
    st.subheader("The response is")
    st.write(response) #download some food image & check if this model works as expected

#now lets dockerize the GenAI 
#Step1 : Create Docker file use slim edition because it lighere compance to bullseye