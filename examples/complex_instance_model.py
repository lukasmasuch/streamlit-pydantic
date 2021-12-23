import datetime
from enum import Enum
from typing import Dict, List, Literal, Optional, Set

import streamlit as st
from pydantic import BaseModel, Field

import streamlit_pydantic as sp


class OtherData(BaseModel):
    text: str
    integer: int


class SelectionValue(str, Enum):
    FOO = "foo"
    BAR = "bar"


class ExampleModel(BaseModel):
    some_number: float = 10.0  # Optional
    some_text: str = Field(..., description="A text property")
    some_text_with_an_alias: str = Field(
        ..., description="A text property with an alias", alias="some_alias"
    )
    some_integer: int = Field(..., description="An integer property.")
    some_date: datetime.date = Field(..., description="A date.")
    some_time: datetime.time = Field(..., description="A time.")
    some_datetime: datetime.datetime = Field(..., description="A datetime.")
    some_boolean: bool = False  # Option
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
    nested_object: OtherData = Field(
        ...,
        description="Another object embedded into this model.",
    )
    int_list: List[int] = Field(..., description="List of int values")
    object_list: List[OtherData] = Field(
        ...,
        description="A list of objects embedded into this model.",
    )


instance = ExampleModel(
    some_number=999.99,
    some_text="Some INSTANCE text",
    some_alias="Some INSTANCE alias text",
    some_integer=999,
    some_date=datetime.date(1999, 9, 9),
    some_time=datetime.time(9, 9, 16),
    some_datetime=datetime.datetime(1999, 9, 9),
    integer_in_range=28,
    some_boolean=True,
    long_text="This is some really long text from the INSTANCE",
    single_selection=SelectionValue.FOO,
    multi_selection=[SelectionValue.FOO, SelectionValue.BAR],
    read_only_text="INSTANCE read only text",
    nested_object=OtherData(text="nested data INSTANCE text", integer=66),
    int_list=[9, 99, 999],
    object_list=[
        OtherData(text="object list INSTANCE item 1", integer=6),
        OtherData(text="object list INSTANCE item 2", integer=99),
    ],
)

# col1, col2 = st.columns(2)

# with col1:
st.header("Form inputs from model")
data = sp.pydantic_input(key="my_input_model", model=ExampleModel)
with st.expander("Current Input State", expanded=False):
    st.json(data)


# # with col2:
st.header("Form inputs from instance")
data = sp.pydantic_input(key="my_input_instance", model=instance)
with st.expander("Current Input State", expanded=False):
    st.json(data)


with st.expander("Session State", expanded=False):
    st.write(st.session_state)
