# -*- coding: utf-8 -*-
"""Classes for Request/Response schema definitions."""
from pydantic import BaseModel


class Message(BaseModel):
    detail: str
    system_metrics: dict