from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

from typing import List, Literal
from pydantic import BaseModel, Field
from .tiles import Tile, TileWithTexture


class Weapon(BaseModel):
    tile: Tile = Field(description="The tile representing the weapon.")

    rarity: int = Field(
        gt=-1,
        lt=11,
        description="The item's rarity. The rarer the item, the better it is, but it is also harder to find. Need be in the range [0, 10].",
    )

    weight: int = Field(
        gt=-1,
        lt=11,
        description="The weapon's weight. Heavier weapons deal more damage but have a slower attack speed. Need be in the range [0, 10].",
    )

    mana_cost: int = Field(
        gt=-1,
        lt=11,
        description="Mana cost for ranged weapons. Higher mana cost equals higher damage. Need be in the range [1, 10] (inclusive and grater than 0).",
    )

    weapon_type: Literal["range", "melee"] = Field(
        description="Type of the weapon. 'Melee' for close combat, 'range' for distance attacks."
    )


class WeaponList(BaseModel):
    items: List[Weapon]


class WeaponWithTexture(Weapon):
    tile_with_texture: TileWithTexture


class WeaponWithTextureList(BaseModel):
    items: List[WeaponWithTexture]
