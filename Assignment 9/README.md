# Product Describer Generator

## Overview

**Product Describer Generator** is a Streamlit-based AI application that generates concise, marketing-friendly product descriptions and slogans from images. It leverages Google's Gemini 1.5 Flash model to analyze uploaded product images and combine them with optional user-provided context to create structured output.

## Features

- Upload one or more product images
- Enter a unique product ID and optional description per image
- AI generates:
  - A short, stylish product description (max 3 sentences)
  - 3 marketing slogans
- Real-time preview of each uploaded image
- Download results in both:
  - PDF format
  - JSON format (structured, machine-readable)

## Tech Stack

- Python 3
- Streamlit (user interface)
- Google Generative AI (Gemini 1.5 Flash model)
- markdown2 + pdfkit (for PDF export)

## Installation

Ensure you have Python 3 installed. Then, in your terminal or PowerShell:

```bash
pip install streamlit google-generativeai markdown2 pdfkit
```

Install [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) and ensure it is added to your system PATH.

## Usage

Run the app using:

```bash
streamlit run Product_describer_App.py
```

The app opens in your browser. Upload product images, fill in the product ID and context, then click **Generate Descriptions**.

You can download results as:

- A styled PDF with all product descriptions and slogans
- A structured JSON file with the same data for integration or reuse

## Example JSON Output

```json
{
  "product_id": "mug001",
  "description": "A handcrafted ceramic mug with a natural glaze finish. Perfect for slow mornings and warm sips.",
  "slogans": [
    "Savor Every Sip.",
    "Handmade for Harmony.",
    "Warmth in Your Hands."
  ]
}
```

## Author

This app was developed by Mira Vallenius for HAMK course  AI APIs and Standalone AI Applications Spring 2025 / Week #5 Google Gemini and Anthropic Claude and Structured Output/ Assignment #9 to practice multimodal prompt engineering, user input integration, and structured text generation.

---

Feel free to modify the UI or model prompts to suit your own use case.
