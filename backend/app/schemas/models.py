from pydantic import BaseModel
from typing import List, Optional

class Entity(BaseModel):
    text: str
    label: str

class Table(BaseModel):
    headers: List[str]
    rows: List[List[str]]

class ExtractionResult(BaseModel):
    entities: List[Entity]
    dates: List[str]
    addresses: List[str]
    tables: List[Table]
