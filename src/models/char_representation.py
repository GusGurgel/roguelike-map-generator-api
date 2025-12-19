from pydantic import BaseModel, Field
from typing import Optional


class CharTileRepresentation(BaseModel):
    """
    Maps a single character symbol to specific object names.
    This acts as a 'key' or 'legend', linking a character (like '@' or '#')
    to the unique names of the Tile, Entity, and Item presets.
    """

    char: str = Field(
        description="The unique character symbol used in the ASCII map grid. "
        "Note: You MUST define '@' to represent the player's starting position."
    )

    description: str = Field(
        description="A brief explanation for humans about what this character represents "
        "(e.g., 'Player on grass', 'Orc on stone floor')."
    )

    entity: Optional[str] = Field(
        default=None,
        description="The 'name' identifier of the EntityPreset to be placed here. "
        "Must match a name from the previously generated entities list. Use null if empty.",
    )

    item: Optional[str] = Field(
        default=None,
        description="The 'name' identifier of the ItemPreset to be placed here. "
        "Must match a name from the previously generated items list. Use null if empty.",
    )

    tile: Optional[str] = Field(
        description="The 'name' identifier of the TilePreset that serves as the base layer. "
        "Must match a name from the provided tile list."
    )


class CharTileRepresentationList(BaseModel):
    """
    A collection of character-to-name mappings (the Legend) used to interpret the map grid.
    """

    items: list[CharTileRepresentation] = Field(
        default_factory=list,
        description="The legend containing all character definitions used in the map layout.",
    )
