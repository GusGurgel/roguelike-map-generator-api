# fastapi dev api.py --host "::" --port 8000
from vector_db import query_vector_store
from fastapi import FastAPI
from pydantic import BaseModel
from models import AssetBundle
from asset_generator import AssetsGenerator, load_dark_souls_asset_bundle

app = FastAPI()


class MapDescription(BaseModel):
    map_description: str


@app.post("/generate-asset-bundle/")
async def generate_asset_bundle(map_description: MapDescription) -> AssetBundle:
    asset_generator = AssetsGenerator(map_description)

    return load_dark_souls_asset_bundle()
