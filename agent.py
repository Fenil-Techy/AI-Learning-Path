

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate

from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field

load_dotenv()

llm_agent = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

tavily_tool = TavilySearch(max_results=1)

search_tool = Tool.from_function(
    func=tavily_tool.invoke,
    name="TavilySearch",
    description="Useful for finding resources to learn a topic."
)

tools = [search_tool]

# --- Agent Setup ---
# Define Pydantic models for structured output
class ResourceOutput(BaseModel):
    title: str = Field(description="Title of the learning resource")
    url: str = Field(description="Direct URL link to the resource, prefer YouTube links")
    type: str = Field(description="Type of resource, e.g., 'Video', 'Course', 'Article', 'Link'")

class ResourcesList(BaseModel):
    resources: list[ResourceOutput] = Field(description="A list of high-quality, beginner-friendly resources")


agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You're a helpful research assistant. Use tools to find video resources from the youtube for the user.
    When providing resources, always output in the following JSON format:
    {{
      "resources": [
        {{
          "title": "Title of the resource",
          "url": "Direct URL link",
          "type": "Youtube Video"
        }}
      ]
    }}
    Ensure the URL is a direct, working link. Only provide one link per resource.
    """),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])


agent = create_tool_calling_agent(llm=llm_agent, tools=tools, prompt=agent_prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

