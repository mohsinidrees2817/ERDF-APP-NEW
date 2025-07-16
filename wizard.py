# wizard.py
import streamlit as st
import os
import time
from io import BytesIO
from docx import Document
from openai import OpenAI
from streamlit_extras.switch_page_button import switch_page

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

wizard_steps = [
    "1 - Organisation & contact",
    "2 - Project idea",
    "3 - Programme & geography",
    "4 - Target group one-liner",
    "5 - Agenda 2030 & risk",
    "6 - Work-package generator",
    "7 - Policies & sign-off",
]

section_mapping = {
    0: "Project Summary",
    1: "Challenges and Needs",
    2: "Target Group",
    3: "Organisation Structure",
    4: "Risk Analysis",
    5: "Communication Plan",
    6: "Internal Policies",
}


def generate_from_ai(step_name, user_input):
    prompt = (
        f"**Your input:**\n{user_input}\n\n"
        f"**AI-generated draft for {step_name}:**\n"
        f"Please write professional ERDF application content for the section '{step_name}' using proper formatting, tables, and headings."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant writing EU project applications.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
            max_tokens=1000,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error: {e}"


def wizard_ui():
    email = st.session_state.get("user", "guest@example.com")
    username = email.split("@")[0]
    st.markdown(
        f"""
        <div style='background-color: #f5f5f5; padding: 1rem; border-radius: 8px;'>
        <b>🧙‍♂️ ERDF Application Wizard</b> | 👤 <span style='color:gray'>Logged in as: <strong>{username}</strong></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "step" not in st.session_state:
        st.session_state.step = 0
        st.session_state.edited_sections = {}

    step = st.session_state.step
    step_label = wizard_steps[step]
    step_input_key = f"step_{step}_input"

    st.subheader(f"Step {step+1}/{len(wizard_steps)}: {step_label}")
    st.divider()

    user_input = ""
    if step == 0:
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Organisation name", key="org_name")
            st.text_input("Registration number", key="reg_number")
        with col2:
            st.text_input("Contact name", key="contact_name")
            st.text_input("E-mail", key="email")
            st.text_input("Phone", key="phone")
        st.radio("Subject to LOU", ["Yes", "No"], key="lou")

        user_input = (
            f"Organisation Name: {st.session_state.org_name}\n"
            f"Registration Number: {st.session_state.reg_number}\n"
            f"Contact Name: {st.session_state.contact_name}\n"
            f"Email: {st.session_state.email}\n"
            f"Phone: {st.session_state.phone}\n"
            f"Subject to LOU: {st.session_state.lou}"
        )

    elif step == 1:
        st.text_area(
            "Short project idea (max 1,000 characters)",
            key="project_idea",
            max_chars=1000,
        )
        user_input = st.session_state.get("project_idea", "")

    elif step == 2:
        st.selectbox(
            "Programme area", ["Smart Growth", "Green Transition"], key="programme"
        )
        st.multiselect(
            "Region / municipality",
            ["Region North", "Region South", "Region East", "Region West"],
            key="region",
        )
        user_input = f"Programme: {st.session_state.programme}, Regions: {', '.join(st.session_state.region)}"

    elif step == 3:
        st.text_area("Target group description", key="target_group", max_chars=500)
        user_input = st.session_state.get("target_group", "")

    elif step == 4:
        st.multiselect(
            "Select 1-2 SDG goals", ["Goal 7", "Goal 9", "Goal 11"], key="sdg_goals"
        )
        st.multiselect(
            "Select up to 3 risks",
            ["Low participation", "Budget overrun", "Tech delays", "Staff turnover"],
            key="risks",
        )
        user_input = f"SDG Goals: {', '.join(st.session_state.sdg_goals)}; Risks: {', '.join(st.session_state.risks)}"

    elif step == 5:
        if "work_packages" not in st.session_state:
            st.session_state.work_packages = []
        wp_options = ["Digital Needs Analysis", "Pilot Lab", "SME Coaching"]
        for wp in wp_options:
            if st.button(f"Add {wp}"):
                st.session_state.work_packages.append(
                    {"name": wp, "description": f"Placeholder for {wp}"}
                )
        user_input = "\n".join(
            [
                f"{wp['name']}: {wp['description']}"
                for wp in st.session_state.work_packages
            ]
        )

    elif step == 6:
        st.radio("Procurement according to LOU", ["Yes", "No"], key="procurement_lou")
        user_input = f"Procurement under LOU: {st.session_state.procurement_lou}"

    st.session_state[step_input_key] = user_input

    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if step > 0 and st.button("◀ Previous"):
            st.session_state.step -= 1
            st.rerun()
    with col3:
        if step < len(wizard_steps) - 1 and st.button("Next ▶"):
            st.session_state.step += 1
            st.rerun()
        elif step == len(wizard_steps) - 1 and st.button(
            "✅ Submit All & Generate Document"
        ):
            with st.spinner("Generating all content with AI..."):
                for i in range(len(wizard_steps)):
                    label = wizard_steps[i]
                    user_input = st.session_state.get(f"step_{i}_input", "")
                    ai_text = generate_from_ai(label, user_input)
                    section_name = section_mapping.get(i, label)
                    st.session_state[f"step_{i}_generated"] = ai_text
                    st.session_state.edited_sections[section_name] = ai_text
                st.session_state["wizard_complete"] = True
                st.rerun();
                # switch_page("Dashboard")


wizard_ui()
