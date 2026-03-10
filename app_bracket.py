# -*- coding: utf-8 -*-
import re
import streamlit as st
from typing import Tuple

def convert_to_native_delimiters(text: str) -> Tuple[str, int]:
    """
    Convert $...$ (inline) or $$...$$ (display) delimiters to native LaTeX 
    \(...\) and \[...\] environments.
    
    Args:
        text: Input text with standard dollar-sign delimiters
    Returns:
        Tuple of (converted_text, conversion_count)
    """
    conversion_count = 0
    current_text = text  # Work on a copy that gets updated

    # Helper function to count conversions
    def convert_and_count(pattern, replacement, flags=0):
        nonlocal conversion_count, current_text
        new_text, count = re.subn(pattern, replacement, current_text, flags=flags)
        if count > 0:
            current_text = new_text
            conversion_count += count
        return new_text

    # 1. First handle display math ($$ ... $$)
    # We match $$ over multiple lines. Negative lookbehinds ensure we don't trip over escaped dollars.
    pattern_display = r'(?<!\\)\$\$((?:.|\n)*?)(?<!\\)\$\$'
    # Replace with \[ ... \]
    convert_and_count(pattern_display, r'\\\[\1\\\]')

    # 2. Next handle inline math ($ ... $)
    # Match single $ over multiple lines.
    pattern_inline = r'(?<!\\)\$((?:.|\n)*?)(?<!\\)\$'
    # Replace with \( ... \)
    convert_and_count(pattern_inline, r'\\\(\1\\\)')

    return current_text, conversion_count

def main():
    st.set_page_config(
        page_title="LaTeX Delimiter Converter (Reverse)",
        page_icon="🔄",
        layout="centered",
        initial_sidebar_state="expanded"
    )

    st.title("Reverse LaTeX Delimiter Converter")
    st.markdown("""
    Convert standard `$ ... $` (inline) and `$$ ... $$` (display) delimiters back to native LaTeX formatting.

    This tool will convert:
    - `$$ ... $$` → `\\[ ... \\]`
    - `$ ... $` → `\\( ... \\)`
    """)

    input_mode = st.radio(
        "Input mode:",
        ["Paste text", "Upload .tex file"],
        horizontal=True
    )

    input_text = ""

    if input_mode == "Paste text":
        input_text = st.text_area("Paste your text here:", height=300)
    else:
        uploaded_file = st.file_uploader("Upload a .tex file", type=["tex", "txt", "md"])
        if uploaded_file is not None:
            input_text = uploaded_file.read().decode("utf-8")

    if st.button("Convert Delimiters"):
        if not input_text.strip():
            st.warning("Please enter some text or upload a file.")
            return

        with st.spinner("Converting delimiters..."):
            converted_text, count = convert_to_native_delimiters(input_text)

        st.success(f"Converted {count} math environments!")

        st.subheader("Converted LaTeX")
        st.code(converted_text, language="latex")

        st.download_button(
            label="Download converted text",
            data=converted_text.encode("utf-8"),
            file_name="converted_native.tex",
            mime="text/plain"
        )

        st.subheader("Conversion Details")
        st.markdown("""
        ### What was converted:
        - Display math:
          - `$$ ... $$` → `\\[ ... \\]`
        - Inline math:
          - `$ ... $` → `\\( ... \\)`
        
        *Note: Escaped dollar signs (`\\$`) are ignored during conversion.*
        """)

if __name__ == "__main__":
    main()
