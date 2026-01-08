from pydantic import BaseModel, Field

from typing import List
from pydantic import BaseModel, Field
from .tiles import Tile, TileWithTexture


class Enemy(BaseModel):
    tile: Tile = Field(description="Tile used to represent the enemy.")

    weight: int = Field(
        gt=0,
        lt=11,
        description="The weight of the enemy. More weight, more damage, but more time to use the hit.",
    )

    weight: int = Field(
        gt=0,
        lt=11,
        description="The thread of the enemy. More thread, more damage, but more rare to find this enemy.",
    )


class EnemyList(BaseModel):
    items: List[Enemy]


class EnemyWithTexture(Enemy):
    tile_with_texture: TileWithTexture


class EnemyWithTextureList(BaseModel):
    items: List[EnemyWithTexture]
