from pydantic import BaseModel

class Tile(BaseModel):
    b64image : str
    x : int
    y : int
    description : str