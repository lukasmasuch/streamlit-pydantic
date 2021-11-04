from enum import Enum
from typing import Set

import streamlit as st
from pydantic import BaseModel, Field, ValidationError, parse_obj_as

import streamlit_pydantic as sp


class OtherData(BaseModel):
    text: str
    integer: int


class SelectionValue(str, Enum):
    FOO = "foo"
    BAR = "bar"


class ExampleModel(BaseModel):
    long_text: str = Field(
        ..., format="multi-line", description="Unlimited text property"
    )
    integer_in_range: int = Field(
        20,
        ge=10,
        le=30,
        multiple_of=2,
        description="Number property with a limited range.",
    )
    single_selection: SelectionValue = Field(
        ..., description="Only select a single item from a set."
    )
    multi_selection: Set[SelectionValue] = Field(
        ..., description="Allows multiple items from a set."
    )
    read_only_text: str = Field(
        "Lorem ipsum dolor sit amet",
        description="This is a ready only text.",
        readOnly=True,
    )
    single_object: OtherData = Field(
        ...,
        description="Another object embedded into this model.",
    )


data = sp.pydantic_form(key="my_form", model=ExampleModel)
if data:
    st.json(data.json())
