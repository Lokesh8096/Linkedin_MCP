import streamlit as st
from src.linkedin_api import post_to_linkedin

def main():
    st.title("🚀 LinkedIn Auto Poster")

    day = st.text_input("Day")
    project = st.text_input("Project Title")
    techs = st.text_input("Technologies Used")
    future = st.text_input("Future Technologies to Learn (optional)")

    if st.button("Post to LinkedIn"):
        if not (day and project and techs):
            st.error("Please fill in Day, Project Title, and Technologies.")
        else:
            text = f"Day {day}\n\nProject: {project}\n\nTech Stack: {techs}"
            if future:
                text += f"\n\nUpcoming Learning: {future}"

            res = post_to_linkedin(text)
            if res.ok:
                st.success("✅ Posted to LinkedIn successfully!")
            else:
                st.error(f"❌ Failed to post. {res.status_code}: {res.text}")
