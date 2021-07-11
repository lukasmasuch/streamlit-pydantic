import os

import streamlit as st

from streamlit_pydantic.ui_renderer import name_to_title

demos = [str(dir) for dir in filter(os.path.isfile, os.listdir(os.curdir))]

for i, demo in enumerate(demos):
    st.write(name_to_title(demo))
