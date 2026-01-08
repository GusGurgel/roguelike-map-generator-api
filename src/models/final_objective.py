from pydantic import BaseModel, Field, ConfigDict, field_validator
from .tiles import *


class FinalObjective(BaseModel):
    tile: Tile = Field(
        description="The visual definition of the ultimate artifact located at the deepest level of the dungeon. Its name and description should imply high value, power, or mystery, distinguishing it from regular loot."
    )
    back_history: str = Field(
        description="The deep lore and narrative significance of this object within the Roguelike theme. Explain its origin, why it is sealed at the bottom of the dungeon, and the compelling motivation for the player to retrieve it and carry it back to the surface (e.g., to break a curse, save a kingdom, or settle a debt)."
    )


class FinalObjectiveWithTexture(FinalObjective):
    tile_with_texture: TileWithTexture
