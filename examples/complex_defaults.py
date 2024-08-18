from enum import Enum
from typing import Dict, List, Set

import streamlit as st
from pydantic import BaseModel, Field
from pydantic.color import Color

import streamlit_pydantic as sp


class OtherData(BaseModel):
    text: str = "default_text"
    integer: int = 99


class SelectionValue(str, Enum):
    FOO = "foo"
    BAR = "bar"


class ExampleModel(BaseModel):
    """A model to showcase & test different types of pydantic fields with default values."""

    long_text: str = Field(
        "default string", format="multi-line", description="Unlimited text property"
    )
    integer_in_range: int = Field(
        22,
        ge=10,
        le=30,
        multiple_of=2,
        description="Number property with a limited range",
    )
    single_selection: SelectionValue = Field(
        "bar", description="Only select a single item from a set."
    )
    multi_selection: Set[SelectionValue] = Field(
        "bar", description="Allows multiple items from a set."
    )
    read_only_text: str = Field(
        "Lorem ipsum dolor sit amet",
        description="This is ready only text.",
        readOnly=True,
    )
    default_color: Color = Field("yellow", description="A defaulted color")
    default_object: OtherData = Field(
        OtherData(),
        description="An object embedded into the model with a default",
    )
    overriden_default_object: OtherData = Field(
        OtherData(text="overridden object text", integer="12"),
        description="Default object overrides the embedded object defaults",
    )
    default_dict: Dict[str, str] = {"foo": "bar"}
    default_list: List[str] = ["foo", "bar"]
    default_object_list: List[OtherData] = Field(
        [OtherData()],
        description="A list of objects with a default object in the list",
    )


data = sp.pydantic_input(key="my_default_input", model=ExampleModel)
if data:
    st.json(data)
