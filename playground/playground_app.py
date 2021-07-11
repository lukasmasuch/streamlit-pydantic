import os
import pathlib

import streamlit as st

from streamlit_pydantic.ui_renderer import name_to_title

path_of_script = pathlib.Path(__file__).parent.resolve()
path_to_examples = pathlib.Path(path_of_script).parent.joinpath("examples").resolve()

demos = []
for example_file in os.listdir(path_to_examples):
    file_path = path_to_examples.joinpath(example_file).resolve()

    if not file_path.is_file():
        continue

    demos.append(str(file_path))

st.write(path_of_script)
st.write(os.listdir(path_to_examples))
st.write(demos)
st.write(path_to_examples)
for i, demo in enumerate(demos):
    st.write(name_to_title(demo))
