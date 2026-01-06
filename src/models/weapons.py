from typing import Literal
from pydantic import BaseModel, Field, ConfigDict
from .textures import TextureDescription, Texture


class WeaponBase(BaseModel):
    """
    Base class for all weapons.
    Defines common attributes such as name, description, and rarity.
    """

    name: str = Field(..., min_length=1, description="Name of the weapon.")

    description: str = Field(..., description="Descriptive text (lore) of the weapon.")

    rarity: int = Field(
        ...,
        ge=1,
        le=10,
        description=(
            "Item rarity ranging from 1 to 10. "
            "The rarer the item, the better its stats, but the lower the drop chance."
        ),
    )


class MeleeWeaponBase(WeaponBase):
    weapon_type: Literal["melee"] = "melee"

    weight: int = Field(
        ...,
        ge=1,
        le=10,
        description=(
            "Weapon weight ranging from 1 to 10. "
            "1 = very light, 10 = extremely heavy. "
            "Heavier weapons deal more damage but have slower attack speed."
        ),
    )


class MeleeWeaponDefinition(MeleeWeaponBase):
    """
    Weapon Blueprint (Definition).
    Used to register the item type (contains the PBR texture description).
    """

    texture: TextureDescription


class MeleeWeapon(MeleeWeaponBase):
    """
    Weapon Instance in the world.
    Contains the concrete Texture positioned in the grid.
    """

    texture: Texture


class RangeWeaponBase(WeaponBase):
    """
    Base for ranged weapons.
    Adds the power mechanic.
    """

    weapon_type: Literal["range"] = "range"

    power: int = Field(
        ...,
        ge=1,
        le=10,
        description=(
            "Weapon power ranging from 1 to 10. "
            "Higher power increases damage and mana cost."
        ),
    )


class RangeWeaponDefinition(RangeWeaponBase):
    """
    Ranged Weapon Blueprint (Definition).
    """

    texture: TextureDescription


class RangeWeapon(RangeWeaponBase):
    """
    Ranged Weapon Instance in the world.
    """

    texture: Texture
