import streamlit as st
from pydantic import BaseModel, EmailStr, Field, HttpUrl, ValidationError
from pydantic_extra_types.color import Color

import streamlit_pydantic as sp


class ExampleModel(BaseModel):
    url: HttpUrl
    color: Color = Field("blue", format="text")
    email: EmailStr


try:
    data = sp.pydantic_form(key="my_form", model=ExampleModel)
    if data:
        st.json(data.model_dump())
except ValidationError as ex:
    st.error(str(ex))
