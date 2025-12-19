from pydantic import BaseModel, Field
from typing import Literal


class EntityPreset(BaseModel):
    """
    Represents a blueprint or template for a dynamic entity.
    This definition is used to spawn one or multiple instances of the same entity type.
    """

    name: str = Field(
        description="Unique identifier for this preset type (e.g., 'skeleton_warrior'). "
        "This ID is used to reference this specific type of entity."
    )

    tile_preset: str = Field(
        description="Must match the 'name' of a TilePreset in the entities_tile_presets list "
        "to define the visual appearance.",
    )

    threat: int = Field(
        ge=1,
        le=10,
        description="The power level/difficulty of this entity type from 1 to 10.",
    )

    entity_type: Literal["enemy"] = Field(
        default="enemy",
        description="The category of the entity. Currently supports 'enemy'.",
    )

    description: str = Field(description="Description of the entity.")


class EntitiesPresetList(BaseModel):
    """
    A collection of unique entity blueprints available for the map.
    Each item in this list should represent a unique TYPE of entity, not an individual instance.
    """

    items: list[EntityPreset] = Field(
        default_factory=list,
        description="List of unique entity templates available to be placed on the map.",
    )
