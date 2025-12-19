from pydantic import BaseModel, Field


class MapCharRepresentation(BaseModel):
    """
    The final 2D spatial layout of the map.
    This class holds the ASCII-style grid that defines where every object is placed.
    """

    representation: list[str] = Field(
        description="A matrix of strings representing the 2D map. Each string is a row, "
        "and each character in the string must match a 'char' defined in "
        "the CharTileRepresentationList. Use a space ' ' for empty or null areas."
    )
