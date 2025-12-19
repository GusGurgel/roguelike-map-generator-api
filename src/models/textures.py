from pydantic import BaseModel, Field, field_validator


class TextureDescription(BaseModel):
    """
    A structured description of a texture for pixel art generation/retrieval.
    """

    name: str = Field(description="Unique identifier in snake_case.")

    description: str = Field(
        description="A detailed visual description of the texture (e.g., 'cracked stone wall with moss'). This will be vectorized for semantic search.",
    )

    color: str = Field(
        description="A HEX color code representing the dominant tone. Values must start with '#'. Example: '#4287f5'",
        pattern=r"^#(?:[0-9a-fA-F]{3}){1,2}$",
    )

    @field_validator("color")
    @classmethod
    def validate_hex(cls, v):
        if not v.startswith("#"):
            raise ValueError("Color must start with #")
        return v.lower()


class TextureDescriptionList(BaseModel):
    """
    A container for multiple texture descriptions.
    """

    items: list[TextureDescription] = Field(
        description="A list of texture objects, each containing a description and a color."
    )
