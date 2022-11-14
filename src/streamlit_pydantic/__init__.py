from . import _about

# define the version before the other imports since these need it
__version__ = _about.__version__

# Do other imports here
import streamlit as st

from .settings import StreamlitSettings
from .ui_renderer import pydantic_form as _pydantic_form

pydantic_form = st._gather_metrics("pydantic_form", _pydantic_form)
from .ui_renderer import pydantic_input as _pydantic_input

pydantic_input = st._gather_metrics("pydantic_input", _pydantic_input)
from .ui_renderer import pydantic_output as _pydantic_output

pydantic_output = st._gather_metrics("pydantic_output", _pydantic_output)
