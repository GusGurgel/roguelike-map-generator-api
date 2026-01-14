from pydantic import BaseModel, Field
from .player import PlayerWithTexture
from .levels import DungeonLevelWithTextureList
from .enemies import EnemyWithTextureList
from .weapons import WeaponWithTextureList
from .final_objective import FinalObjectiveWithTexture


class AssetBundleBase(BaseModel):
    name: str = Field(
        min_length=10,
        max_length=150,
        description="A concise, marketable title for the generated Roguelike asset pack. It should capture the essence of the theme in 2-5 words, formatted in Title Case (e.g., 'Cyberpunk Neon', 'Cursed Crypts', 'Samurai Legends').",
    )


class AssetBundle(AssetBundleBase):
    raw_description: str
    description: str
    generation_time_seconds: int

    player: PlayerWithTexture

    dungeon_levels: DungeonLevelWithTextureList

    enemies: EnemyWithTextureList

    weapons: WeaponWithTextureList

    final_objective: FinalObjectiveWithTexture

    usage_metadata: dict
