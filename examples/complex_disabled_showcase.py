import datetime
from enum import Enum
from typing import Dict, List, Literal, Set

import streamlit as st
from pydantic import Base64UrlBytes, BaseModel, Field, SecretStr
from pydantic_extra_types.color import Color

import streamlit_pydantic as sp


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
    date: datetime.date = Field(
        datetime.date.today(),
        readOnly=True,
        description="Date property. Optional because of default value.",
    )
    time: datetime.time = Field(
        datetime.datetime.now().time(),
        readOnly=True,
        description="Time property. Optional because of default value.",
    )
    dt: datetime.datetime = Field(
        datetime.datetime.now(),
        readOnly=True,
        description="Datetime property. Optional because of default value.",
    )
    boolean: bool = Field(
        False,
        readOnly=True,
        description="Boolean property. Optional because of default value.",
    )
    colour: Color = Field(
        Color("Blue"),
        readOnly=True,
        description="Color property. Optional because of default value.",
    )
    read_only_text: str = Field(
        "Lorem ipsum dolor sit amet",
        description="This is a read only text.",
        readOnly=True,
    )
    file_list: List[Base64UrlBytes] = Field(
        [],
        readOnly=True,
        description="A list of files. Optional property.",
    )
    single_file: Base64UrlBytes = Field(
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
    short_text="Some INSTANCE text",
    password="$uper_$ecret!",
    long_text="This is some really long text from the INSTANCE",
    integer_in_range=28,
    positive_integer=20,
    float_number=0.00444,
    date=datetime.date(1999, 9, 9),
    time=datetime.time(9, 9, 16),
    dt=datetime.datetime(1999, 9, 9),
    boolean=True,
    colour=Color("Yellow"),
    read_only_text="INSTANCE read only text",
    file_list=[],
    single_file=b"",
    single_selection=SelectionValue.FOO,
    single_selection_with_literal="bar",
    multi_selection=[SelectionValue.FOO, SelectionValue.BAR],
    multi_selection_with_literal=["foo", "bar"],
    single_object=OtherData(text="nested data INSTANCE text", integer=66),
    string_list=["a", "ab", "abc"],
    int_list=[9, 99, 999],
    string_dict={"key 1": "A", "key 2": "B", "key 3": "C"},
    float_dict={"key A": 9.99, "key B": 66.0, "key C": -55.8},
    object_list=[
        OtherData(text="object list INSTANCE item 1", integer=6),
        OtherData(text="object list INSTANCE item 2", integer=99),
    ],
)


from_model_tab, from_instance_tab = st.tabs(
    ["Form inputs from model", "Form inputs from instance"]
)

with from_model_tab:
    data = sp.pydantic_input(key="my_disabled_model", model=DisabledModel)
    with st.expander("Current Input State", expanded=False):
        st.json(data)

with from_instance_tab:
    data = sp.pydantic_input(key="my_disabled_instance", model=instance)
    with st.expander("Current Input State", expanded=False):
        st.json(data)
