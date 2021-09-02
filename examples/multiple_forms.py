import datetime

import streamlit as st
from pydantic import BaseModel

import streamlit_pydantic as sp


class ExampleModel(BaseModel):
    some_text: str
    some_number: int = 10
    some_boolean: bool = True


col1, col2 = st.columns(2)

with col1:
    data = sp.pydantic_form(key="form_1", model=ExampleModel)
    if data:
        st.json(data.json())

with col2:
    data = sp.pydantic_form(key="form_2", model=ExampleModel)
    if data:
        st.json(data.json())
