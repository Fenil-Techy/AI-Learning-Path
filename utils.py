import asyncio

import json
import re
from agent import agent_executor 


async def enrich_topic_with_resources(topic_title: str, context: str) -> dict:
    """Asynchronously enriches a single topic with resources using the agent."""
    query = f"""
    You're helping enrich a personalized learning roadmap.
    Now provide high-quality, beginner-friendly resources for: "{topic_title}" in context:{context}.
    Only include:
    - Title of the resource
    - Direct link, prefer youtube video
    - 1 link max
    No extra explanations.
    Always output in the following JSON format:
    {{
      "resources": [
        {{
          "title": "Title of the resource",
          "url": "Direct URL link",
          "type": "Type of resource (e.g., Video)"
        }}
      ]
    }}
    Ensure the URL is a direct, working link. Avoid repeating links already implied in earlier parts.
    """
    try:
        result = await agent_executor.ainvoke({"input": query})
        raw_output_string = result.get("output", "")

        valid_resources = []
        if raw_output_string:
            # *** ADD THIS CLEANING STEP ***
            # Remove leading/trailing markdown code block fences and 'json' tag
            cleaned_output_string = raw_output_string.strip()
            if cleaned_output_string.startswith("```json"):
                cleaned_output_string = cleaned_output_string[len("```json"):].strip()
            if cleaned_output_string.endswith("```"):
                cleaned_output_string = cleaned_output_string[:-len("```")].strip()
            # ---------------------------

            try:
                # Use the cleaned string for JSON parsing
                parsed_data = json.loads(cleaned_output_string)
                if isinstance(parsed_data, dict) and "resources" in parsed_data:
                    for res_item in parsed_data["resources"]:
                        if isinstance(res_item, dict) and res_item.get("url"):
                            valid_resources.append({
                                "title": res_item.get("title", "No Title"),
                                "url": res_item["url"],
                                "type": res_item.get("type", "Link")
                            })
                else:
                    print(f"⚠️ Agent output was JSON but not in expected 'resources' format for {topic_title}. Raw: {cleaned_output_string}")
            except json.JSONDecodeError:
                # This block should ideally not be hit if the JSON is correctly formatted by the LLM
                print(f"⚠️ Agent still did not output valid JSON after cleaning for {topic_title}. Attempting regex parsing. Raw: {cleaned_output_string}")
                # Fallback to regex (less ideal but keeps robustness)
                title_match = re.search(r"Title:\s*(.*?)(?=\n*- Direct Link:|\Z)", raw_output_string, re.DOTALL)
                url_match = re.search(r"Direct Link:\s*\[.*?\]\((.*?)\)", raw_output_string)

                title = title_match.group(1).strip() if title_match else raw_output_string
                url = url_match.group(1).strip() if url_match else ""

                if url:
                    valid_resources.append({"title": title, "url": url, "type": "Text (Parsed)"})
                else:
                    valid_resources.append({"title": raw_output_string, "url": "", "type": "Text (Raw)"})
        
        return valid_resources

    except Exception as e:
        print(f"❌ Failed to get resources for {topic_title}: {e}")
        return []
    
async def attach_resources_to_all_topics(parsed_output: dict, context: str) -> dict:
    """
    Collects all topic enrichment tasks and runs them concurrently
    using asyncio.gather.
    """
    all_topic_tasks = []
    topic_references = [] # To map results back to original topics

    for week_key, week_data in parsed_output.items():
        if "Topics" in week_data:
            for topic in week_data["Topics"]:
                all_topic_tasks.append(enrich_topic_with_resources(topic["Title"], context))
                topic_references.append((week_key, topic)) # Store reference to modify later

    # Run all resource enrichment tasks concurrently
    all_results = await asyncio.gather(*all_topic_tasks)
    

    week_resources_map = {}
    for i, resources in enumerate(all_results):
        week_key, _ = topic_references[i]
        if week_key not in week_resources_map:
            week_resources_map[week_key] = []
        week_resources_map[week_key].extend(resources)

    for week_key, week_data in parsed_output.items():
        week_data["Resources"] = week_resources_map.get(week_key, [])

    return parsed_output
