import streamlit as st
from pydantic import BaseModel

import streamlit_pydantic as sp


class ExampleModel(BaseModel):
    some_text: str
    some_number: int = 10
    some_boolean: bool = True


with st.form(key="pydantic_form"):
    data = sp.pydantic_input(key="my_custom_form_model", model=ExampleModel)
    submit_button = st.form_submit_button(label="Submit")
    obj = ExampleModel(data)

# if data:
#     st.json(obj.model_dump())
