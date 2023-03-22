from typing import Union

import streamlit as st
from pydantic import BaseModel

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


from_model_tab, from_instance_tab = st.tabs(
    ["Form inputs from model", "Form inputs from instance"]
)

with from_model_tab:
    input_data = sp.pydantic_input(key="union_input", model=ContactMethod)
    if input_data:
        st.json(input_data)


with from_instance_tab:
    instance = ContactMethod(
        contact=EmailAddress(email="instance@example.com", send_news=True),
        text="instance text",
    )

    instance_input_data = sp.pydantic_input(key="union_input_instance", model=instance)

    if instance_input_data:
        st.json(instance_input_data)


st.markdown("---")

with st.expander("Session State", expanded=False):
    st.write(st.session_state)
