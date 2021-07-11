import streamlit as st
from pydantic import BaseModel, ByteSize, Field, HttpUrl
from pydantic.color import Color
from pydantic.types import PaymentCardNumber

import streamlit_pydantic as sp


class ExampleModel(BaseModel):
    url: HttpUrl
    color: Color
    email: str = Field(..., max_length=100, regex=r"^\S+@\S+$")


data = sp.pydantic_form(key="my_form", input_class=ExampleModel)
if data:
    st.json(data.json())
