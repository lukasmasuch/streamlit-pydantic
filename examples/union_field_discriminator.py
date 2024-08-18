from typing import Literal, Optional, Union

import streamlit as st
from pydantic import BaseModel, Field

import streamlit_pydantic as sp


class PostalAddress(BaseModel):
    contact_type: Literal["postal"]
    street: str
    city: str
    house: int


class EmailAddress(BaseModel):
    contact_type: Literal["email"]
    email: str
    send_news: bool


class ContactMethod(BaseModel):
    contact: Optional[Union[PostalAddress, EmailAddress]] = Field(
        ..., discriminator="contact_type"
    )
    text: str


from_model_tab, from_instance_tab = st.tabs(
    ["Form inputs from model", "Form inputs from instance"]
)

with from_model_tab:
    input_data = sp.pydantic_input(key="discriminator_union_input", model=ContactMethod)
    if input_data:
        st.json(input_data)


with from_instance_tab:
    instance = ContactMethod(
        contact=EmailAddress(
            contact_type="email", email="instance@example.com", send_news=True
        ),
        text="instance text",
    )

    instance_input_data = sp.pydantic_input(
        key="discriminator_union_input_instance", model=instance
    )

    if instance_input_data:
        st.json(instance_input_data)

st.markdown("---")

with st.expander("Session State", expanded=False):
    st.write(st.session_state)
