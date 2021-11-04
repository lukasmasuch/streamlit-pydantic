import streamlit as st
from pydantic import BaseModel, Field

from typing import Optional
import streamlit_pydantic as sp
from streamlit_pydantic.types import FileContent


class ExampleModel(BaseModel):
    text: str = Field(..., max_length=100, st_kwargs_max_chars=500)
    number: int = Field(
        10, st_kwargs_min_value=10, st_kwargs_max_value=100, st_kwargs_step=5
    )
    single_file: Optional[FileContent] = Field(
        None,
        st_kwargs_type=["png", "jpg"],
    )


data = sp.pydantic_form(key="my_form", model=ExampleModel)
if data:
    st.json(data.json())
