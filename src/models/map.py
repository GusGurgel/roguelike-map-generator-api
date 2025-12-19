from .tiles import TilePresetList
from .entities import EntitiesPresetList
from .items import ItemPresetList
from .char_representation import CharTileRepresentationList
from .textures import TextureDescriptionList
from .map_char_representation import MapCharRepresentation

from devtools import pprint

from vector_db import query_vector_store


class Map:
    def __init__(
        self,
        textures: TextureDescriptionList,
        tiles_preset_list: TilePresetList,
        entities_preset_list: EntitiesPresetList,
        items_preset_list: ItemPresetList,
        char_representation: CharTileRepresentationList,
        map_char_representation: MapCharRepresentation,
    ) -> None:
        self.textures: TextureDescriptionList = textures
        self.tiles_preset_list: TilePresetList = tiles_preset_list
        self.entities_preset_list: EntitiesPresetList = entities_preset_list
        self.items_preset_list: ItemPresetList = items_preset_list
        self.char_representation: CharTileRepresentationList = char_representation
        self.map_char_representation = map_char_representation

        self.texture_dict = {}
        self.generate_texture_dict()

        self.preset_tile_dict = {}
        self.generate_preset_tile_dict()

        self.preset_entities_dict = {}
        self.generate_preset_entities()

        self.preset_items_dict = {}
        self.generate_preset_items()

        self.char_representation_dict = {}
        self.generate_char_representation_dict()

        pprint(self.char_representation_dict)
        pprint(self.map_char_representation.representation)

    def generate_char_representation_dict(self) -> None:
        for char_representation in self.char_representation.items:
            char_representation_converted = {}
            if char_representation.entity != None:
                char_representation_converted["entity"] = self.preset_entities_dict[
                    char_representation.entity
                ]

            if char_representation.item != None:
                char_representation_converted["item"] = self.preset_items_dict[
                    char_representation.item
                ]

            if char_representation.tile != None:
                char_representation_converted["tile"] = self.preset_tile_dict[
                    char_representation.tile
                ]

            self.char_representation_dict[char_representation.char] = (
                char_representation_converted
            )

    def generate_preset_items(self) -> None:
        for item in self.items_preset_list.items:
            self.preset_items_dict[item.name] = {
                "tile": self.preset_tile_dict[item.tile_preset_id],
                "type": item.item_type,
                "description": item.description,
                # ---
                "health_increase": 10,
                "damage": 20,
            }

    def generate_preset_entities(self) -> None:
        for entity in self.entities_preset_list.items:
            self.preset_entities_dict[entity.name] = {
                "type": entity.entity_type,
                "entity_name": entity.name,
                "tile": self.preset_tile_dict[entity.tile_preset],
                # ---
                "turns_to_move": 1,
                "max_health": 30,
                "health": 50,
                "max_mana": 3,
                "mana": 3,
                "base_damage": 5,
            }

    def generate_preset_tile_dict(self) -> None:
        for tile in [
            *self.tiles_preset_list.entities_tile_presets,
            *self.tiles_preset_list.environment_tile_presets,
            *self.tiles_preset_list.items_tile_presets,
        ]:
            self.preset_tile_dict[tile.name] = {
                "texture": tile.texture_id,
                "color": self.texture_dict[tile.texture_id]["color"],
                "has_collision": tile.has_collision,
                "is_transparent": tile.is_transparent,
            }

    def generate_texture_dict(self) -> None:
        for texture in self.textures.items:
            query_result = query_vector_store(texture.description, 1)
            if len(query_result) > 0:
                result = query_result[0]
                self.texture_dict[texture.name] = {
                    "x": result["x"],
                    "y": result["y"],
                    "color": texture.color,
                    "description_from_texture": texture.description,
                    "description_from_vector_store": result["description"],
                }

    def generate_json_map(self) -> dict:
        tiles = {}
        entities = {}
        items = {}

        player_x = 0
        player_y = 0

        first_tile_with_no_collision = None
        for tile in self.tiles_preset_list.environment_tile_presets:
            if tile.has_collision == False:
                first_tile_with_no_collision = {
                    "texture": tile.texture_id,
                    "color": self.texture_dict[tile.texture_id]["color"],
                    "has_collision": tile.has_collision,
                    "is_transparent": tile.is_transparent,
                }

        for y, row in enumerate(self.map_char_representation.representation):
            for x, char in enumerate(row):
                if char in self.char_representation_dict:
                    char_representation_converted = self.char_representation_dict[char]

                    if "entity" in char_representation_converted:
                        entities[f"{x},{y}"] = char_representation_converted["entity"]

                    if "item" in char_representation_converted:
                        items[f"{x},{y}"] = char_representation_converted["item"]

                    if "tile" in char_representation_converted:
                        tiles[f"{x},{y}"] = char_representation_converted["tile"]

                    if char == "@":
                        player_x = x
                        player_y = y
                elif char == " " and first_tile_with_no_collision != None:
                    if "tile" in char_representation_converted:
                        tiles[f"{x},{y}"] = first_tile_with_no_collision

        result_map = {
            "turn": 0,
            "current_layer": "main",
            "layers": {"main": {"tiles": tiles, "entities": entities, "itens": items}},
            "textures": self.texture_dict,
            "player": {
                "entity": {
                    "max_health": 100,
                    "health": 100,
                    "max_mana": 10,
                    "mana": 10,
                    "base_damage": 10,
                    "entity_name": self.tiles_preset_list.player_tile_preset.name,
                    "turns_to_move": 1,
                    "tile": {
                        "grid_position": {"x": player_x, "y": player_y},
                        "is_explored": True,
                        "preset": "warrior",
                        "texture": self.tiles_preset_list.player_tile_preset.texture_id,
                    },
                },
                "heal_per_turns": 1,
            },
        }

        return result_map
