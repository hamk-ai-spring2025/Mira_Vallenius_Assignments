# AI-Powered Scientific Article Generator (APA Style to PDF)

## Project Overview

This Python application automates the generation of a scientific article draft based on a user-provided topic. The goal is to produce a document with a standard scientific article structure, including an abstract, introduction, chapters with subchapters, conclusions, an APA-style reference list, and in-text APA citations. The application leverages a Large Language Model (LLM) – specifically Google's Gemini models via their API – to generate the article content in Markdown format. This Markdown is then converted into a structured PDF document.

The project was developed as an assignment to explore LLM capabilities in academic writing and document generation.

**Assignment Requirements:**
*   Input: Topic for a scientific article.
*   Output:
    *   Standard article structure (abstract to conclusions).
    *   Divided into chapters and subchapters with headings.
    *   Potential inclusion of tables.
    *   APA-style reference list.
    *   APA-style in-text citations.
*   Recommended Solution: Prompt LLM for Markdown, then convert to PDF.

## How It Works

The application follows these main steps:

1.  **User Input:**
    *   The user is prompted to enter a topic for the scientific article.
    *   The application attempts to infer the desired language of the article from the language of the input topic.

2.  **LLM Prompting (Google Gemini API):**
    *   A detailed, multi-lingual prompt is constructed for the Google Gemini API (`gemini-1.5-flash-latest` is the default, but configurable).
    *   The prompt instructs the LLM to:
        *   Generate a comprehensive article on the given topic.
        *   Use the language inferred from the topic.
        *   Adhere to a standard scientific article structure (Title, Abstract, Introduction, Chapters with subchapters, Tables/Figures, Conclusions, References).
        *   Format the entire output in Markdown.
        *   Generate an APA 7th edition style reference list, prioritizing sources with DOI (Digital Object Identifier).
        *   Include APA 7th edition style in-text citations.
        *   **Experimental Feature:** The LLM is asked to append an "assessment tag" (e.g., `[Assessment: Likely real]`, `[Assessment: Possibly generated/uncertain]`, `[Assessment: Fictional]`) to each reference in the reference list, indicating its own confidence in the reference's authenticity.

3.  **Markdown Generation & Processing:**
    *   The LLM's response (the Markdown article) is received.
    *   The application attempts to "trim" any extraneous text генerated by the LLM after the reference list to ensure the PDF ends cleanly. This is done by identifying the last reference entry with an assessment tag.
    *   The reference list is parsed from the Markdown to extract individual references and the LLM's self-assessment tags.

4.  **Markdown to PDF Conversion:**
    *   The (potentially trimmed) Markdown content is saved to a `.md` file.
    *   The `pypandoc` library (a Python wrapper for Pandoc) is used to convert the Markdown file into a PDF document.
    *   The conversion uses Pandoc's default PDF engine. For higher quality PDFs, especially with special characters or complex layouts, a LaTeX engine (like `xelatex` via `extra_args` in `pypandoc`) could be configured, but this requires a local LaTeX installation.

