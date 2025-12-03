from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from generator import generate_and_parse_roadmap
from utils import attach_resources_to_all_topics

app=FastAPI()

class user_inputs(BaseModel):
    context: str
    time_period: str
    learnings: str

@app.post("/")
def generate_roadmap(user_input: user_inputs):
    parsed_output = asyncio.run(generate_and_parse_roadmap(user_input.context, user_input.time_period, user_input.learnings))
    enriched_output = asyncio.run(attach_resources_to_all_topics(parsed_output, user_input.context))
   
    return enriched_output