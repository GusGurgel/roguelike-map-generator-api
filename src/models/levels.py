from typing import List
from pydantic import BaseModel, Field
from .tiles import Tile, TileWithTexture


class DungeonLevel(BaseModel):
    description: str = Field(
        description="A basic description of the level.",
    )

    name: str = Field(
        description="The name of level in title case (ex: The Crypts, The Red Desert, Forest of The Fallen Giants).",
    )

    depth: int = Field(
        gt=0,
        lt=20,
        description="The dungeon level depth. The deeper the level, the harder it is.",
    )

    wall_tile: Tile = Field(
        description="The tile used to represent the dungeon walls.",
    )

    floor_tile: Tile = Field(
        description="The tile used to represent the dungeon floor.",
    )


class DungeonLevelList(BaseModel):
    items: List[DungeonLevel]


class DungeonLevelWithTexture(DungeonLevel):
    wall_tile_with_texture: TileWithTexture
    floor_tile_with_texture: TileWithTexture


class DungeonLevelWithTextureList(BaseModel):
    items: List[DungeonLevelWithTexture]
