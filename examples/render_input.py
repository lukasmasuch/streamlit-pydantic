from pydantic import BaseModel

import streamlit_pydantic as sp


class ExampleModel(BaseModel):
    some_text: str
    some_number: int = 10
    some_boolean: bool = True


# Input data is accesible via st.session_state["input_data"]
sp.pydantic_input("model_input", ExampleModel, use_sidebar=True)
