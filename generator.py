from dotenv import load_dotenv
from langchain.output_parsers import RetryWithErrorOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from langchain_openai import ChatOpenAI

load_dotenv()

llm_roadmap = ChatOpenAI(model="gpt-4.1-mini", temperature=0.4)

TEMPLATE = """
Generate roadmap for context:{context}
which should be completing within time-period: {time_period}
adjust the roadmap according to the prior knoweledge :{learnings}

roadmap should be:
-divide it into weekly milestone with title
-for each week give topics with subtopics
-clean and concise
-divide weekly
-for each week, include a list of practical tasks or small projects with detail
-structured it in JSON

format example:

{{
  "Week 1": {{
    "Title": "title of week",
    "Topics": [
      {{
        "Title": "title of topic",
        "Subtopics": []
      }}
    ],
    "Projects": [],
    "Resources": []
  }}
}}
"""

parser = JsonOutputParser()
retry_parser = RetryWithErrorOutputParser.from_llm(parser=parser, llm=llm_roadmap)



async def generate_and_parse_roadmap(context,time_period,learnings):
    """Generates the initial roadmap using the LLM."""
    formatted_prompt = ChatPromptTemplate.from_template(TEMPLATE).format_prompt(
        context=context,
        time_period=time_period,
        learnings=learnings
    )
    response = await llm_roadmap.ainvoke(formatted_prompt.to_messages())
    parsed_output = retry_parser.parse_with_prompt(response.content, formatted_prompt)
    
    return parsed_output