from pydantic import BaseModel


class Temp(BaseModel):
    name: str | int


temp = Temp(name=123)

print(temp.name)
