from pydantic import BaseModel, Field
from typing import Literal


class ItemPreset(BaseModel):
    """
    Represents a blueprint or template for an item.
    This definition defines the properties and visuals for a specific type of item
    (e.g., 'Health Potion') that can appear multiple times in the game world.
    """

    name: str = Field(
        description="Unique ID for this item type (e.g., 'iron_sword', 'minor_healing_potion')."
    )

    tile_preset_id: str = Field(
        alias="tile_preset",
        description="Must match the 'name' of a TilePreset in the items_tile_presets list "
        "to define how the item looks on the ground or in the inventory.",
    )

    item_type: Literal["healing_potion", "melee_weapon"] = Field(
        description="The functional category of the item, which determines its behavior and usage."
    )

    item_rarity: int = Field(
        ge=1,
        le=10,
        description="The rarity level of the item from 1 to 10. "
        "1 represents common items, while 10 represents unique or legendary items.",
    )

    description: str = Field(description="Description of the item.")


class ItemPresetList(BaseModel):
    """
    A collection of unique item blueprints available for the current map or level.
    This list acts as a library of items that can be instantiated.
    """

    items: list[ItemPreset] = Field(
        default_factory=list,
        description="List of unique item templates. Do not create multiple entries for "
        "the same item type; one preset is enough to spawn many instances.",
    )
