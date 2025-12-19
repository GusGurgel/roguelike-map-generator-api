from pydantic import BaseModel, Field


class TilePreset(BaseModel):
    """
    Represents a game tile configuration, linking physical properties to a texture.
    """

    name: str = Field(
        description="Unique identifier for the tile preset in snake_case (e.g., 'stone_wall', 'water_deep').",
    )

    has_collision: bool = Field(
        description="True if the player or NPCs cannot walk through this tile (e.g., walls, large rocks)."
    )

    is_transparent: bool = Field(
        description="True if the tile does not block the line of sight (e.g., glass, low grass, floor)."
    )

    texture_id: str = Field(
        description="The snake_case name of the texture that should be applied to this tile."
    )


class TilePresetList(BaseModel):
    """
    A collection of tile configurations for a game map, categorized by their
    role in the game engine (Player, Entities, or Environment).
    """

    player_tile_preset: TilePreset = Field(
        description="The specific configuration for the player character."
    )

    entities_tile_presets: list[TilePreset] = Field(
        description="A list of presets for dynamic non-player characters (NPCs) or enemies (e.g., Orcs, Goblins, Guards)."
    )

    environment_tile_presets: list[TilePreset] = Field(
        description="A list of presets for the static world architecture (e.g., Floors, Walls, Ceilings, Fixed Obstacles)."
    )

    items_tile_presets: list[TilePreset] = Field(
        description="A list of presets for interactive or pickable objects (e.g., Swords on the floor, Chests, Keys, Potions)."
    )
