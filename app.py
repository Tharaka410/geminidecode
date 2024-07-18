from dotenv import load_dotenv
load_dotenv()                                                   # Load all the environment variables
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
from googletrans import Translator

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))             # Configure Gemini Pro Vision API



## Function to load Google Gemini Pro Vision API and get response
def get_gemini_response(input_text, image, prompt):
    try:
        model = genai.GenerativeModel('gemini-pro-vision')
        
                                                                              
        if image.mode != 'RGB':                                   # Ensure image is in the correct format
            image = image.convert('RGB')
        
        response = model.generate_content([input_text, image, prompt])
        
        # Extract text from response
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            print(response)
            return response.candidates[0].content.parts[0].text                  # actual summary part
        else:
            st.warning("No valid text found in the response.")
            return None
    except Exception as e:
        st.error(f"An error occurred while processing the request: {e}")
        return None

## Function to handle image upload and processing
def input_image_setup():
    uploaded_file = st.file_uploader("Choose an image of the document:", type=["jpg", "jpeg", "png"])
    image = None
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
    else:
        st.info("Please upload an image file to proceed.")
    return image

## Function to translate text to English (this is for some specific cases where the model displays the result 
## in the language of the document, we observed this in case of mainly Hindi documents)
def translate_to_english(text):
    translator = Translator()
    translation = translator.translate(text, dest='en')
    return translation.text

## Function to summarize the document
def summarize_document():
    if st.session_state.image:
        prompt = "Analyze the uploaded document and provide a summary as detailed as possible."
        response = get_gemini_response(prompt, st.session_state.image, prompt)
        if response:
            translated_response = translate_to_english(response)
            st.session_state.analysis_result = translated_response
        else:
            st.warning("Could not extract relevant information from the document.")

## Function to ask questions about the document
def ask_question():
    user_question = st.text_input("Enter your question:")
    if st.button("Ask Question"):
        if user_question:
            detailed_response = get_gemini_response(user_question, st.session_state.image, user_question)    #the session will be the same so it maintains context for the image
            if detailed_response:
                translated_response = translate_to_english(detailed_response)
                st.success("**Answer:**")
                st.write(translated_response)
            else:
                st.warning("Could not extract relevant information for the question.")
        else:
            st.warning("Please enter a question.")

## Main function for Streamlit app
def main():
    # Initialize Streamlit app
    st.set_page_config(page_title="GeminiDecode: Multilingual Document Analysis")
    st.header("GeminiDecode: Analyze Documents in Any Language")

    # Text description
    text = """
    Using Gemini Pro AI, this project analyzes documents in multiple languages. 
    Upload an image of your document and ask questions to extract key information, 
    transcending language barriers and boosting productivity. You can also ask questions 
    about the document to improve your knowledge on it.
    """

    styled_text = f"<span style='font-family:tahoma;'>{text}</span>"                                
    st.markdown(styled_text, unsafe_allow_html=True)

    # Initialize session state for image and analysis results
    if "image" not in st.session_state:
        st.session_state.image = None
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None

    # User input for image and question
    image = input_image_setup()
    if image:
        st.session_state.image = image

    if st.session_state.image and st.button("Analyze Document"):
        summarize_document()

    # Display analysis result if available
    if st.session_state.analysis_result:
        st.success("**Document Summary:**")
        st.write(st.session_state.analysis_result)

        # Add section for user to ask additional questions
        st.header("Ask more about the document")
        ask_question()

if __name__ == "__main__":
    main()
