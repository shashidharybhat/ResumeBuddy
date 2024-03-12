from PIL import Image
import os 
import pdf2image
import base64
import io
import google.generativeai as genai

safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

def get_gemini_response(prompt,pdf_content):
    model=genai.GenerativeModel('gemini-pro-vision',safety_settings=safety_settings)
    response=model.generate_content([prompt,pdf_content[0]])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        images=pdf2image.convert_from_bytes(uploaded_file.read())
        first_page=images[0]
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

#Create LLM prompt to get a score for the layout's readability
LAYOUT_READABILITY_PROMPT = """
You are a hiring manager and you are reviewing a resume. You want to score the layout's readability.
Provide a score from 1 to 10, where 1 is the worst and 10 is the best.
Provide only the score in the response and nothing else.
Consider the following resume:

"""
#Create LLM prompt to get an expanation for the layout's readability score
LAYOUT_READABILITY_EXPLANATION_PROMPT = """

You are a hiring manager and you are reviewing a resume. 
You have provided the given layout a score of <SCORE> for readability.
Now, provide an explanation for the score you gave.
Consider the following resume:

"""
#Create LLM prompt to get a score for the resume's 


def get_layout_analysis(pdf_parts):
    model=genai.GenerativeModel('gemini-pro-vision')
    readaility_score=get_gemini_response(LAYOUT_READABILITY_PROMPT,pdf_parts)
    readability_explanation=get_gemini_response(LAYOUT_READABILITY_EXPLANATION_PROMPT.replace("<SCORE>",readaility_score),pdf_parts)
    return readaility_score,readability_explanation