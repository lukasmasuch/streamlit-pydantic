import datetime
from enum import Enum
from typing import Dict, List, Literal, Optional, Set

import streamlit as st
from pydantic import BaseModel, Field, SecretStr

import streamlit_pydantic as sp
from streamlit_pydantic.types import FileContent


class SelectionValue(str, Enum):
    FOO = "foo"
    BAR = "bar"


class OtherData(BaseModel):
    text: str
    integer: int


class ShowcaseModel(BaseModel):
    short_text: str = Field(..., max_length=60, description="Short text property")
    password: SecretStr = Field(..., description="Password text property")
    long_text: str = Field(
        ..., format="multi-line", description="Unlimited text property"
    )
    integer_in_range: int = Field(
        20,
        ge=10,
        le=30,
        multiple_of=2,
        description="Number property with a limited range. Optional because of default value.",
    )
    positive_integer: int = Field(
        ..., ge=0, multiple_of=10, description="Positive integer with step count of 10."
    )
    float_number: float = Field(0.001)
    date: Optional[datetime.date] = Field(
        datetime.date.today(),
        description="Date property. Optional because of default value.",
    )
    time: Optional[datetime.time] = Field(
        datetime.datetime.now().time(),
        description="Time property. Optional because of default value.",
    )
    boolean: bool = Field(
        False,
        description="Boolean property. Optional because of default value.",
    )
    read_only_text: str = Field(
        "Lorem ipsum dolor sit amet",
        description="This is a ready only text.",
        readOnly=True,
    )
    file_list: Optional[List[FileContent]] = Field(
        None,
        description="A list of files. Optional property.",
    )
    single_file: Optional[FileContent] = Field(
        None,
        description="A single file. Optional property.",
    )
    single_selection: SelectionValue = Field(
        ..., description="Only select a single item from a set."
    )
    single_selection_with_literal: Literal["foo", "bar"] = Field(
        "foo", description="Only select a single item from a set."
    )
    single_selection_with_radio: SelectionValue = Field(
        description="Use radio type for single_selection.",
        st_kwargs_ui_type="radio",
    )
    multi_selection: Set[SelectionValue] = Field(
        ..., description="Allows multiple items from a set."
    )
    multi_selection_with_literal: Set[Literal["foo", "bar"]] = Field(
        ["foo", "bar"], description="Allows multiple items from a set."
    )
    single_object: OtherData = Field(
        ...,
        description="Another object embedded into this model.",
    )
    string_list: List[str] = Field(
        ..., max_items=20, description="List of string values"
    )
    int_list: List[int] = Field(..., description="List of int values")
    string_dict: Dict[str, str] = Field(
        ..., description="Dict property with string values"
    )
    float_dict: Dict[str, float] = Field(
        ..., description="Dict property with float values"
    )
    object_list: List[OtherData] = Field(
        ...,
        description="A list of objects embedded into this model.",
    )


session_data = sp.pydantic_input(
    key="my_input", model=ShowcaseModel, group_optional_fields="sidebar"
)

with st.expander("Current Input State", expanded=False):
    st.json(session_data)
