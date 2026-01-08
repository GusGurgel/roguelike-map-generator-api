from pydantic import BaseModel, Field, ConfigDict, field_validator


class Tile(BaseModel):
    name: str = Field(description="The name of the tile in snake_case.")
    description: str = Field(description="A basic description of the tile")


class Position(BaseModel):
    x: int
    y: int


class Texture(BaseModel):
    tileset_position: Position
    tileset_description: str


class TileWithTexture(Tile):
    texture: Texture
