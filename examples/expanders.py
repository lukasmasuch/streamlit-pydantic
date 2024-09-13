"""
An example of using the Expander annotation with nested objects.
"""

from typing_extensions import Annotated, List
from pydantic import BaseModel
import streamlit as st
import streamlit_pydantic as sp
from streamlit_pydantic import Expander


class Child(BaseModel):
    """Child class."""

    name: str
    age: int


class Parent(BaseModel):
    """Parent class."""

    occupation: str
    child: Annotated[List[Child], Expander]


data = sp.pydantic_input("form", model=Parent)

if data:
    obj = Parent.model_validate(data)
    st.json(obj.model_dump())
