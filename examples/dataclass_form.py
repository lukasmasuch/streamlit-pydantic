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


from_model_tab, from_instance_tab = st.tabs(
    ["Form inputs from model", "Form inputs from instance"]
)

with from_model_tab:
    data = sp.pydantic_form(key="my_form", model=ExampleModel)
    if data:
        st.json(json.dumps(data, default=pydantic_encoder))

with from_instance_tab:
    instance = ExampleModel(
        some_number=999, some_boolean=True, some_text="instance text"
    )

    # FIXME: this should be a pydantic_form to match the "from model.." above
    # but initialising a pydantic_form with an instance is not yet supported
    instance_input_data = sp.pydantic_input(key="my_form_instance", model=instance)
    if instance:
        st.json(json.dumps(instance_input_data, default=pydantic_encoder))