5.  **Output & LLM Reference Assessment Display:**
    *   The paths to the generated `.md` and `.pdf` files are displayed.
    *   The extracted references, along with the LLM's self-assessment for each, are printed to the console. This allows the user to see the LLM's "confidence" but **does not replace the need for manual verification.**
    *   A summary count of potentially uncertain or fictional references (based on the LLM's tags) is provided.

## Meeting the Assignment Requirements

*   **Topic Input:** Yes, the application takes a topic as input.
*   **Standard Article Structure:** Yes, the LLM is prompted to generate this structure. The quality and completeness depend on the LLM's output for the given topic.
*   **Chapters and Subchapters:** Yes, the LLM is instructed to use Markdown headings for this.
*   **Tables:** Yes, the LLM is prompted to include tables if relevant.
*   **APA Reference List:** Yes, this is a core instruction to the LLM.
*   **APA In-text Citations:** Yes, this is also instructed.
*   **Recommended Solution (Markdown to PDF):** Yes, this is the implemented approach.

**Successes:**

*   **Core Functionality:** The application successfully prompts the LLM, receives Markdown, and converts it to PDF.
*   **Structured Output:** The LLM generally produces a well-structured Markdown document.
*   **APA Styling (Attempted):** The LLM attempts to follow APA style for references and citations as instructed.
*   **Multi-lingual Capability (Attempted):** The application tries to generate the article in the language of the input topic by dynamically adjusting the prompt.
*   **LLM Self-Assessment (Experimental):** The feature requesting the LLM to assess its own generated references provides an interesting, albeit unreliable, insight into the LLM's "thinking."
*   **PDF Trimming:** Logic has been implemented to try and ensure the PDF ends cleanly after the reference list.

**Challenges & Limitations:**

*   **LLM Reliability & Hallucinations:**
    *   The primary challenge is the LLM's tendency to "hallucinate" – inventing sources, DOIs, or details that seem plausible but are incorrect. The LLM's self-assessment tags are an attempt to mitigate this by making the LLM "aware" of the issue, but they are not a foolproof solution. **Manual verification of all references, especially DOIs, is crucial.**
    *   The LLM may not always perfectly adhere to APA 7th edition formatting.
*   **Language Adherence:** While prompted, the LLM might occasionally revert to its default language or mix languages, especially with complex topics or if the input topic's language is ambiguous. The current language detection for the prompt is very basic.
*   **PDF Conversion Quality:** Using Pandoc's default PDF engine is convenient but may not always produce the most aesthetically pleasing or typographically perfect PDFs. A full LaTeX installation (e.g., MiKTeX, TeX Live) and configuring Pandoc to use an engine like `xelatex` would improve this but adds external dependencies.
*   **Content Depth and Scientific Accuracy:** The quality, depth, and scientific accuracy of the generated article are entirely dependent on the LLM's capabilities and the training data for the given topic. The generated text should be seen as a **first draft** requiring significant expert review and editing.
*   **"Scientific Publication" Length:** The prompt requests a "long and detailed" article, but achieving true publication-level length and rigor with a single LLM prompt is highly ambitious. The `max_output_tokens` parameter can be adjusted, but very long outputs can sometimes lead to a decrease in coherence.

## Prerequisites

*   Python 3.x
*   `pip` (Python package installer)
*   **Pandoc:** Must be installed separately and added to your system's PATH. Download from [pandoc.org](https://pandoc.org/installing.html).
*   **Google Cloud Project with Generative Language API enabled.**
*   **Google API Key:** An API key for the above project.

## Setup and Usage

1.  **Clone the repository (if applicable) or save the Python script.**

2.  **Set up your Google API Key:**
    Set an environment variable named `GOOGLE_API_KEY` to your API key value.
    *   **Windows (Command Prompt):**
        ```bash
        setx GOOGLE_API_KEY "YOUR_API_KEY_HERE"
        ```
        (Restart your command prompt or IDE after setting this.)
    *   **Linux/macOS (Terminal):**
        ```bash
        export GOOGLE_API_KEY="YOUR_API_KEY_HERE"
        ```
        (Add this line to your shell's startup file, e.g., `.bashrc`, `.zshrc`, for persistence.)

3.  **Install Python dependencies:**
    Navigate to the project directory in your terminal and run:
    ```bash
    pip install google-generativeai pypandoc
    ```
    *(Optional: For more advanced language detection, you could install `langdetect` with `pip install langdetect` and integrate it into the script.)*

4.  **Run the application:**
    ```bash
    python article_generatot_g3.py
    ```
    (Replace `article_generatot_g3.py` with the actual name of your Python file, e.g., `article_generator_g3.py`).

5.  **Follow the prompt:**
    *   Enter the topic for your scientific article when prompted. The application will attempt to use the language of your topic.

6.  **Check the output:**
    *   A `.md` file and a `.pdf` file will be generated in the same directory as the script.
    *   The console will display the LLM's assessment of the generated references. **Critically review these and the actual references.**

## Future Improvements (Potential)

*   **True DOI Validation:** Integrate with an API like CrossRef to programmatically check the validity of generated DOI links.
*   **Advanced Language Detection:** Use a dedicated library (e.g., `langdetect`) for more reliable language detection of the input topic to guide the LLM.
*   **Configurable PDF Engine:** Allow users to specify a Pandoc PDF engine (e.g., `xelatex`, `weasyprint`) if they have the necessary dependencies installed.
*   **Iterative Refinement:** Instead of one large prompt, break down the article generation into sections, allowing for review and refinement at each stage.
*   **GUI:** Develop a simple graphical user interface for easier use.