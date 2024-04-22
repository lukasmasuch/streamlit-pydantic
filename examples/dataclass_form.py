import dataclasses
import json

import streamlit as st

import streamlit_pydantic as sp


@dataclasses.dataclass
class ExampleModel:
    some_number: int
    some_boolean: bool
    some_text: str = "default input"


from_model_tab, from_instance_tab = st.tabs(
    ["Form inputs from model", "Form inputs from instance"]
)

with from_model_tab:
    data = sp.pydantic_form(key="my_dataclass_form", model=ExampleModel)
    if data:
        st.json(dataclasses.asdict(data))

with from_instance_tab:
    instance = ExampleModel(
        some_number=999, some_boolean=True, some_text="instance text"
    )

    instance_input_data = sp.pydantic_form(
        key="my_dataclass_form_instance", model=instance
    )
    if instance_input_data:
        st.json(dataclasses.asdict(instance_input_data))
