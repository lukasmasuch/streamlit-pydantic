import dataclasses
import json

import streamlit as st
from pydantic.json import pydantic_encoder

import streamlit_pydantic as sp


@dataclasses.dataclass
class ExampleModel:
    some_number: int
    some_boolean: bool
    some_text: str = "default input"


data = sp.pydantic_form(key="my_form", input_class=ExampleModel)
if data:
    st.json(json.dumps(data, default=pydantic_encoder))
