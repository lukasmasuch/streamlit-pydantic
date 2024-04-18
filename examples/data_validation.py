import streamlit as st
import streamlit_pydantic as sp
from pydantic import BaseModel, Field, HttpUrl
from pydantic_extra_types.color import Color


class ExampleModel(BaseModel):
    url: HttpUrl
    color: Color = Field("blue", format="text")
    email: str = Field(..., max_length=100, regex=r"^\S+@\S+$")


data = sp.pydantic_form(key="my_form", model=ExampleModel)
if data:
    st.json(data.model_dump_json())
