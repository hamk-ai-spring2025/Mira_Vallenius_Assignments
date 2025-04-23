import os
import base64
import streamlit as st
import google.generativeai as genai
import json
import markdown2
import pdfkit
import re
from PIL import Image

# Configure API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="Product Describer Generator", layout="centered")
st.title("Product Describer Generator")

# File upload
uploaded_files = st.file_uploader("Upload 1 or more product images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
user_inputs = []
product_ids = []

if uploaded_files:
    for i, file in enumerate(uploaded_files):
        st.image(file, caption=f"Preview of Product {i+1}", width=200)
        product_id = st.text_input(f"Product ID for Product {i+1}", key=f"pid_{i}")
        user_input = st.text_area(f"Description for Product {i+1}", key=f"desc_{i}")
        product_ids.append(product_id)
        user_inputs.append(user_input)

submitted = st.button("Generate Descriptions")

# Image encoding
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.read()).decode("utf-8")

# Generation
if submitted and uploaded_files:
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    all_markdown_outputs = []
    all_json_outputs = []

    for idx, (uploaded_file, user_input, product_id) in enumerate(zip(uploaded_files, user_inputs, product_ids), start=1):
        image_base64 = encode_image(uploaded_file)

        prompt = [
            "You are a structured product content generator AI.",
            {"mime_type": uploaded_file.type, "data": image_base64},
            f"""
            User description: {user_input}

            Please output the result in strict JSON format, with this structure:
            description: a short, stylish product description (max 3 sentences)
            slogans: a list of 3 marketing slogans

            Do not include any markdown or explanations. Respond with a valid JSON object only.
            """
        ]

        with st.spinner(f"Analyzing Product {idx}..."):
            response = model.generate_content(prompt)

        raw_text = response.text.strip()
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)

        if not match:
            st.error(f"Failed to extract JSON for Product {idx}. Response: {raw_text}")
            continue

        try:
            result = json.loads(match.group())
            st.success(f"Product {idx} generated!")

            markdown_output = f"""
## Product {product_id or idx}

### Description
{result['description']}

### Marketing Slogans
""" + "\n".join([f"* {s}" for s in result["slogans"]])

            all_markdown_outputs.append(markdown_output)

            json_result = {
                "product_id": product_id or f"product_{idx}",
                "description": result["description"],
                "slogans": result["slogans"]
            }
            all_json_outputs.append(json_result)

        except json.JSONDecodeError as e:
            st.error(f"Failed to parse JSON for Product {idx}. Try again or check your prompt.")

    if all_markdown_outputs and all_json_outputs:
        full_markdown = "\n\n".join(all_markdown_outputs)
        st.markdown(full_markdown)

        html = markdown2.markdown(full_markdown)
        pdf_path = "output.pdf"
        json_path = "product_descriptions.json"

        config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        pdfkit.from_string(html, pdf_path, configuration=config)

        with open(pdf_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()

        with open(json_path, "w", encoding="utf-8", errors="ignore") as json_file:
            json.dump(all_json_outputs, json_file, ensure_ascii=False, indent=2)

        with open(json_path, "rb") as file:
            json_bytes = file.read()

        st.session_state["pdf_bytes"] = pdf_bytes
        st.session_state["json_bytes"] = json_bytes

if "pdf_bytes" in st.session_state and "json_bytes" in st.session_state:
    st.download_button("Download as PDF", data=st.session_state["pdf_bytes"], file_name="product_descriptions.pdf")
    st.download_button("Download as JSON", data=st.session_state["json_bytes"], file_name="product_descriptions.json")
