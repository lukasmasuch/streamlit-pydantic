import datetime
from typing import Optional

from pydantic import BaseModel, Field

import streamlit_pydantic as sp


class ExampleModel(BaseModel):
    text: str = Field(..., description="A text property")
    integer: int = Field(..., description="An integer property.")
    date: datetime.date = Field(..., description="A date.")
    optional_datetime: Optional[datetime.datetime] = Field(...,
        description="An optional datetime property."
    )


instance = ExampleModel(text="Some text", integer=40, date=datetime.date.today(), optional_datetime=datetime.datetime.now())
sp.pydantic_output(instance)
