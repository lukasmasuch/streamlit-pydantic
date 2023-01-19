from typing import Union

import streamlit as st
from pydantic import BaseModel, Field

import streamlit_pydantic as sp


class PostalAddress(BaseModel):
    street: str
    city: str
    house: int


class EmailAddress(BaseModel):
    email: str
    send_news: bool


class ContactMethodRadio(BaseModel):
    contact: Union[PostalAddress, EmailAddress] = Field(
        description="Use radio type for single_selection.",
        st_kwargs_ui_type="radio",
    )
    text: str

st.header("Form radio inputs from model")
input_data = sp.pydantic_input(key="union_radio_input", model=ContactMethodRadio)
if input_data:
    st.json(input_data)

class ContactMethod(BaseModel):
    contact: Union[PostalAddress, EmailAddress]
    text: str

st.header("Form inputs from model")
input_data = sp.pydantic_input(key="union_input", model=ContactMethod)
if input_data:
    st.json(input_data)


st.header("Form inputs from instance")
instance = ContactMethod(
    contact=EmailAddress(email="instance@example.com", send_news=True),
    text="instance text",
)

instance_input_data = sp.pydantic_input(key="union_input_instance", model=instance)

if instance_input_data:
    st.json(instance_input_data)
