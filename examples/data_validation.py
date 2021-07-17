import streamlit as st
from pydantic import BaseModel, Field, HttpUrl
from pydantic.color import Color

import streamlit_pydantic as sp


class ExampleModel(BaseModel):
    url: HttpUrl
    color: Color
    email: str = Field(..., max_length=100, regex=r"^\S+@\S+$")


data = sp.pydantic_form(key="my_form", model=ExampleModel)
if data:
    st.json(data.json())
