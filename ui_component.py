def display_enriched_output(enriched_output):
    """Display the enriched output in a structured format."""
    for week_key, week_data in enriched_output.items():
        # Week title
        print(f"### 📅 {week_key}: {week_data.get('Title', '')}")

        # Topics & Subtopics
        for topic in week_data.get("Topics", []):
            print(f"##### 🔹 {topic['Title']}")
            for sub in topic.get("Subtopics", []):
                print(f"  - {sub}")

        # Projects / Tasks
        print("##### 🎯 Projects/Tasks:")
        projects = week_data.get("Projects", [])
        if projects:
            for project_obj in projects:
                if isinstance(project_obj, dict):
                    print(f"  - **{project_obj.get('Title', 'N/A')}**")
                else:
                    print(f"- {project_obj}")
        else:
            print("- (No projects listed)")

        # Resources
        print("##### 🔗 Resources:")
        resources = week_data.get("Resources", [])
        if resources:
            for res in resources:
                title = res.get("title", "N/A")
                url = res.get("url", "#")
                print(f"  - {title} : {url}")
        else:
            print("- (No resources found)")

        # Divider between weeks
        print("---")

