import datetime

from pydantic import BaseModel, Field

import streamlit_pydantic as sp


class ExampleModel(BaseModel):
    text: str = Field(..., description="A text property")
    integer: int = Field(..., description="An integer property.")
    date: datetime.date = Field(..., description="A date.")


instance = ExampleModel(text="Some text", integer=40, date=datetime.date.today())
sp.pydantic_output(instance)
