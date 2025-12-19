# fastapi dev api.py --host "::" --port 8000
from vector_db import query_vector_store
from fastapi import FastAPI
from pydantic import BaseModel
from map_generator import MapGenerator

app = FastAPI()


# class Tile(BaseModel):
#     b64image: str
#     x: int
#     y: int
#     description: str


# class QueryStr(BaseModel):
#     query: str


# @app.post("/query-vector-store/")
# async def route_query_vector_store(query_str: QueryStr) -> list[Tile]:
#     return query_vector_store(query_str.query)


class MapDescription(BaseModel):
    map_description: str


map_generator = MapGenerator()


@app.post("/generate-map/")
async def route_query_vector_store(map_description: MapDescription) -> dict:
    map_created = map_generator.generate_map(map_description.map_description)

    return map_created.generate_json_map()
