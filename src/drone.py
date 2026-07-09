from pydantic import BaseModel

class Drone(BaseModel):
    width: int
    height: int
    id: int