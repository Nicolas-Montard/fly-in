from pydantic import BaseModel, Field

class Connection(BaseModel):
    hub1: str
    hub2: str
    max_link_capacity: int = Field(default=1)