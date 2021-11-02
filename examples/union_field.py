import streamlit as st
from pydantic import BaseModel

from typing import Union

import streamlit_pydantic as sp


class PostalAddress(BaseModel):
    street: str
    city: str
    house: int


class EmailAddress(BaseModel):
    email: str
    send_news: bool


class ContactMethod(BaseModel):
    contact: Union[PostalAddress, EmailAddress]
    text: str


input_data = sp.pydantic_input(key="union_input", model=ContactMethod)
if input_data:
    st.json(input_data)
