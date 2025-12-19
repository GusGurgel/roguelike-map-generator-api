"""
Collections of prompts
"""

get_texture_description_list_tips = """
You are a game asset specialist. Your task is to extract visual texture descriptions from map prompts.

Guidelines:
1. **Unique Identifiers (CRITICAL)**: The `name` field for each TextureDescription MUST be unique within the list. Think of it as a Primary Key. 
   - Good: 'mossy_stone_wall', 'plain_stone_wall'
   - Bad: 'stone_wall', 'stone_wall' (even if descriptions differ).
2. **Player Tile**: Always include a unique texture entry for the player/hero (e.g., name='player_sprite'), even if not mentioned.
3. **Visual Focus**: Describe patterns, materials, and weathering. Use physical traits that can be used for vector similarity search.
4. **Consistency**: Ensure HEX colors form a cohesive palette. 
5. **Decomposition**: Break complex objects into material textures. For a 'wooden house', extract 'thatch_roof', 'oak_plank_wall', etc.
6. **Naming Convention**: Use snake_case for the `name` field. No spaces or special characters.
"""

get_tile_preset_list_tips = """
You are a game systems engineer. Your task is to categorize map elements and define their physical behavior.

Guidelines:
1. **Categorization Rules**:
    - `player_tile_preset`: The protagonist.
    - `entities_tile_presets`: Living beings (Orcs, NPCs, Monsters).
    - `environment_tile_presets`: Static structure (Floors, Walls, Trees).
    - `items_tile_presets`: Interactive objects (Swords, Chests, Potions).
2. **Entity Transparency**: All dynamic entities (Player and NPCs) MUST have `is_transparent: true`. They do not block the line of sight.
3. **Collision Logic**:
    - `has_collision: true`: For walls, trees, deep water, and solid entities (like enemies or the player).
    - `has_collision: false`: For walkable floors, grass, or small items on the ground.
4. **Consistency**: Every `texture_id` used must exactly match a `name` from the previously generated Texture List. Use snake_case for all identifiers.
5. **Naming Strategy**: Use semantic names that describe both material and function (e.g., 'stone_wall_environment', 'orc_enemy_entity').
6. **Completeness**: You must extract at least one ground-type preset in `environment_tile_presets` to serve as the map's base.
"""

get_entities_list_tips = """
1. UNIQUE IDENTIFICATION: Each 'name' must be a unique slug (e.g., 'goblin_scout').
2. VISUAL MAPPING: The 'tile_preset' must strictly match an existing ID in the 
   entities_tile_presets list to ensure the sprite renders correctly.
3. THREAT CALIBRATION: Use 'threat' levels (1-10) to balance the map difficulty:
   - 1-3: Low-level minions or environmental hazards.
   - 4-7: Standard enemies and elite units.
   - 8-10: Bosses or high-value targets.
4. ENUMERATION: Currently, only 'enemy' is supported for 'entity_type'.
5. PLACEMENT LOGIC: Ensure entity distribution makes sense for the map's 
   narrative and layout (e.g., guards near entrances).
6. PRESET REUSABILITY (IMPORTANT): Do not create duplicate entries for the same 
   type of entity. These are Blueprints, not individual instances. 
   - Example: If the description mentions '3 Skeletons', you only need to define 
     ONE 'skeleton' preset in this list. The game engine will use this single 
     preset to spawn multiple instances later.
"""

get_items_list_tips = """
1. UNIQUE IDENTIFICATION: Each 'name' must be a unique slug identifying the item type (e.g., 'steel_longsword', 'greater_healing_potion').
2. VISUAL MAPPING: The 'tile_preset' must strictly match an existing ID in the items_tile_presets list to ensure the correct icon or sprite is displayed.
3. SUPPORTED ITEM TYPES (STRICT): Currently, ONLY the following two types are supported. Do not use any other categories:
   - 'healing_potion': Consumables used to restore health.
   - 'melee_weapon': Equipment used for close-quarters physical combat.
4. PRESET REUSABILITY (IMPORTANT): These are Templates, not individual world objects. Do not create duplicate entries for the same item type. 
   - Example: If there are 5 identical potions in a room, define the 'healing_potion' preset ONLY ONCE in this list.
5. RARITY CALIBRATION: Assign 'item_rarity' on a scale of 1 to 10:
   - 1-3: Common/Basic items.
   - 4-7: Rare/High-quality items.
   - 8-10: Legendary/Epic unique items.
6. NAMING CONVENTION: Use descriptive, lower-case snake_case for names to maintain consistency with the game engine's database.
"""

get_char_tile_representation_tips = """
1. MANDATORY PLAYER REPRESENTATION (@): You MUST define a CharTileRepresentation using the character '@'. 
   - This defines the player's starting position on the map.
   - The 'tile' field for '@' must be the NAME of a walkable surface (e.g., 'stone_floor').
   - The 'entity' and 'item' fields for this character must be null.

2. UNIQUE CHARACTER MAPPING: Every entry in the list must use a unique 'char' (e.g., '#', '.', 'E', '$'). This acts as the legend for the map grid.

3. NAME-BASED COMPOSITION: Each character maps to the NAME of the presets defined in previous steps:
   - 'tile' (Mandatory): The string name of the base layer (e.g., 'brick_wall').
   - 'entity' (Optional): The string name of a creature (e.g., 'orc_scout'). Use null if empty.
   - 'item' (Optional): The string name of an object (e.g., 'iron_sword'). Use null if empty.

4. ID REFERENCE INTEGRITY (CRITICAL): 
   - The 'tile' field must exactly match the 'name' string of an available TilePreset.
   - The 'entity' field must exactly match the 'name' string of an available EntityPreset (or null).
   - The 'item' field must exactly match the 'name' string of an available ItemPreset (or null).

5. THEMATIC CONSISTENCY: Ensure the combinations make sense. For example, do not map a character to an 'ice_troll' entity on a 'lava_tile' unless the map description specifically requires it.

6. DESCRIPTIVE LABELS: Use the 'description' field to clearly explain the combination (e.g., "A goblin standing on a dungeon floor", "A treasure chest on a grass tile").
"""

get_map_grid_tips = """
1. 2D GRID CONSTRUCTION: Create the map as a list of strings (rows). 
2. RECTANGULAR CONSISTENCY: Every string in the list must have the EXACT same length to maintain a perfect grid.
3. CHARACTER LIMITATION: Use ONLY the characters provided in the 'VALID CHARACTERS' list. Do not invent new characters.
4. PLAYER PLACEMENT (@): You must place exactly ONE '@' character in a logical starting position.
5. VOID VS. PLAYABLE SPACE: 
   - Use a space " " ONLY for the "void" (areas outside the map boundaries or unreachable sections).
   - NEVER use a blank space " " inside a room or hallway. Every playable inch of the map must be filled with a valid tile character (e.g., floor, grass, etc.).
6. GEOMETRY: 
   - Use wall characters to create clear boundaries.
   - Ensure there is a walkable path for the player to reach all interesting areas.
   - Match the spatial feeling of the description (e.g., if it's a 'narrow tunnel', keep it thin).
7. FILL LOGIC (CRITICAL): Do not leave "hollow" rooms. If the map description mentions a 5x5 room, all 25 tiles of that room must be filled with either a floor character, an item character, or an entity character.
8. RAW OUTPUT: Return only the JSON structure containing the list of strings.
"""
