import asyncio
from generator import generate_and_parse_roadmap
from utils import attach_resources_to_all_topics


async def main(context):
    parsed_output = await generate_and_parse_roadmap()
    enriched_output = await attach_resources_to_all_topics(parsed_output, context)
    


# For Jupyter Notebook
if __name__ == "__main__":
    asyncio.run(main())