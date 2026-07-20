from pydantic import BaseModel, Field
from . import Hub

class Connection(BaseModel):
    hub1: Hub
    hub2: Hub
    max_link_capacity: int = Field(default=1, gt=1)