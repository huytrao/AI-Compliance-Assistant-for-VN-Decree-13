import streamlit as st
import google.generativeai as genai
import os
from pathlib import Path
import pypdf
import docx

def read_pdf(file):
    """Reads and extracts text from a PDF file."""
    try:
        pdf_reader = pypdf.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return None

def read_docx(file):
    """Reads and extracts text from a DOCX file."""
    try:
        doc = docx.Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading DOCX file: {e}")
        return None

def read_txt(file):
    """Reads and extracts text from a TXT file."""
    try:
        # The file uploader in Streamlit provides a BytesIO object.
        # We need to decode it to a string.
        return file.read().decode("utf-8")
    except Exception as e:
        st.error(f"Error reading TXT file: {e}")
        return None

def get_reference_docs_text(data_path):
    """Reads all reference documents from the data directory."""
    reference_texts = {}
    try:
        for file_path in data_path.iterdir():
            if file_path.is_file():
                st.write(f"Reading reference file: {file_path.name}")
                if file_path.suffix == ".pdf":
                    reference_texts[file_path.name] = read_pdf(str(file_path))
                elif file_path.suffix == ".docx":
                    reference_texts[file_path.name] = read_docx(str(file_path))
                elif file_path.suffix == ".txt":
                    with open(file_path, "r", encoding="utf-8") as f:
                        reference_texts[file_path.name] = f.read()
        return reference_texts
    except Exception as e:
        st.error(f"Could not read reference documents in the data directory: {e}")
        return None

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(page_title="Privacy Policy Checker", layout="wide")
    st.title("Privacy Policy Check with Gemini AI")

    # --- Sidebar for API Key ---
    with st.sidebar:
        st.header("Configuration")
        gemini_api_key = st.text_input("Enter your Gemini API Key", type="password", key="api_key")
        st.markdown(
            "Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)."
        )

    # --- Main content area ---
    st.subheader("1. Upload the company's Privacy Policy")
    uploaded_file = st.file_uploader(
        "Choose a file (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"]
    )

    if st.button("Analyze", disabled=(not uploaded_file or not gemini_api_key)):
        if not gemini_api_key:
            st.warning("Please enter your Gemini API Key in the sidebar.")
            return
        if not uploaded_file:
            st.warning("Please upload a policy file.")
            return

        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            st.error(f"Error configuring Gemini API: {e}")
            return

        with st.spinner("Processing... Please wait a moment."):
            # --- Read uploaded policy file ---
            file_extension = Path(uploaded_file.name).suffix
            policy_text = ""
            if file_extension == ".pdf":
                policy_text = read_pdf(uploaded_file)
            elif file_extension == ".docx":
                policy_text = read_docx(uploaded_file)
            elif file_extension == ".txt":
                policy_text = read_txt(uploaded_file)

            if not policy_text:
                st.error("Could not read content from the uploaded file.")
                return

            # --- Read reference documents ---
            data_path = Path("data")
            reference_texts = get_reference_docs_text(data_path)
            if not reference_texts:
                st.error("No reference documents found or could not be read.")
                return

            # --- Construct the prompt for Gemini ---
            prompt_parts = [
                "YOU ARE AN EXPERT IN DATA PRIVACY POLICY ANALYSIS.",
                "Below is a company's 'Privacy Policy' and reference documents on data security regulations (such as Vietnam's Decree 13, ISO, PCI-DSS).",
                "### POLICY DOCUMENT TO BE ANALYZED:",
                policy_text,
                "---",
                "### REFERENCE DOCUMENTS:",
            ]
            for name, text in reference_texts.items():
                prompt_parts.append(f"\n--- Start of {name} ---\n{text}\n--- End of {name} ---\n")

            prompt_parts.extend([
                "---",
                "### ANALYSIS REQUEST:",
                "Based on the provided reference documents, please perform the following requests and present the results in English, using Markdown format:",
                "1. **Key Points Summary:** Briefly summarize the most important clauses in the company's policy.",
                "2. **Compliance Analysis:** Compare the company's policy against each reference document (especially Vietnam's Decree 13). Point out clauses that appear to be compliant and those that may be lacking, unclear, or non-compliant.",
                "3. **Improvement Suggestions:** Provide specific recommendations to improve the policy, helping it better comply with the stated regulations and standards, especially the requirements of Vietnamese law.",
                "4. **Compliance Rating (Estimate):** Provide an estimate of the overall compliance level on a scale of 10 (e.g., 7/10) and briefly explain the score."
            ])

            # --- Generate content with Gemini ---
            try:
                st.info("Sending request to Gemini... This may take a moment.")
                response = model.generate_content(prompt_parts)
                st.subheader("Analysis Results")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred while calling the Gemini API: {e}")

if __name__ == "__main__":
    main()