from pydantic import BaseModel

import streamlit_pydantic as sp


def test_renderer() -> None:
    class TestModel(BaseModel):
        name: str

    sp.pydantic_form("my_key", TestModel)
