from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class DocumentType(str, Enum):
    all = "all"
    text = "text"
    ipfs = "ipfs"

class Permission(str, Enum):
    all = "all"
    shared = "shared"
    private = "private"

class DataIngestionSchema(BaseModel):
    text: str
    shared: bool 
    creator_address: str
    shared_addresses: List[str]
    document_type: DocumentType

class DateSort(str, Enum):
    asc = "asc"
    desc = "desc"

class SearchQuerySchema(BaseModel):
    text: str=""
    shared: Permission = Permission.all
    creator_address: Optional[str]
    document_type: DocumentType = DocumentType.all
    date_sort: DateSort = DateSort.desc
    from_date: date = None
    to_date: date = None
    page: int = 1
    size: int = 10


class ExchangeStructure(BaseModel):
    public_key: str
    aes_key: str