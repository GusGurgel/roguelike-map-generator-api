# fastapi dev api.py --host "::" --port 8000
from tile import Tile
from vector_db import query_vector_store
from fastapi import FastAPI
from query_str import QueryStr

app = FastAPI()


@app.post("/query-vector-store/")
async def route_query_vector_store(query_str: QueryStr) -> list[Tile]:
    return query_vector_store(query_str.query)
