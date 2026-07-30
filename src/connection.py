from pydantic import BaseModel, Field
from . import Hub

class Connection(BaseModel):
    hub1: Hub
    hub2: Hub
    max_link_capacity: int = Field(default=1, gt=1)
    current_drone: int = 0

    def get_name(self) -> str:
        return f"{self.hub1.name}-{self.hub2.name}"
    
    def get_max_capacity(self) -> int:
        return self.max_link_capacity