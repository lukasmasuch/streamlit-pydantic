import streamlit as st
from pydantic import BaseModel, HttpUrl, EmailStr
from pydantic.color import Color

import streamlit_pydantic as sp


class ExampleModel(BaseModel):
    url: HttpUrl
    color: Color
    email: EmailStr


data = sp.pydantic_form(key="my_form", model=ExampleModel)
if data:
    st.json(data.json())
