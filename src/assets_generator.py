from typing import Type, TypeVar
from pydantic import BaseModel
from langchain.messages import SystemMessage, HumanMessage, AIMessage
from devtools import pprint
from time import sleep
from os.path import join


from utils import MAIN_PATH, save_object, load_object
from llm_models import get_model, Providers, GroqModels, GoogleModels
from models.dungeon import DungeonLevelDescriptions, DungeonLevelNames, DungeonLevel
from models.textures import TexturePosition, TextureDescription, Texture
from vector_db import query_vector_store, StoreType, query_by_tileset_position
from prompts import (
    get_map_description_prompt,
    get_dungeon_level_names_prompt,
    get_level_by_dungeon_depth_and_name_prompt,
    get_texture_with_llm_prompt,
)

T = TypeVar("T", bound=BaseModel)

save_path = join(MAIN_PATH, "saves")

map_description = """
Atmosphere & Lighting
The visual atmosphere is defined by a sense of ancient decay and oppressive
darkness, utilizing a muted, desaturated color palette dominated by deep greys,
muddy browns, and cold, pale blues. Lighting plays a crucial role, relying on
high-contrast chiaroscuro techniques where the player is often surrounded by
encroaching shadows, illuminated only by the flickering, warm orange glow of
bonfires or torches. The environment should feel heavy and melancholic, with
volumetric fog and floating dust particles emphasizing the stagnation of a dying
world.

Architecture & Environment
Architectural assets must reflect a ruined Gothic grandeur, featuring towering
cathedrals, crumbling castle battlements, and claustrophobic dungeon corridors.
The structures should appear colossal but dilapidated, covered in thick ivy,
moss, and centuries of grime to convey extreme age. For a roguelike generation,
tilesets need to blend seamlessly between distinct biomes—from poisonous,
rotting swamps to jagged, snowy peaks—incorporating environmental storytelling
elements like scattered debris, broken statues, and skeletal remains embedded in
the scenery.

Character & Equipment Design
Character and equipment designs prioritize realism and weathering over
high-fantasy polish. Armor sets should look functional yet worn, featuring
dented plate metal, rusted chainmail, and tattered cloth simulations that react
to movement. The aesthetic is grounded and gritty; weapons are heavy, chipped,
and stained, lacking oversized or cartoonish proportions. The protagonist and
NPCs often remain faceless or obscured by helmets and cowls, reinforcing themes
of anonymity and the loss of humanity in a harsh, unforgiving cycle.

Enemies & Monstrosities
Enemy designs lean heavily into grotesque body horror and tragic lore, mixing
standard undead tropes with twisted, surreal anatomy. Creatures should evoke a
sense of pity and terror, ranging from hollowed soldiers dragging heavy swords
to colossal abominations made of visceral limbs and dark magic. The texturing
should emphasize organic decay—rotting flesh, exposed bone, and mutated
growth—while boss assets should be imposing and distinct, often characterized by
distorted religious imagery or corrupted knightly elegance.
"""


class AssetsGenerator:
    def __init__(self, map_description) -> None:
        self.model = get_model(Providers.GROQ, GroqModels.OPENAI_GPT_OSS_120B)
        self.map_description = map_description

    def _get_structured_model(self, schema_class: Type[T]):
        return self.model.with_structured_output(
            schema=schema_class.model_json_schema(), method="json_schema"
        )

    def _ask_llm_structured(self, schema_class: Type[T], messages: list) -> T:
        structured_llm = self._get_structured_model(schema_class)
        result = structured_llm.invoke(messages)
        return schema_class.model_validate(result)

    def generate_dungeon_level_names(self, n_levels: int) -> DungeonLevelNames:
        return self._ask_llm_structured(
            DungeonLevelNames,
            [
                SystemMessage(content=get_dungeon_level_names_prompt(n_levels)),
                HumanMessage(content=get_map_description_prompt(self.map_description)),
            ],
        )

    def generate_level_by_dungeon_depth_and_name(
        self, level_name: str, depth: int
    ) -> DungeonLevel:
        dungeon_level_descriptions: DungeonLevelDescriptions = self._ask_llm_structured(
            DungeonLevelDescriptions,
            [
                SystemMessage(
                    content=get_level_by_dungeon_depth_and_name_prompt(
                        level_name, depth
                    )
                ),
                HumanMessage(content=map_description),
            ],
        )

        return DungeonLevel(
            name=dungeon_level_descriptions.name,
            description=dungeon_level_descriptions.description,
            wall_texture=self.generate_texture_without_llm(
                dungeon_level_descriptions.wall_texture, "environments"
            ),
            floor_texture=self.generate_texture_without_llm(
                dungeon_level_descriptions.floor_texture, "environments"
            ),
            depth=depth,
        )

    def generate_texture_with_llm(
        self, texture_description: TextureDescription, store_type: StoreType
    ) -> Texture:
        texture_position: TexturePosition = self._ask_llm_structured(
            TexturePosition,
            [
                SystemMessage(
                    content=(
                        get_texture_with_llm_prompt(
                            query_vector_store(
                                texture_description.description, store_type, 6
                            ),
                            texture_description.name,
                            texture_description.description,
                        )
                    )
                )
            ],
        )

        description_rag = ""
        texture_rag = query_by_tileset_position(texture_position.x, texture_position.y)
        if len(texture_rag) > 0:
            description_rag = texture_rag[0]["description"]

        return Texture(
            color=texture_description.color,
            position=texture_position,
            name=texture_description.name,
            description=texture_description.description,
            description_rag=description_rag,
        )

    def generate_texture_without_llm(
        self, texture_description: TextureDescription, store_type: StoreType
    ) -> Texture:
        texture = query_vector_store(texture_description.description, store_type, 1)[0]

        return Texture(
            color=texture_description.color,
            position=TexturePosition(x=texture["x"], y=texture["y"]),
            name=texture_description.name,
            description=texture_description.description,
            description_rag=texture["description"],
        )


if __name__ == "__main__":
    assets_generator = AssetsGenerator(map_description)

    dungeon_level_names: DungeonLevelNames = (
        assets_generator.generate_dungeon_level_names(2)
    )

    level: DungeonLevel = assets_generator.generate_level_by_dungeon_depth_and_name(
        dungeon_level_names.names[0], 1
    )

    pprint(level.wall_texture.model_dump())
    pprint(level.floor_texture.model_dump())

    # color_wall = level.wall_texture.color
    # name_wall = level.wall_texture.name
    # description_wall = level.wall_texture.description
    # wall_texture = assets_generator.generate_texture_without_llm(
    #     name_wall, description_wall, color_wall, "environments"
    # )

    # pprint(wall_texture.model_dump())
