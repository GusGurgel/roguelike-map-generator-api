from pydantic import BaseModel, Field, ConfigDict, field_validator


class Tile(BaseModel):
    name: str = Field(description="The name of the tile in snake_case.")
    description: str = Field(description="A basic description of the tile")
    color: str = Field(
        description="A valid 6-character Hexadecimal color code (starting with #) representing the dominant or average color of the tile (e.g., `#2A2A2A` for dark stone, `#8B0000` for dried blood). This will be used for minimaps or fallback rendering."
    )


class Position(BaseModel):
    x: int
    y: int


class Texture(BaseModel):
    tileset_position: Position
    tileset_description: str


class TileWithTexture(Tile):
    texture: Texture
