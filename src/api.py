# fastapi dev api.py --host "::" --port 8000
from vector_db import query_vector_store
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from models import AssetBundle
from asset_generator import AssetsGenerator
from db import (
    find_all_assets_bundles,
    find_bundle_data_by_id,
    delete_asset_bundle_by_id,
    insert_asset_bundle,
)
from typing import Any, Dict
from config import model_key
from fastapi.staticfiles import StaticFiles
from os.path import join
from utils import MAIN_PATH
import logging

logger = logging.getLogger(__name__)

# Configure basic logging to the console (StreamHandler is default)
logging.basicConfig(
    level=logging.INFO,  # Set the desired log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ],  # Explicitly use StreamHandler for console output
)

app = FastAPI()

# Mount the "static" directory to the "/static" URL path
app.mount(
    "/viewer",
    StaticFiles(directory=join(MAIN_PATH, "public/", "viewer/")),
    name="viewer",
)


class MapDescription(BaseModel):
    map_description: str


@app.post("/asset-bundle/")
async def route_post_asset_bundle(map_description: MapDescription) -> AssetBundle:
    try:
        asset_generator: AssetsGenerator = AssetsGenerator(
            map_description.map_description
        )
        asset_bundle: AssetBundle = asset_generator.generate_asset_bundle()

        insert_asset_bundle(
            asset_bundle,
            model_key,
        )
        return asset_bundle
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error.")


@app.get("/asset-bundle/")
async def route_find_all_asset_bundle() -> list[Dict[str, Any]]:
    return find_all_assets_bundles()


@app.get("/asset-bundle/{id}")
async def route_find_bundle_data_id(id: int) -> AssetBundle:
    asset_bundle = find_bundle_data_by_id(id)

    if asset_bundle == None:
        raise HTTPException(
            status_code=404, detail=f"Asset bundle with id {id} no found."
        )

    return asset_bundle


@app.get("/raw/asset-bundle/{id}")
async def route_find_raw_bundle_data_id(id: int) -> dict:
    asset_bundle = find_bundle_data_by_id(id)

    if asset_bundle == None:
        raise HTTPException(
            status_code=404, detail=f"Asset bundle with id {id} no found."
        )

    json = asset_bundle.model_dump()
    del json["name"]
    del json["description"]
    del json["raw_description"]
    del json["usage_metadata"]
    del json["generation_time_seconds"]

    return json


@app.delete("/asset-bundle/{id}")
async def route_delete_bundle_data_id(id: int):
    was_delete = delete_asset_bundle_by_id(id)

    if not was_delete:
        return HTTPException(
            status_code=404, detail=f"Asset bundle with id {id} no found."
        )
    else:
        return Response(content=f"Asset bundle with id {id} was deleted.")


logger.info("Access bundle viewer on http://localhost:8000/viewer/index.html")
