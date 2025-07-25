# -*- coding: utf-8 -*

import streamlit as st
import re
import json
from datetime import datetime

# ---- App Configuration ----
st.set_page_config(
    page_title="LaTeX to Jupyter Notebook Converter",
    page_icon="📓",
    layout="centered"
)

# ---- Custom CSS for Better UI ----
st.markdown("""
    <style>
    .stTextArea textarea {
        font-family: 'Courier New', monospace;
        font-size: 14px;
    }
    .stDownloadButton button {
        background-color: #4CAF50 !important;
        color: white !important;
        font-weight: bold !important;
        transition: all 0.3s !important;
    }
    .stDownloadButton button:hover {
        background-color: #45a049 !important;
    }
    .stSpinner div {
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

# ---- App Header ----
st.title("🚀 TeX Studio to Colab Notebook Converter - © Michel Martins 😎")
st.markdown("""
Convert LaTeX-formatted mathematical content into Colab Notebook SFT format.
Paste your LaTeX content below and get a downloadable `.ipynb` file.
""")

# ---- Your Processing Functions ----
def transform_latex_equations(text):
    pattern = r'\\\[\s*(.*?)\s*\\\]'
    def replace_equation(match):
        equation = match.group(1)
        equation = re.sub(r'\s+', ' ', equation).strip()
        return f'\\[ {equation} \\]'
    return re.sub(pattern, replace_equation, text, flags=re.DOTALL)

def parse_input_to_notebook(text):
    notebook = {
        "cells": [],
        "metadata": {"colab": {"provenance": []}},
        "nbformat": 4,
        "nbformat_minor": 5
    }
    metadata_text = """# Metadata\n\n**Topic:** - Mathematics\n\n**Subtopic:** - \n\n**Difficulty:** - \n\n**Explanation:** -  \n\n**Sections:** - \n\n**Prompt:** - \t\n"""
    notebook["cells"].append({
        "cell_type": "markdown",
        "source": [metadata_text],
        "metadata": {},
        "id": "metadata_cell"
    })

    # First remove \end{document} if it exists in the text
    text = re.sub(r'\\end{document}.*', '', text, flags=re.DOTALL)

    sections = re.split(r"\\section\*{(\[.*?\])}", text)
    for i in range(1, len(sections), 2):
        section_title = sections[i]
        section_content = sections[i + 1].strip()
        
        # Add separator for SECTION_XX labels (like [SECTION_01], [SECTION_02], etc.)
        if re.search(r'\[SECTION_\d+\]', section_title.upper()):
            notebook["cells"].append({
                "cell_type": "markdown",
                "source": ["---"],
                "metadata": {},
                "id": f"separator_before_{section_title}"
            })
        # Also keep the original separator for PROMPT/RESPONSE
        elif re.search(r'\b(PROMPT|RESPONSE)\b', section_title.upper()):
            notebook["cells"].append({
                "cell_type": "markdown",
                "source": ["---"],
                "metadata": {},
                "id": f"separator_{i}"
            })
            
        # Remove any remaining \end{document} in section content
        section_content = re.sub(r'\\end{document}.*', '', section_content, flags=re.DOTALL)
        
        # Additional check for RESPONSE section to ensure no \end{document} remains
        if "RESPONSE" in section_title.upper():
            section_content = re.sub(r'\\end{document}.*', '', section_content, flags=re.DOTALL)
        
        notebook["cells"].append({
            "cell_type": "markdown",
            "source": [f"**{section_title}**\n\n{section_content}"],
            "metadata": {},
            "id": f"section_{i}"
        })

        atomic_parts = re.split(r"\\section\*{(\[atomic_.*?])}", section_content)
        if len(atomic_parts) > 1:
            for j in range(1, len(atomic_parts), 2):
                atomic_title = atomic_parts[j]
                atomic_content = atomic_parts[j + 1].strip()
                atomic_content = re.sub(r'\\end{document}.*', '', atomic_content, flags=re.DOTALL)
                atomic_content = re.sub(r'\\\[\s*(.*?)\s*\\\]', r'\\[\n\1\n\\]', atomic_content)
                atomic_content = atomic_content.replace("\n", "  \n")
                notebook["cells"].append({
                    "cell_type": "markdown",
                    "source": [f"**{atomic_title}**\n\n{atomic_content}"],
                    "metadata": {},
                    "id": f"{atomic_title}_{i}_{j}"
                })

    notebook["cells"].append({
        "cell_type": "markdown",
        "source": ["---"],
        "metadata": {},
        "id": "final_separator"
    })

    # Final cleanup of all cells to ensure no \end{document} remains
    for cell in notebook["cells"]:
        if cell["cell_type"] == "markdown":
            # Apply multiple cleanup steps
            cleaned_source = []
            for text in cell["source"]:
                # Replace escaped backslashes first
                text = text.replace("\\\\", "\\")
                # Remove \end{document} and anything after it
                text = re.sub(r'\\end{document}.*', '', text, flags=re.DOTALL)
                cleaned_source.append(text)
            cell["source"] = cleaned_source

    return notebook

def perform_substitutions(input_text):
    substitutions = [
        (r"\\\\", r"\\newline"),
        (r"\\frac", r"\\\\frac"),
        (r"\\right", r"\\\\right"),
        (r"\\rfloor", r"\\\\rfloor"),
        (r"\\begin", r"\\\\begin"),
        (r"\\theta", r"\\\\theta"),
        (r"\\_", r"_"),
    ]
    output_text = input_text
    for old, new in substitutions:
        output_text = re.sub(old, new, output_text)
    return output_text

def escape_latex_delimiters_in_notebook(notebook):
    delimiter_subs = [
        (r'\\\(', r'\\\('),
        (r'\\\)', r'\\\)'),
        (r'\\\[', r'\\\['),
        (r'\\\]', r'\\\]')
    ]
    for cell in notebook['cells']:
        if cell['cell_type'] == 'markdown':
            for i in range(len(cell['source'])):
                text = cell['source'][i]
                for old, new in delimiter_subs:
                    text = re.sub(old, new, text)
                cell['source'][i] = text
    return notebook
def extract_body_content(text):
    """Extract content between \begin{document} and \end{document}, ignoring everything else"""
    # Remove everything before \begin{document} if it exists
    begin_pos = text.find(r'\begin{document}')
    if begin_pos >= 0:
        text = text[begin_pos + len(r'\begin{document}'):]
    
    # Remove everything after \end{document} if it exists
    end_pos = text.find(r'\end{document}')
    if end_pos >= 0:
        text = text[:end_pos]
    
    return text.strip()

# ---- Main App Interface ----
input_text = st.text_area(
    "**Paste your LaTeX content here:**",
    height=300,
    placeholder=r"""\section*{[SECTION1]}
Content with LaTeX equations like \[\frac{1}{2}\] goes here...

\section*{[atomic_part1]}
More content with $\theta$ symbols""",
    help="Paste your LaTeX content with sections marked with \section*{}"
)

if st.button("**Convert to Jupyter Notebook**", type="primary"):
    if not input_text.strip():
        st.warning("Please enter some LaTeX content first!")
    else:
        with st.spinner("Processing your LaTeX content..."):
            try:
                # First extract the body content, ignoring document wrappers
                body_content = extract_body_content(input_text)
                # Process through transformations
                transformed_text = transform_latex_equations(input_text)
                output_text = perform_substitutions(transformed_text)
                structured_notebook = parse_input_to_notebook(output_text)
                final_notebook = escape_latex_delimiters_in_notebook(structured_notebook)

                # Convert to JSON string
                notebook_json = json.dumps(final_notebook, indent=2)

                # Create download button
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.success("✅ Conversion successful!")

                st.download_button(
                    label="⬇️ Download Jupyter Notebook (.ipynb)",
                    data=notebook_json,
                    file_name=f"converted_notebook_{timestamp}.ipynb",
                    mime="application/json",
                    help="Click to download the Jupyter Notebook file"
                )

                # Show preview (collapsible)
                with st.expander("Preview Notebook Structure"):
                    st.json(final_notebook)

            except Exception as e:
                st.error(f"Conversion failed: {str(e)}")

# ---- Footer ----
st.markdown("---")
st.caption("""
Built with Streamlit · [Host for free on Streamlit Community Cloud](https://streamlit.io/cloud)
""")
