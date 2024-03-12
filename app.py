import streamlit as st
import PyPDF2
import difflib
import os
import google.generativeai as genai
import pandas as pd
import json
import layouts

from doc_utils import extract_text_from_upload
from prompts import generate_json_resume, match_resume_to_jd

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def main():
    
    st.title("Resume Buddy")
    tab1, tab2, tab3 = st.tabs(["Profile Information", "Match Parameters", "Layout Analysis"])
    json_resume = {}
    match_parameters = {}
    with st.sidebar:
        st.title("Menu:")
        uploaded_resume = st.file_uploader(
            "Upload your Resume (PDF) and Click on the Submit", type="pdf")
        job_description_text = st.text_area("Input Job Description, Leave Blank if not required")
        if st.button("Submit & Process"):
            with st.spinner("Processing..."):
                if uploaded_resume is not None and job_description_text != "":
                    text = extract_text_from_upload(uploaded_resume)
                    json_resume = generate_json_resume(text)
                    match_parameters = match_resume_to_jd(text, job_description_text)
                    st.success("Resume and Job Description Processed Successfully")
                elif uploaded_resume is None:
                    st.error("Please upload a Resume")
                elif job_description_text == "":
                    text = extract_text_from_upload(uploaded_resume)
                    json_resume = generate_json_resume(text)
                    st.success("Resume Processed Successfully")

    with tab1:
        st.subheader("Resume Information:")
        #st.write(json_resume)
        #Generate profile page using the JSON data
        if uploaded_resume is not None:
            st.write("Name: ",json_resume["basics"]["name"])
            st.write("Email: ",json_resume["basics"]["email"])
            st.write("Website: ",json_resume["basics"]["website"])
        else:
            st.write("Please upload a Resume")
        

    if tab3:
        with tab3:
            st.subheader("Layout Analysis:")
            with st.spinner("Processing..."):
                if uploaded_resume is not None:
                    pdf_parts = layouts.input_pdf_setup(uploaded_resume)
                    readability_score,explanation = layouts.get_layout_analysis(pdf_parts)
                    st.write(f"Readability Score: {readability_score}")
                    st.write(f"Explanation: {explanation}")
                else:
                    st.error("Please upload a Resume")

        
        


    with tab2:
        #st.subheader("Match Parameters:")
        #st.write(match_parameters)

        if match_parameters != {}:
            data = match_parameters

            matches_df = pd.DataFrame(data["explanations"]["matches"], index=range(len(data["explanations"]["matches"])))

            missing_df = pd.DataFrame(data["explanations"]["missing"],  index=range(len(data["explanations"]["missing"])))

            st.subheader(f"Match percentage: {data['match_percentage']}%")

            st.write("**Matches:**")
            st.table(matches_df)

            # Display the missing skills table
            st.write("**Missing skills:**")
            st.table(missing_df)



if __name__ == "__main__":
    main()
