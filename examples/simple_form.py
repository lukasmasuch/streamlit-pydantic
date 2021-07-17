import streamlit as st
from pydantic import BaseModel

import streamlit_pydantic as sp


class ExampleModel(BaseModel):
    some_text: str
    some_number: int
    some_boolean: bool


data = sp.pydantic_form(key="my_form", model=ExampleModel)
if data:
    st.json(data.json())
