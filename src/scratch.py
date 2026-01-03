from typing import Optional
from pydantic import BaseModel, Field
from llm_models import get_model, Providers, GroqModels

# Supondo que esta função retorne uma string de contexto relevante
from vector_db import query_vector_store

from devtools import pprint


class Texture(BaseModel):
    """Coordinates for the texture mapping."""

    description: str = Field(description="description of the texture")
    x: int = Field(description="X coordinate on the sprite sheet")
    y: int = Field(description="Y coordinate on the sprite sheet")


class MeleeWeapon(BaseModel):
    """Represents a melee weapon in the game."""

    weapon_name: str
    weapon_description: str
    rarity: int = Field(
        description="Rarity scale from 1 (common) to 10 (legendary).", ge=1, le=10
    )
    texture: Texture = Field(
        description="Description of the Melee Weapon texture"
    )  ## Retirada do Vector Store de Items


def main():
    # 2. Configuração do Modelo
    try:
        model = get_model(Providers.GROQ, GroqModels.OPENAI_GPT_OSS_120B)
    except Exception as e:
        print(f"Erro ao carregar modelo: {e}")
        return

    # 3. Structured Output Direto
    # Passar a classe Pydantic (e não o schema) faz o .invoke retornar o objeto pronto
    structured_llm = model.with_structured_output(MeleeWeapon)

    # 5. Prompting Melhorado
    # Dê instruções claras e injete o contexto
    prompt_template = f"""
    You are a game designer assistant. Generate a valid JSON object for a Melee Weapon based on the description below.
    
    Weapon Description:  The excalibur, once the sword of the kings Arthur

    For the texture coordinates (x, y), if not specified, assume standard starting position (0,0).
    """

    # 6. Execução e Tratamento de Erros
    try:
        result: MeleeWeapon = structured_llm.invoke(prompt_template)

        # print(user_query)
        # O resultado já é uma instância de MeleeWeapon, não precisa de model_validate
        vector_texture = (
            query_vector_store(result.texture.description, "items", documents_count=1)
        )[0]

        result.texture.description = vector_texture["description"]
        result.texture.x = vector_texture["x"]
        result.texture.y = vector_texture["y"]

        # print(f"Weapon Created: {result.weapon_name}")
        # print(f"Rarity: {result.rarity}/10")
        # print(
        #     f"Texture: {result.texture.description} at ({result.texture.x}, {result.texture.y})"
        # )

        pprint(result.model_dump_json())

        # Se precisar converter para dict ou json depois:
        # print(result.model_dump_json(indent=2))

    except Exception as e:
        print(
            f"Falha ao gerar a arma. O modelo retornou um formato inválido ou houve erro de conexão.\nDetalhes: {e}"
        )


if __name__ == "__main__":
    main()
