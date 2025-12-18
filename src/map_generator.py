from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain.messages import AIMessage
from pydantic import BaseModel
from typing import Literal
from llm_models import get_model, Providers, GroqModels

model = get_model(Providers.GROQ, GroqModels.OPENAI_GPT_OSS_120B)


class Feedback(BaseModel):
    sentiment: Literal["positive", "neutral", "negative"]
    summary: str


structured_model = model.with_structured_output(
    schema=Feedback.model_json_schema(), method="json_schema"
)

response1 = structured_model.invoke(
    "I love everything, the red color makes all better."
)
response2 = structured_model.invoke(
    "I really heat this. I don't like that everything is red."
)

print(response1)
print(response2)
