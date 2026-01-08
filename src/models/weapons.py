from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

from typing import List, Literal
from pydantic import BaseModel, Field
from .tiles import Tile, TileWithTexture


class Weapon(BaseModel):
    tile: Tile = Field(description="The tile representing the weapon.")

    rarity: int = Field(
        gt=0,
        lt=11,
        description="The item's rarity. The rarer the item, the better it is, but it is also harder to find.",
    )

    weight: int = Field(
        gt=0,
        lt=11,
        description="The weapon's weight. Heavier weapons deal more damage but have a slower attack speed.",
    )

    mana_cost: int = Field(
        gt=0,
        lt=11,
        description="Mana cost for ranged weapons. Higher mana cost equals higher damage.",
    )

    weapon_type: Literal["range", "melee"] = Field(
        description="Type of the weapon. 'Melee' for close combat, 'range' for distance attacks (magic, staffs, guns, bows, etc.)."
    )


class WeaponList(BaseModel):
    items: List[Weapon]


class WeaponWithTexture(Weapon):
    tile_with_texture: TileWithTexture


class WeaponWithTextureList(BaseModel):
    items: List[WeaponWithTexture]
