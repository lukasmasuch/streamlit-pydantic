import streamlit as st
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from pydantic_extra_types.color import Color

import streamlit_pydantic as sp


class ExampleModel(BaseModel):
    url: HttpUrl
    color: Color = Field("blue", format="text")
    email: EmailStr


data = sp.pydantic_form(key="my_form", model=ExampleModel)
if data:
    st.json(data.model_dump_json())
