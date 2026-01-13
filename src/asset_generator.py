from typing import Type, TypeVar
from pydantic import BaseModel
from devtools import pprint
from time import sleep
from os.path import join

from langchain.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.callbacks import UsageMetadataCallbackHandler


from utils import *
from llm_models import get_model, Providers, GroqModels, GoogleModels
from models import *  # type: ignore
from vector_db import query_vector_store, StoreType, query_by_tileset_position
from db import *


T = TypeVar("T", bound=BaseModel)

save_path = join(MAIN_PATH, "saves")


class AssetsGenerator:

    def __init__(self, theme_description) -> None:
        self.model = get_model(Providers.GROQ, GroqModels.OPENAI_GPT_OSS_120B)
        self.usage_callback = UsageMetadataCallbackHandler()

        # O prompt agora atua como um "Lead Game Designer" criando a documentação base.
        response = self.model.invoke(
            [
                HumanMessage(
                    f"""
Act as a Lead Game Designer and World Builder.
You are tasked with expanding a basic concept into a rich Roguelike Game Setting.

Input Concept: "{theme_description}"

**IMPORTANT LANGUAGE CONSTRAINT:**
Regardless of the language used in the "Input Concept", **you must write the expanded description entirely in English.**

Your goal is to write a cohesive "World Description" that will serve as the source of truth for generating assets later.
Please define:
1. **The Setting Name**: Give this world or dungeon a unique name.
2. **Visual Style & Atmosphere**: Describe the art direction (e.g., Gritty Industrial, Neon-Cyberpunk, Gothic Horror) and the mood (lighting, weather, ambient noise).
3. **The Lore**: Briefly explain the history. Why is this place dangerous? What happened here?
4. **The Core Conflict**: What is the corruption, curse, or enemy force controlling this place?

Do not list specific item stats yet. Focus on the narrative and sensory details to guide future generation.
"""
                )
            ],
            config={"callbacks": [self.usage_callback]},
        )

        self.raw_theme_description = theme_description
        self.theme_description: str = str(response.content)

    def _get_structured_model(self, schema_class: Type[T]):
        return self.model.with_structured_output(
            schema=schema_class.model_json_schema(), method="json_schema"
        )

    def _ask_llm_structured(self, schema_class: Type[T], messages: list) -> T:
        structured_llm = self._get_structured_model(schema_class)
        result = structured_llm.invoke(
            messages,
            config={"callbacks": [self.usage_callback]},
        )
        return schema_class.model_validate(result)

    def generate_player(self) -> Player:
        return self._ask_llm_structured(
            Player,
            [
                HumanMessage(
                    f"""
Act as a Narrative Designer and RPG System Creator.
Based on the rich world description below:
"{self.theme_description}"

Create the Main Protagonist (The Player Character) for this Roguelike.
Guidelines:
1. **Archetype**: Define a starting class/role that fits the setting (e.g., A Disgraced Knight, A Glitchy Android, A Cursed Cultist).
2. **Backstory & Motivation**: Why is this character entering this dangerous place? (Redemption, Greed, Revenge, Survival?).
3. **Visuals**: Describe their appearance, starting gear look, and distinct physical traits matching the visual style of the theme.

Generate the Player profile now.
"""
                )
            ],
        )

    def generate_final_objective(self) -> FinalObjective:
        return self._ask_llm_structured(
            FinalObjective,
            [
                HumanMessage(
                    f"""
Act as a Lead Narrative Designer and Lore Architect.
Context: We are designing the climax of a Roguelike game based on this world setting:
"{self.theme_description}"

Your task is to design the **Final Objective** (The "MacGuffin").
This is the ultimate item located at the very bottom of the dungeon (Depth 6) that the player must retrieve and physically carry back to the entrance to win.

Guidelines:
1. **The "Amulet of Yendor" Factor**: The object must be tangible and portable (e.g., an artifact, a sacred scroll, a severed head, a crystallized soul). It cannot be a location or a giant structure.
2. **High Stakes Lore**: In the `back_history`, connect this object directly to the "Core Conflict" of the theme. Is it the source of the dungeon's corruption? The only cure for a plague? The key to a sealed god?
3. **Visual Distinction**: The `tile` description should sound legendary. It should visually stand out from regular loot.
4. **Motivation**: Clearly state why leaving it down there is not an option.

Generate the legendary Final Objective now.
"""
                )
            ],
        )

    def generate_dungeon_levels(self) -> DungeonLevelList:
        return self._ask_llm_structured(
            DungeonLevelList,
            [
                HumanMessage(
                    f"""
Act as an expert Roguelike Level Designer. 
Your task is to generate a progression of 6 dungeon levels based on the following theme:
"{self.theme_description}"

Guidelines for generation:
1. **Progression**: The levels must evolve. Depth 1 should be the entrance/surface (easier), while Depth 6 is the core/deepest part (most dangerous).
2. **Atmosphere**: For each level, describe the environment, lighting, smells, and ambient sounds.
3. **Cohesion**: Ensure the transition between levels makes logical sense within the theme.
4. **Variety**: Avoid repeating the exact same biome descriptions.

Generate the 6 levels now.
"""
                )
            ],
        )

    def generate_weapons(self) -> WeaponList:
        return self._ask_llm_structured(
            WeaponList,
            [
                HumanMessage(
                    f"""
Act as a Creative Director for a Roguelike game.
Based on the theme specification: "{self.theme_description}"

Generate 30 unique weapons. 
Guidelines:
1. **Thematic Fit**: All weapons must strictly fit the technology/magic level and tone of the theme.
2. **Diversity**: Include a broad mix of types:
   - Melee (Daggers, Swords, Hammers, Polearms).
   - Ranged (Bows, Guns, Crossbows, Thrown).
   - Magic/Tech (Staffs, Wands, Experimental Devices).
3. **Rarity Spread (Balanced Economy)**:
   - **15 Common weapons**: Rusty, improvised, or basic standard issue gear.
   - **10 Rare weapons**: Specialized, high quality, superior craftsmanship, or enchanted.
   - **5 Legendary weapons**: Artifacts, experimental prototypes, or named weapons with lore and unique properties.
4. **Descriptions**: Provide vivid descriptions focusing on the weapon's appearance and the specific "feeling" of wielding it.

Generate the list of 30 weapons now.
"""
                )
            ],
        )

    def generate_enemies(self) -> EnemyList:
        return self._ask_llm_structured(
            EnemyList,
            [
                HumanMessage(
                    f"""
Act as a Gameplay Balance Designer.
Using the theme: "{self.theme_description}"

Generate a Bestiary of 30 enemies distributed across the dungeon depths.
Guidelines:
1. **Archetypes**: Ensure a mix of:
   - *Fodder*: Weak, come in groups.
   - *Tanks*: Slow, high health.
   - *Ranged/Casters*: Attack from afar, low health.
   - *Elites*: Dangerous variations with unique traits.
2. **Progression**: 
   - Enemies for Depths 1-2 should be simpler/beasts.
   - Enemies for Depths 5-6 should be complex/horrors/highly equipped units.
3. **Visuals**: Describe their appearance to match the gloomy/adventurous tone of the theme.
4. **Behavior**: Briefly hint at how they attack (e.g., "Ambushes from shadows", "Charges blindly").

Generate the 30 enemies now.
"""
                )
            ],
        )

    def generate_asset_bundle(self) -> AssetBundle:
        asset_buddle_base = self._ask_llm_structured(
            AssetBundleBase,
            [
                HumanMessage(
                    f"""
Act as a Creative Director and Marketing Lead for a Game Studio.
Analyze the rich world description provided below:
"{self.theme_description}"

Your task is to craft the perfect Title (Name) for this Roguelike Asset Bundle.

Guidelines:
1. **Impact**: The name must be catchy, evocative, and marketable (e.g., "Echoes of the Void", "Neon Chrome", "The Iron Oath").
2. **Relevance**: It should capture the core mood, setting, or conflict of the theme.
3. **Format**: Use Title Case. Keep it concise (2 to 6 words). Avoid generic names like "Dungeon Pack 1".

Generate the title now.
"""
                )
            ],
        )

        player = self.generate_player()
        dungeon_levels = self.generate_dungeon_levels()
        enemies = self.generate_enemies()
        weapons = self.generate_weapons()
        final_objective = self.generate_final_objective()

        player_with_texture = PlayerWithTexture(
            **player.model_dump(),
            tile_with_texture=AssetsGenerator.convert_tile_to_tile_with_texture(
                player.tile, "entities"
            ),
        )

        final_objective_with_texture = FinalObjectiveWithTexture(
            **final_objective.model_dump(),
            tile_with_texture=AssetsGenerator.convert_tile_to_tile_with_texture(
                final_objective.tile, "items"
            ),
        )

        dungeon_levels_with_texture_items: List[DungeonLevelWithTexture] = []
        for dungeon_level in dungeon_levels.items:
            dungeon_levels_with_texture_items.append(
                DungeonLevelWithTexture(
                    **dungeon_level.model_dump(),
                    wall_tile_with_texture=AssetsGenerator.convert_tile_to_tile_with_texture(
                        dungeon_level.wall_tile, "environments"
                    ),
                    floor_tile_with_texture=AssetsGenerator.convert_tile_to_tile_with_texture(
                        dungeon_level.floor_tile, "environments"
                    ),
                )
            )
        dungeon_levels_with_texture = DungeonLevelWithTextureList(
            items=dungeon_levels_with_texture_items
        )

        enemies_with_texture_items: List[EnemyWithTexture] = []
        for enemy in enemies.items:
            enemies_with_texture_items.append(
                EnemyWithTexture(
                    **enemy.model_dump(),
                    tile_with_texture=AssetsGenerator.convert_tile_to_tile_with_texture(
                        enemy.tile, "entities"
                    ),
                )
            )
        enemies_with_texture = EnemyWithTextureList(items=enemies_with_texture_items)

        weapons_with_texture_items: List[WeaponWithTexture] = []
        for weapon in weapons.items:
            weapons_with_texture_items.append(
                WeaponWithTexture(
                    **weapon.model_dump(),
                    tile_with_texture=AssetsGenerator.convert_tile_to_tile_with_texture(
                        weapon.tile, "items"
                    ),
                )
            )
        weapons_with_texture = WeaponWithTextureList(items=weapons_with_texture_items)

        return AssetBundle(
            **asset_buddle_base.model_dump(),
            raw_description=self.raw_theme_description,
            description=self.theme_description,
            player=player_with_texture,
            dungeon_levels=dungeon_levels_with_texture,
            enemies=enemies_with_texture,
            weapons=weapons_with_texture,
            final_objective=final_objective_with_texture,
            usage_metadata=self.usage_callback.usage_metadata,
        )

    @staticmethod
    def convert_tile_to_tile_with_texture(
        tile: Tile, store_type: StoreType
    ) -> TileWithTexture:
        texture_from_rag = query_vector_store(tile.description, store_type, 1)[0]

        position = Position(x=texture_from_rag["x"], y=texture_from_rag["y"])

        texture = Texture(
            tileset_position=position,
            tileset_description=texture_from_rag["description"],
        )

        return TileWithTexture(**tile.model_dump(), texture=texture)


def load_zombie_souls_asset_bundle() -> AssetBundle:
    return load_object_json(
        join(MAIN_PATH, "saves/", "zombie_asset_bundle.json"), AssetBundle
    )


map_description = """
Create a roguelike with the theme as zombie pos apocalyptic world.
"""

if __name__ == "__main__":
    id = find_all_assets_bundles()[0]["id"]

    asset_buddle = find_bundle_data_by_id(id)

    if asset_buddle != None:
        print(asset_buddle.final_objective)

    # asset_generator = AssetsGenerator(map_description)

    # asset_buddle: AssetBundle = load_zombie_souls_asset_bundle()

    # save_object_json(
    #     asset_buddle, join(MAIN_PATH, "saves/", "zombie_asset_bundle.json")
    # )
    # pprint(asset_buddle.usage_metadata)
    # id = insert_asset_bundle(
    #     asset_buddle.name,
    #     asset_buddle.description,
    #     GroqModels.OPENAI_GPT_OSS_120B,
    #     asset_buddle,
    # )

    # print(id)

    # save_object(asset_buddle, join(MAIN_PATH, "saves/", "zombie_asset_bundle.pk"))

    # pprint(asset_buddle.final_objective.model_dump())
