from typing import List
from pydantic import BaseModel, Field
from .textures import TextureDescription, Texture

# --- New Model ---


class DungeonLevelNames(BaseModel):
    """
    A collection of thematic names for dungeon levels.
    """

    names: List[str] = Field(
        ...,
        description="A list of distinct and evocative names for the dungeon levels.",
        min_length=1,
        max_length=30,
        examples=[["The Whispering Geode", "Fungal Hollows", "Crystalline Abyss"]],
    )


class DungeonLevelBase(BaseModel):
    name: str = Field(
        ...,
        description="The display name of the level (e.g., 'The Whispering Catacombs').",
        min_length=3,
        max_length=100,
    )

    description: str = Field(
        ...,
        description="Narrative description of the level's environment and atmosphere.",
        min_length=10,
        max_length=1000,
    )

    depth: int = Field(
        ...,
        description="The depth of the level. Must be a positive integer (greater than zero).",
        gt=0,  # 'gt' stands for Greater Than
        examples=[1, 5, 100],
    )


class DungeonLevelDescriptions(DungeonLevelBase):
    """
    Represents a specific level within the dungeon, defining its atmosphere
    through visual descriptions and texturing.
    """

    wall_texture: TextureDescription = Field(
        ..., description="The texture definition used for the walls of this level."
    )

    floor_texture: TextureDescription = Field(
        ..., description="The texture definition used for the floors of this level."
    )


class DungeonLevel(DungeonLevelBase):
    wall_texture: Texture
    floor_texture: Texture
