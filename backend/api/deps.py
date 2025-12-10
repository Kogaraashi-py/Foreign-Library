from typing import Annotated,Generator
from fastapi import Depends
from sqlmodel import Session
from core.data_base import get_session
session_dep = Annotated[Session,Depends(get_session)]








