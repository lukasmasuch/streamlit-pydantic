import datetime

from pydantic import BaseModel, Field

import streamlit_pydantic as sp


class ExampleModel(BaseModel):
    short_text: str = Field(..., max_length=60, description="Short text property")
    positive_integer: int = Field(
        ..., ge=0, multiple_of=10, description="Positive integer with step count of 10."
    )
    date: datetime.date = Field(
        datetime.date.today(),
        description="Date property.",
    )


data = sp.pydantic_form(key="my_form", input_class=ExampleModel)
if data:
    sp.pydantic_output(data)
