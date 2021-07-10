from pydantic import BaseModel

import streamlit_pydantic as sp


class ExampleModel(BaseModel):
    text: str
    integer: int
    test: bool


sp.pydantic_input(ExampleModel, "input_data")
