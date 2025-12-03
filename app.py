import streamlit as st
import requests

st.set_page_config(layout="wide", page_title="AI Learning Path")

st.title("📚 Personalized AI Learning Path")
st.markdown("Enter your **learning goals**, and get a **custom roadmap** with curated resources to guide your journey.")

# Input Section
with st.form("roadmap_form"):
    col1, col2 = st.columns(2)

    with col1:
        context = st.text_input("🎯 Learning Goal", placeholder="e.g. Machine learning engineer")

    with col2:
        time_period = st.text_input("⏳ Time Period", placeholder="e.g. 10 weeks")

    learnings = st.text_input("📘 Prior Knowledge", placeholder="e.g. Python or 'None' if you're a beginner")

    submitted = st.form_submit_button("🚀 Generate My Learning Path")

# Generation Section
if submitted:
    if not context or not time_period:
        st.warning("⚠️ Please fill in both the Learning Goal and Time Period.")
    else:
        try:
            # First spinner: generate roadmap
            with st.spinner("Generating your personalized learning path..."):
                response = requests.post(
                    "http://localhost:8000/",
                    json={
                        "context": context,
                        "time_period": time_period,
                        "learnings": learnings
                    }
                )
                enriched_output = response.json()
                if not enriched_output:
                    st.error("❌ No roadmap generated. Please check your inputs.")
                    st.stop()
                
                else:

            # Display Section
                    for week_key, week_data in enriched_output.items():
                        # Week title
                        st.markdown(f"### 📅 {week_key}: {week_data.get('Title', '')}")

                        # Topics & Subtopics
                        for topic in week_data.get("Topics", []):
                            st.markdown(f"##### 🔹 {topic['Title']}")
                            for sub in topic.get("Subtopics", []):
                                st.markdown(f"  - {sub}")

                        # Projects / Tasks
                        st.markdown("##### 🎯 Projects/Tasks:")
                        projects = week_data.get("Projects", [])
                        if projects:
                            for project_obj in projects:
                                if isinstance(project_obj, dict):
                                    st.markdown(f"  - **{project_obj.get('Title', 'N/A')}**")
                                
                                else:
                                    st.markdown(f"- {project_obj}")
                        else:
                            st.markdown("- (No projects listed)")

                        # Resources
                        st.markdown("##### 🔗 Resources:")
                        resources = week_data.get("Resources", [])
                        if resources:
                            for res in resources:
                                title = res.get("title", "N/A")
                                url = res.get("url", "#")
                                st.markdown(f"  - {title} : {url}")
                        else:
                            st.markdown("- (No resources found)")

                        # Divider between weeks
                        st.markdown("---")


        except Exception as e:
            st.error(f"❌ Error generating roadmap: {e}")
        