import tempfile
import pandas as pd
import streamlit as st

from gtts import gTTS
from pypdf import PdfReader
from key import GEMINI_API_KEY
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

st.title("Tinotenda J.T's Multilanguage Translation Application.")

user_text = st.text_area('Enter Text')
uploaded_file = st.file_uploader('Or Upload a Text File', type=['txt', 'pdf', 'xlsx', 'csv'])

languages = {
    "Afrikaans (South Africa)": "af-SA",
    "Chinese (Mandarin, Mainland)": "cmn-CN",
    "English (US)": "en-US",
    "French (France)": "fr-FR",
    "German (Germany)": "de-DE",
    "Hindi (India)": "hi-IN",
    "Italian (Italy)": "it-IT",
    "Japanese (Japan)": "ja-JP",
    "Korean (Korea)": "ko-KR",
    "Portuguese (Brazil)": "pt-BR",
    "Spanish (Spain)": "es-ES",}

select_language = st.selectbox('Choose a language', list(languages.keys()))

if st.button('Translate & Generate Speech'):
    if uploaded_file is not None:
        filename = uploaded_file.name

        if filename.endswith('.txt'):
            text_input = uploaded_file.read().decode('utf-8', errors='ignore')

        elif filename.endswith('.pdf'):
            with PdfReader(uploaded_file) as pdf:
                text_input = " "
                for page in pdf.pages:
                    text_input += page.extract_text() or " "

        elif filename.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            text_input = " ".join(df.columns) + "\n" + df.head().to_string()

        elif filename.endswith('.xlsx'):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            df = pd.read_excel(tmp_path, engine="openpyxl")
            text_input = " ".join(df.columns) + "\n" + df.head().to_string()

    else:
        text_input = user_text

    if text_input.strip() == '':
        st.error('Please enter text or upload a text file.')

    else:
        translation_prompt = f"""
        Translate this text to {select_language}.
        Return only the context-aware translated text. No explanations, options or formatting.
        Text: {text_input}"""

        st.info(f'Translating to {select_language}...')
        response = model.generate_content(translation_prompt)
        translated_text = response.text.strip()
        st.write('Translated text preview:', translated_text[:300])

        try:
            tts = gTTS(text=translated_text, lang=languages[select_language].split('-')[0])
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                tts.save(tmp.name)
                output_path = tmp.name

            st.audio(output_path, format='audio/mp3')
            with open(output_path, "rb") as mp3:
                st.download_button(
                    label="Download mp3 Speech File",
                    data=mp3,
                    file_name=f"Tinotenda J.T's Translated Speech: {select_language}.mp3",
                    mime='audio/mpeg')

        except Exception as error:
            st.error(f"Error during speech synthesis: {error}")