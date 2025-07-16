# -*- coding: utf-8 -*-
import re
import streamlit as st
from typing import Tuple  # Add this import

def convert_latex_delimiters(text: str) -> Tuple[str, int]:
    """
    Convert all LaTeX math environments to $...$ (inline) or $$...$$ (display) delimiters.
    Args:
        text: Input LaTeX text
    Returns:
        Tuple of (converted_text, conversion_count) where conversion_count is the number
        of math environments converted
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

    # First handle all display math environments that span multiple lines
    # \[...\] -> $$...$$
    convert_and_count(r'\\\[((?:.|\n)*?)\\\]', r'$$\1$$')

    # Other display math environments (equation, align, gather, etc.)
    display_envs = [
        'equation*', 'equation',
        'align*', 'align',
        'gather*', 'gather',
        'multline*', 'multline'
    ]

    for env in display_envs:
        pattern = rf'\\begin\{{{env}\}}((?:.|\n)*?)\\end\{{{env}\}}'
        convert_and_count(pattern, r'$$\1$$')

    # Inline math conversions
    # \(...\) -> $...$
    convert_and_count(r'\\\((.*?)\\\)', r'$\1$')

    # \ensuremath{...} -> $...$
    convert_and_count(r'\\ensuremath\{(.*?)\}', r'$\1$')

    return current_text, conversion_count

def main():
    st.set_page_config(
        page_title="LaTeX Delimiter Converter",
        page_icon="📝",
        layout="centered",
        initial_sidebar_state="expanded"
    )

    st.title("LaTeX Delimiter Converter")
    st.markdown("""
    Convert LaTeX math environments to standard `$...$` (inline) and `$$...$$` (display) delimiters.

    This tool will convert:
    - `\\(...\\)` → `$...$`
    - `\\[...\\]` → `$$...$$`
    - `\\begin{equation}...\\end{equation}` → `$$...$$`
    - And other math environments to their appropriate delimiters
    """)

    input_mode = st.radio(
        "Input mode:",
        ["Paste text", "Upload .tex file"],
        horizontal=True
    )

    input_text = ""

    if input_mode == "Paste text":
        input_text = st.text_area("Paste your LaTeX code here:", height=300)
    else:
        uploaded_file = st.file_uploader("Upload a .tex file", type=["tex"])
        if uploaded_file is not None:
            input_text = uploaded_file.read().decode("utf-8")

    if st.button("Convert Delimiters"):
        if not input_text.strip():
            st.warning("Please enter some LaTeX code or upload a file.")
            return

        with st.spinner("Converting delimiters..."):
            converted_text, count = convert_latex_delimiters(input_text)

        st.success(f"Converted {count} math environments!")

        st.subheader("Converted LaTeX")
        st.code(converted_text, language="latex")

        st.download_button(
            label="Download converted LaTeX",
            data=converted_text.encode("utf-8"),
            file_name="converted.tex",
            mime="text/plain"
        )

        st.subheader("Conversion Details")
        st.markdown("""
        ### What was converted:
        - Inline math:
          - `\\(...\\)` → `$...$`
          - `\\ensuremath{...}` → `$...$`
        - Display math:
          - `\\[...\\]` → `$$...$$`
          - `\\begin{equation}...\\end{equation}` → `$$...$$`
          - `\\begin{equation*}...\\end{equation*}` → `$$...$$`
          - `\\begin{align}...\\end{align}` → `$$...$$`
          - `\\begin{align*}...\\end{align*}` → `$$...$$`
          - `\\begin{gather}...\\end{gather}` → `$$...$$`
          - `\\begin{gather*}...\\end{gather*}` → `$$...$$`
        """)

if __name__ == "__main__":
    main()
