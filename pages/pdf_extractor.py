import os
import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image
import re  # this is required for regular expression operation (eg: @, #, +)
from pdf2image import convert_from_bytes  # This has to be installed. Add it to requirements.txt
from dotenv import load_dotenv

# Step 1: Load API Key from .env
load_dotenv()
google_api_key = os.getenv("API_KEY")

if not google_api_key:
    st.error("API key is missing! Please check your .env file.")
else:
    # Step 2: Configure GenAI
    genai.configure(api_key=google_api_key)

    # Step 3: Load Gemini Pro Model
    model = genai.GenerativeModel('gemini-pro')

    # Step 4: Create "images" folder
    output_path = "images"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Step 5: Define function to convert PDF to images
    def pdf_to_images(pdf_file, output_path):
        images = convert_from_bytes(pdf_file.read())
        for i, image in enumerate(images):   # enumerate means it will convert into images
            image_path = os.path.join(output_path, f'page_{i+1}.jpg')
            image.save(image_path, 'JPEG')

    # Step 6: Load Gemini Vision Model & Configure the response
    def gemini_vision_response(input_text, image):
        vmodel = genai.GenerativeModel('gemini-pro-vision') # vmodel is short for "vision model"
        try:
            response = vmodel.generate_content([input_text, image])
        except Exception as e:
            st.error(f"Error generating content: {e}")
            return ""
        st.write(f"Response: {response}")
        return response[0].text if response and isinstance(response, list) and len(response) > 0 else ""

    # Step 7: Extract the company details
    def extract_project_details(response):
        st.write(f"Extracting details from response: {response}")
        pattern = r".+?,.+?,.+?,.+"
        matches = re.findall(pattern, response)
        
        # Split each match into a list of four elements
        matches = [match.split(",") for match in matches]

        # Filter rows with null values and rows with more than 4 columns
        matches = [
            match for match in matches
            if not any(field.strip().lower() == 'na' for field in match) and len(match) == 4
        ]
        return matches

    # Step 8: Define custom prompt
    custom_inst = '''Extract project details including Project Name, Task Name, Assigned to, and Progress in comma-separated format.
    Ensure accuracy and refrain from including additional information beyond the CSV format.
    Desired output format:
    Project Name, Task Name, Assigned to, Progress
    For example:
    Marketing, Campaign Analysis, Daisy, 0%
    Product Dev, Prototype Development, Ethan, 100%
    Please provide only the necessary details as mentioned above. Do not include any additional information such as page number or any other extraneous content.
    '''

    # Step 9: Frontend page design
    st.title("Project Details Extractor")
    pdf_files = st.file_uploader("Choose multiple...", type="pdf", accept_multiple_files=True)

    # Step 10: Configure the output
    response = []

    if pdf_files:
        for pdf_file in pdf_files:
            pdf_to_images(pdf_file, output_path)
            image_folder = "images"
            if os.path.exists(image_folder):
                st.write(f"Processing Images from PDF: {pdf_file.name}")
                for filename in os.listdir(image_folder):
                    if filename.lower().endswith((".jpg", '.jpeg', '.png')):
                        st.write(f"Processing Image: {filename}")
                        image_path = os.path.join(image_folder, filename)
                        image = Image.open(image_path)
                        st.image(image, caption=filename)
                        input_text = custom_inst
                        img_response = gemini_vision_response(input_text, image)
                        response.extend(extract_project_details(img_response))

        if response:
            df = pd.DataFrame(response, columns=["Project Name", "Task Name", "Assigned to", "Progress"])
            st.write(df)

            # Step 11: Saving dataframe to CSV file
            csv_file_path = "Gemini_Response.csv"
            df.to_csv(csv_file_path, index=False)
            st.write(f"Response is saved to CSV file: {csv_file_path}")
        else:
            st.write("No response to save.")

    # Step 12: Delete all processed images
    def delete_images(output_path):
        for filename in os.listdir(output_path):
            file_path = os.path.join(output_path, filename)
            if os.path.isfile(file_path) and filename.lower().endswith('.jpg'):
                os.remove(file_path)

    delete_images(output_path)
