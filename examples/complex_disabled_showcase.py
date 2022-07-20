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


class DisabledModel(BaseModel):
    short_text: str = Field(
        ..., readOnly=True, max_length=60, description="Short text property"
    )
    password: SecretStr = Field(
        ..., readOnly=True, description="Password text property"
    )
    long_text: str = Field(
        ..., format="multi-line", readOnly=True, description="Unlimited text property"
    )
    integer_in_range: int = Field(
        20,
        ge=10,
        le=30,
        multiple_of=2,
        readOnly=True,
        description="Number property with a limited range. Optional because of default value.",
    )
    positive_integer: int = Field(
        ...,
        ge=0,
        multiple_of=10,
        readOnly=True,
        description="Positive integer with step count of 10.",
    )
    float_number: float = Field(0.001, readOnly=True)
    date: Optional[datetime.date] = Field(
        datetime.date.today(),
        readOnly=True,
        description="Date property. Optional because of default value.",
    )
    time: Optional[datetime.time] = Field(
        datetime.datetime.now().time(),
        readOnly=True,
        description="Time property. Optional because of default value.",
    )
    boolean: bool = Field(
        False,
        readOnly=True,
        description="Boolean property. Optional because of default value.",
    )
    read_only_text: str = Field(
        "Lorem ipsum dolor sit amet",
        description="This is a read only text.",
        readOnly=True,
    )
    file_list: Optional[List[FileContent]] = Field(
        None,
        readOnly=True,
        description="A list of files. Optional property.",
    )
    single_file: Optional[FileContent] = Field(
        None,
        readOnly=True,
        description="A single file. Optional property.",
    )
    single_selection: SelectionValue = Field(
        ..., readOnly=True, description="Only select a single item from a set."
    )
    single_selection_with_literal: Literal["foo", "bar"] = Field(
        "foo", readOnly=True, description="Only select a single item from a set."
    )
    multi_selection: Set[SelectionValue] = Field(
        ..., readOnly=True, description="Allows multiple items from a set."
    )
    multi_selection_with_literal: Set[Literal["foo", "bar"]] = Field(
        ["foo", "bar"], readOnly=True, description="Allows multiple items from a set."
    )
    single_object: OtherData = Field(
        ...,
        readOnly=True,
        description="Another object embedded into this model.",
    )
    string_list: List[str] = Field(
        ..., max_items=20, readOnly=True, description="List of string values"
    )
    int_list: List[int] = Field(..., readOnly=True, description="List of int values")
    string_dict: Dict[str, str] = Field(
        ..., readOnly=True, description="Dict property with string values"
    )
    float_dict: Dict[str, float] = Field(
        ..., readOnly=True, description="Dict property with float values"
    )
    object_list: List[OtherData] = Field(
        ...,
        readOnly=True,
        description="A list of objects embedded into this model.",
    )


instance = DisabledModel(
    some_number=999.99,
    short_text="Some INSTANCE text",
    password="$uper_$ecret!",
    some_alias="Some INSTANCE alias text",
    positive_integer=20,
    some_date=datetime.date(1999, 9, 9),
    some_time=datetime.time(9, 9, 16),
    some_datetime=datetime.datetime(1999, 9, 9),
    integer_in_range=28,
    some_boolean=True,
    long_text="This is some really long text from the INSTANCE",
    single_selection=SelectionValue.FOO,
    disabled_selection=SelectionValue.BAR,
    multi_selection=[SelectionValue.FOO, SelectionValue.BAR],
    read_only_text="INSTANCE read only text",
    single_object=OtherData(text="nested data INSTANCE text", integer=66),
    string_dict={"key 1": "A", "key 2": "B", "key 3": "C"},
    float_dict={"key A": 9.99, "key B": 66.0, "key C": -55.8},
    int_list=[9, 99, 999],
    string_list=["a", "ab", "abc"],
    object_list=[
        OtherData(text="object list INSTANCE item 1", integer=6),
        OtherData(text="object list INSTANCE item 2", integer=99),
    ],
)


session_data = sp.pydantic_input(
    key="my_disabled_input",
    model=instance,
)

with st.expander("Current Input State", expanded=False):
    st.json(session_data)
