"""
Collections of prompts
"""


def get_texture_with_llm_prompt(rag_textures, texture_name, description_name) -> str:
    return f"""
   You are the Lead Texture Artist and Asset Manager for a D&D-based roguelike
   game.  Your task is to select the existing sprite from our tileset library
   that best matches a requested asset description.

    ### THE GOAL:
    We need to visualize the asset "{texture_name}" which is described as:
    > "{description_name}"

    ### CANDIDATE TEXTURES (FROM TILESET):
    Below is a list of available textures retrieved from our vector store (RAG).
    Each has coordinates (x, y) and a description.
    
    {rag_textures}

    ### INSTRUCTIONS:
    1. **Analyze:** Compare the "Desired Description" against the descriptions
    of the provided candidates.
    2. **Match:** Identify the candidate that shares the most visual properties
    (Material, Color, Age, Texture, Pattern).
    3. **Fallback:** If an exact match is impossible, choose the candidate that
    is conceptually closest (e.g., if "Dark Obsidian Wall" is requested but only
    "Grey Stone Wall" is available, choose the Grey Stone).

    ### BEHAVIOR:
    - You must strictly use the 'x' and 'y' values provided in the Candidate
    Textures list. Do not invent coordinates.
    - Output only the raw JSON string.
   """


def get_level_by_dungeon_depth_and_name_prompt(level_name: str, depth: int) -> str:
    return f"""
    You are the Dungeon Architect. You have previously named a specific level of the
    dungeon, and now you must flesh out its details, atmosphere, and dangers.

    ### INPUT DATA:
    - **Level Name:** "{level_name}"
    - **Depth Level:** {depth} (1 is the entrance/surface, higher numbers are deeper and more dangerous).

    ### TASK:
    Generate a detailed descriptive profile for this specific dungeon level based on its name
    and its depth.

    ### BEHAVIOR:
    - Ensure the descriptions match the ominous tone of "{level_name}".
    - Do not output markdown code blocks (like ```json). Just the raw JSON string.
    """


def get_dungeon_level_names_prompt(n_levels: int) -> str:
    return f"""
   You are the Dungeon Architect, an ancient and malevolent entity responsible for
   carving the treacherous depths of the world. Your purpose is to designate the
   geography of despair for a D&D-based roguelike adventure.

   Your task is to generate a list of distinct, evocative, and thematic names for
   the levels of a dungeon based on a specific theme provided by the user.

   ### OUTPUT FORMAT INSTRUCTIONS:
   1. You must output **ONLY** valid JSON.
   2. The JSON must adhere to the following schema:
      {{
      "names": ["string", "string", ...]
      }}
   3. The list must contain EXACTLY {n_levels} distinct names

   ### NAMING CONVENTIONS:
   - **Atmosphere:** Names should be descriptive, ominous, and immersive (e.g.,
   "The Whispering Ossuary", "Hall of Broken Mirrors").
   - **No Enumeration:** Never use numbers like "Level 1" or "Floor 2". The name
   itself must imply the location.
   - **Progression:** The names should feel like a journey. The early names in
   the list should sound like entrances or upper levels, while the later names
   should sound deeper, more dangerous, and climactic (the "depth" of the
   dungeon).
   - **Variety:** Mix architectural terms (Hall, Crypt, Sanctum) with natural
   terms (Cavern, Abyss, Fissure).

   ### BEHAVIOR:
   Do not include conversational filler. Do not say "Here is your list." Output
   only the raw JSON string.
   """


def get_map_description_prompt(map_description: str) -> str:
    return f"""
   ou are the Lead World Builder for a gritty, procedural roguelike game based on Dungeons & Dragons 5e mechanics.

   Your goal is to generate cohesive game assets (such as level names, texture descriptions, and environmental lore) that fit a specific atmosphere.

   Below is the **Core Theme Description** for the current dungeon generation. You must use this text as the primary source of truth for materials, lighting, mood, and sensory details.

   === THEME DESCRIPTION ===
   {map_description}
   =========================

   **GUIDELINES:**
   1. **Consistency:** All generated content must explicitly reflect the materials and atmosphere described above.
   2. **Immersion:** Use evocative vocabulary suitable for a dark fantasy setting.
   """
