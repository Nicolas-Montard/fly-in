from pydantic import BaseModel, Field

class Hub(BaseModel):
    height: int
    width: int
    name: str
    zone_type: str = Field(default="normal")
    color: str = Field(default="black")
    max_drones: int = Field(default=1, gt=0)