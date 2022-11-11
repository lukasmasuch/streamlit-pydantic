from typing import Any, Dict

import streamlit as st
from pydantic import BaseSettings


def streamlit_secrets_source(settings: BaseSettings) -> Dict[str, Any]:
    """A settings source that loads settings from st.secrets."""
    return dict(st.secrets)


class StreamlitSettings(BaseSettings):
    class Config:
        extra = "ignore"

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                env_settings,
                streamlit_secrets_source,
                file_secret_settings,
            )
