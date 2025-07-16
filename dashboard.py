# dashboard.py
import streamlit as st
from docx import Document
from io import BytesIO
import re

section_titles = [
    "Full Document Preview",
    "Project Summary",
    "Challenges and Needs",
    "Target Group",
    "Organisation Structure",
    "Risk Analysis",
    "Communication Plan",
    "Internal Policies",
]


def clean_content(content):
    if not content:
        return ""
    content = re.sub(r"\*\*Your input:\*\*.*?\n\n", "", content, flags=re.DOTALL)
    content = re.sub(r"\*\*AI-generated draft for .*?:\*\*\n\n", "", content)
    return content.strip()


def format_section_content(content):
    cleaned = clean_content(content)
    if not cleaned:
        return "*No content provided for this section*"
    if "|" in cleaned and "-" in cleaned:
        return cleaned
    return cleaned


def add_markdown_table_to_doc(doc, markdown_text):
    lines = [line.strip() for line in markdown_text.strip().splitlines() if "|" in line]
    if len(lines) < 2:
        doc.add_paragraph(markdown_text)
        return

    headers = [cell.strip() for cell in lines[0].strip("|").split("|")]
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    hdr_cells = table.rows[0].cells
    for i, cell in enumerate(headers):
        hdr_cells[i].text = cell

    for line in lines[2:]:
        cols = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cols) != len(headers):
            continue  # skip malformed rows
        row_cells = table.add_row().cells
        for i, cell in enumerate(cols):
            row_cells[i].text = cell


def dashboard_ui():
    user = st.session_state.get("user", "guest@example.com")
    st.markdown(
        f"""
        <div style="background-color: #f5f5f5; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
            <h2>📋 ERDF Application Dashboard</h2>
            <p>👤 Logged in as: <strong>{user}</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.title("Navigation")
    selected_section = st.sidebar.radio("Sections", section_titles)

    if selected_section == "Full Document Preview":
        st.subheader("📄 Complete Application Document")
        st.markdown("---")

        with st.container():
            for i, section in enumerate(section_titles[1:], 1):
                st.markdown(f"## {i}. {section}")
                content = st.session_state.edited_sections.get(
                    section, st.session_state.get(f"step_{i-1}_generated", "")
                )
                st.markdown(format_section_content(content))
                st.markdown("---")

        with st.expander("✏️ Edit Sections"):
            selected_edit = st.selectbox("Select section to edit:", section_titles[1:])
            section_index = section_titles.index(selected_edit) - 1
            content = st.session_state.edited_sections.get(
                selected_edit,
                st.session_state.get(f"step_{section_index}_generated", ""),
            )
            edited = st.text_area(
                f"Edit {selected_edit}",
                value=content,
                height=200,
                key=f"full_preview_edit_{section_index}",
            )
            if st.button(f"💾 Save changes to {selected_edit}"):
                st.session_state.edited_sections[selected_edit] = edited
                st.success(f"Changes to {selected_edit} saved!")
                st.rerun()

        st.markdown("---")
        st.subheader("Export Options")

        if st.button("⬇️ Download as DOCX"):
            doc = Document()
            doc.add_heading("ERDF Application", 0)
            for i, section_name in enumerate(section_titles[1:]):
                doc.add_heading(f"{i+1}. {section_name}", level=1)
                content = st.session_state.edited_sections.get(
                    section_name, st.session_state.get(f"step_{i}_generated", "")
                )
                cleaned_content = clean_content(content)
                if "|" in cleaned_content and "-" in cleaned_content:
                    add_markdown_table_to_doc(doc, cleaned_content)
                else:
                    doc.add_paragraph(cleaned_content)
            buffer = BytesIO()
            doc.save(buffer)
            st.download_button(
                "Download DOCX",
                buffer.getvalue(),
                file_name="ERDF_Application.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        return

    # Single section view
    st.subheader(f"✏️ {selected_section}")
    section_index = section_titles.index(selected_section) - 1
    content = st.session_state.edited_sections.get(
        selected_section,
        st.session_state.get(
            f"step_{section_index}_generated", "No content available yet."
        ),
    )
    edited_content = st.text_area(
        "Edit this section:", value=content, height=400, key=f"edit_{selected_section}"
    )
    if st.button("💾 Save Changes"):
        st.session_state.edited_sections[selected_section] = edited_content
        st.success("Changes saved to your application!")

    st.divider()
    st.subheader("Your Original Input")
    user_input = st.session_state.get(
        f"step_{section_index}_input", "No input provided."
    )
    st.info(user_input)


dashboard_ui()
