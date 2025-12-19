from typing import Type, TypeVar
from pydantic import BaseModel
from langchain.messages import SystemMessage, HumanMessage, AIMessage
from devtools import pprint
from time import sleep
from os.path import join


from utils import MAIN_PATH, save_object, load_object
from llm_models import get_model, Providers, GroqModels, GoogleModels
from models.textures import TextureDescriptionList
from models.tiles import TilePresetList
from models.entities import EntitiesPresetList
from models.items import ItemPresetList
from models.char_representation import CharTileRepresentationList
from models.map import Map
from models.map_char_representation import MapCharRepresentation
from prompts import (
    get_texture_description_list_tips,
    get_tile_preset_list_tips,
    get_entities_list_tips,
    get_items_list_tips,
    get_char_tile_representation_tips,
    get_map_grid_tips,
)

import json

T = TypeVar("T", bound=BaseModel)

save_path = join(MAIN_PATH, "saves")


class MapGenerator:
    def __init__(self) -> None:
        # self.model = get_model(Providers.GROQ, GroqModels.OPENAI_GPT_OSS_120B)
        self.model = get_model(Providers.GOOGLE, GoogleModels.GEMINI_2_5_FLASH)

    def _get_structured_model(self, schema_class: Type[T]):
        return self.model.with_structured_output(
            schema=schema_class.model_json_schema(), method="json_schema"
        )

    def _ask_llm(self, schema_class: Type[T], messages: list) -> T:
        structured_llm = self._get_structured_model(schema_class)
        result = structured_llm.invoke(messages)
        return schema_class.model_validate(result)

    def get_texture_description_list(
        self, map_description: str
    ) -> TextureDescriptionList:
        return self._ask_llm(
            TextureDescriptionList,
            [
                SystemMessage(content=get_texture_description_list_tips),
                HumanMessage(content=map_description),
            ],
        )

    def get_tile_preset_list(
        self, texture_list: TextureDescriptionList, map_description: str
    ) -> TilePresetList:
        return self._ask_llm(
            TilePresetList,
            [
                SystemMessage(content=get_tile_preset_list_tips),
                AIMessage(
                    content=f"Textures generated: {texture_list.model_dump_json()}"
                ),
                HumanMessage(
                    content=f"Now, create tile presets for: {map_description}"
                ),
            ],
        )

    def get_entities_list(
        self, tile_list: TilePresetList, map_description: str
    ) -> EntitiesPresetList:
        available_ids = [t.name for t in tile_list.entities_tile_presets]

        return self._ask_llm(
            EntitiesPresetList,
            [
                SystemMessage(content=get_entities_list_tips),
                SystemMessage(content=f"Available tile_preset IDs: {available_ids}"),
                HumanMessage(content=map_description),
            ],
        )

    def get_items_list(
        self, tile_list: TilePresetList, map_description: str
    ) -> ItemPresetList:
        available_ids = [t.name for t in tile_list.items_tile_presets]

        return self._ask_llm(
            ItemPresetList,
            [
                SystemMessage(content=get_items_list_tips),
                SystemMessage(content=f"Available tile_preset IDs: {available_ids}"),
                HumanMessage(content=map_description),
            ],
        )

    def get_char_tile_representation(
        self,
        tile_list: TilePresetList,
        entity_list: EntitiesPresetList,
        item_list: ItemPresetList,
        map_description: str,
    ) -> CharTileRepresentationList:
        # Extract available IDs for context
        available_tiles = [t.name for t in tile_list.environment_tile_presets]
        available_entities = [e.name for e in entity_list.items]
        available_items = [i.name for i in item_list.items]

        return self._ask_llm(
            CharTileRepresentationList,
            [
                SystemMessage(content=get_char_tile_representation_tips),
                SystemMessage(
                    content=(
                        f"Available tile environment IDs: {available_tiles}\n"
                        f"Available entity IDs: {available_entities}\n"
                        f"Available item IDs: {available_items}"
                    )
                ),
                HumanMessage(
                    content=f"Create a character legend for this map theme: {map_description}"
                ),
            ],
        )

    def get_map_char_representation(
        self,
        representation_list: CharTileRepresentationList,
        map_description: str,
    ) -> MapCharRepresentation:
        # Extract only the characters that the LLM is allowed to use in the grid
        valid_chars = [item for item in representation_list.items]

        return self._ask_llm(
            MapCharRepresentation,
            [
                SystemMessage(content=get_map_grid_tips),
                SystemMessage(
                    content=f"VALID CHARACTERS TO USE: {valid_chars}\n"
                    f"Note: '@' is the player and MUST be placed."
                ),
                HumanMessage(
                    content=f"Draw the 2D map grid for this theme: {map_description}"
                ),
            ],
        )

    def generate_map(self, map_description: str) -> Map:
        print("--- Generating Textures ---")
        textures = self.get_texture_description_list(map_description)
        pprint(textures)

        print("\n--- Generating Tile Presets ---")
        tiles = self.get_tile_preset_list(textures, map_description)
        pprint(tiles)

        print("\n--- Generating Entities ---")
        sleep(5)
        entities = self.get_entities_list(tiles, map_description)
        pprint(entities)

        print("\n--- Generating Items ---")
        sleep(5)
        items = self.get_items_list(tiles, map_description)
        pprint(items)

        print("\n--- Generating CharTileRepresentations ---")
        sleep(5)
        char_tile_representation_list = self.get_char_tile_representation(
            tiles, entities, items, map_description
        )
        pprint(char_tile_representation_list)

        print("\n--- Generating MapCharRepresentation ---")
        sleep(5)
        map_char_representation = self.get_map_char_representation(
            char_tile_representation_list, map_description
        )
        pprint(map_char_representation)

        # save_object(textures, join(save_path, "textures.pk"))
        # save_object(tiles, join(save_path, "tiles.pk"))
        # save_object(entities, join(save_path, "entities.pk"))
        # save_object(items, join(save_path, "items.pk"))
        # save_object(
        #     char_tile_representation_list,
        #     join(save_path, "char_tile_representation_list.pk"),
        # )
        # save_object(
        #     map_char_representation,
        #     join(save_path, "map_char_representation.pk"),
        # )

        return Map(
            textures,
            tiles,
            entities,
            items,
            char_tile_representation_list,
            map_char_representation,
        )


# Execução
# if __name__ == "__main__":
# map_desc = "A square room with a sword in the middle and 3 orcs. The room is covered in a grass floor and is surrounded by wooden walls."
# generator = MapGenerator()
# roguelike_map = generator.generate_map(map_desc)

# textures: TextureDescriptionList = load_object(
#     join(save_path, "textures.pk"), TextureDescriptionList
# )
# tiles: TilePresetList = load_object(join(save_path, "tiles.pk"), TilePresetList)
# entities: EntitiesPresetList = load_object(
#     join(save_path, "entities.pk"), EntitiesPresetList
# )
# items: ItemPresetList = load_object(join(save_path, "items.pk"), ItemPresetList)
# char_tile_representation_list: CharTileRepresentationList = load_object(
#     join(save_path, "char_tile_representation_list.pk"), CharTileRepresentationList
# )
# map_char_representation: MapCharRepresentation = load_object(
#     join(save_path, "map_char_representation.pk"), MapCharRepresentation
# )

# roguelike_map = Map(
#     textures,
#     tiles,
#     entities,
#     items,
#     char_tile_representation_list,
#     map_char_representation,
# )

# with open(join(MAIN_PATH, "map.json"), "w") as file:
#     file.write(json.dumps(roguelike_map.generate_json_map()))
