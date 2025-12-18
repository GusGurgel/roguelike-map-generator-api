from pydantic import BaseModel

class QueryStr(BaseModel):
    query: str