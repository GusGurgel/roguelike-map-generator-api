from pydantic import BaseModel, Field, ConfigDict, field_validator


class TexturePosition(BaseModel):
    """
    Represents a coordinate in the dungeon grid.
    Immutable (frozen) to allow hashing and usage as dictionary keys.
    """

    # 'frozen=True' torna a instância imutável e hashable (pode ser chave de dict)
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    x: int = Field(..., ge=0, description="Horizontal grid coordinate (0-indexed).")

    y: int = Field(..., ge=0, description="Vertical grid coordinate (0-indexed).")


class Texture(BaseModel):
    position: TexturePosition
    name: str
    description: str
    description_rag: str
    color: str


class TextureDescription(BaseModel):
    """
    Advanced representation of a texture including PBR (Physically Based Rendering) hints.
    """

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    name: str = Field(
        ...,
        description="Unique ID in snake_case.",
        pattern=r"^[a-z0-9]+(?:_[a-z0-9]+)*$",
        examples=["rusted_iron_plate"],
    )

    description: str = Field(
        ...,
        description="Detailed visual description focusing on physical properties (roughness, reflectivity).",
        min_length=20,
        max_length=500,
    )

    color: str = Field(
        ..., description="Hex color code (#RRGGBB).", pattern=r"^#[0-9a-fA-F]{6}$"
    )

    @field_validator("color")
    @classmethod
    def to_uppercase(cls, v: str) -> str:
        return v.upper()
