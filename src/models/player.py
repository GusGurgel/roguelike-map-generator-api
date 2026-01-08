from pydantic import BaseModel, Field, ConfigDict, field_validator
from .tiles import *


class Player(BaseModel):
    tile: Tile = Field(description="Tile used to represent the player.")
    back_history: str = Field(
        description="The back history of the player, following the current roguelike theme."
    )


class PlayerWithTexture(Player):
    tile_with_texture: TileWithTexture
