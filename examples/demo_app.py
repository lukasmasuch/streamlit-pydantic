import os
import pathlib

import streamlit as st

from streamlit_pydantic.ui_renderer import name_to_title

path_of_script = pathlib.Path(__file__).parent.resolve()

demos = [str(dir) for dir in filter(os.path.isfile, os.listdir(path_of_script))]

st.write(path_of_script)
st.write(os.listdir(path_of_script))
for i, demo in enumerate(demos):
    st.write(name_to_title(demo))
