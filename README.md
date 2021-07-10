<!-- markdownlint-disable MD033 MD041 -->
<h1 align="center">
    Streamlit Pydantic
</h1>

<p align="center">
    <strong>Transform Pydantic Models into Streamlit Forms</strong>
</p>

<p align="center">
    <a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/LICENSE" title="Project License"><img src="https://img.shields.io/badge/License-MIT-green.svg"></a>
    <a href="https://github.com/lukasmasuch/streamlit-pydantic/actions?query=workflow%3Abuild-pipeline" title="Build status"><img src="https://img.shields.io/github/workflow/status/lukasmasuch/streamlit-pydantic/build-pipeline?style=flat"></a>
    <a href="https://twitter.com/lukasmasuch" title="Follow on Twitter"><img src="https://img.shields.io/twitter/follow/lukasmasuch.svg?style=social&label=Follow"></a>
</p>

<p align="center">
  <a href="#getting-started">Getting Started</a> •
  <a href="#features">Features & Screenshots</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#support--feedback">Support</a> •
  <a href="https://github.com/lukasmasuch/streamlit-pydantic/issues/new?labels=bug&template=01_bug-report.md">Report a Bug</a> •
  <a href="https://github.com/lukasmasuch/streamlit-pydantic/releases">Changelog</a>
</p>

Streamlit-pydantic makes it easy to deal with Pydantic objects within Streamlit. It allows to directly generate Input as well as Output UI components based on a Pydantic models.

## Getting Started

### Installation

> _Requirements: Python 3.6+._

```bash
pip install streamlit-pydantic
```

### Usage

Streamlit-pydantic provides the `pydantic_input` and `pydantic_output` methods to render input/output UI components from Pydantic models. Those methods can be easily embedded into any streamlit script. For example:

1. Create a script (`my_script.py`) with a Pydantic model and render it via `pydantic_input`:

    ```python
    from pydantic import BaseModel
    import streamlit_pydantic as sp

    class ExampleModel(BaseModel):
        text: str
        integer: int
        test: bool
    
    sp.pydantic_input(ExampleModel, "input_data")
    ```

2. Run the streamlit server on the python script: `streamlit run my_script.py`

3. Find out more usage information in the [Features](#features) section or get inspired by our [examples](#examples).

## Examples

The following collection of examples demonstrate how Streamlit Pydantic can be applied in more advanced scenarios. You can find additional - even more advanced - examples in the [examples folder](./examples). 

### Simple Form

```python
import datetime

import streamlit as st
from pydantic import BaseModel, Field

import streamlit_pydantic as sp


class ExampleModel(BaseModel):
    short_text: str = Field(..., max_length=60, description="Short text property")
    positive_integer: int = Field(
        ..., ge=0, multiple_of=10, description="Positive integer with step count of 10."
    )
    date: datetime.date = Field(
        datetime.date.today(),
        description="Date property.",
    )


with st.form(key="pydantic_form"):
    # Render input model -> input data is accesible via st.session_state["input_data"]
    sp.pydantic_input(ExampleModel, "input_data")
    submit_button = st.form_submit_button(label="Submit")
```

### Input-output Form

```python
from enum import Enum
from typing import Set

import streamlit as st
from pydantic import BaseModel, Field, ValidationError, parse_obj_as

import streamlit_pydantic as sp


class SelectionValue(str, Enum):
    FOO = "foo"
    BAR = "bar"


class ExampleModel(BaseModel):
    long_text: str = Field(..., description="Unlimited text property")
    integer_in_range: int = Field(
        20,
        ge=10,
        lt=30,
        multiple_of=2,
        description="Number property with a limited range.",
    )
    single_selection: SelectionValue = Field(
        ..., description="Only select a single item from a set."
    )
    multi_selection: Set[SelectionValue] = Field(
        ..., description="Allows multiple items from a set."
    )


with st.form(key="pydantic_form"):
    # Render input model
    sp.pydantic_input(ExampleModel, "input_data")
    submit_button = st.form_submit_button(label="Submit")

if submit_button:
    try:
        # Get input data from session
        input_data_obj = parse_obj_as(ExampleModel, st.session_state["input_data"])
        # Show the input data
        sp.pydantic_output(input_data_obj)
    except ValidationError as ex:
        st.error(ex)
```


## Support & Feedback

| Type                     | Channel                                              |
| ------------------------ | ------------------------------------------------------ |
| 🚨&nbsp; **Bug Reports**       | <a href="https://github.com/lukasmasuch/streamlit-pydantic/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+label%3Abug+sort%3Areactions-%2B1-desc+" title="Open Bug Report"><img src="https://img.shields.io/github/issues/lukasmasuch/streamlit-pydantic/bug.svg?label=bug"></a>                                 |
| 🎁&nbsp; **Feature Requests**  | <a href="https://github.com/lukasmasuch/streamlit-pydantic/issues?q=is%3Aopen+is%3Aissue+label%3Afeature+sort%3Areactions-%2B1-desc" title="Open Feature Request"><img src="https://img.shields.io/github/issues/lukasmasuch/streamlit-pydantic/feature.svg?label=feature%20request"></a>                                 |
| 👩‍💻&nbsp; **Usage Questions**   |  _tbd_ |
| 📢&nbsp; **Announcements**  | _tbd_ |

## Features

TODO

## Documentation

TODO

## Contribution

- Pull requests are encouraged and always welcome. Read our [contribution guidelines](https://github.com/lukasmasuch/streamlit-pydantic/tree/main/CONTRIBUTING.md) and check out [help-wanted](https://github.com/lukasmasuch/streamlit-pydantic/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+label%3A"help+wanted"+sort%3Areactions-%2B1-desc+) issues.
- Submit Github issues for any [feature request and enhancement](https://github.com/lukasmasuch/streamlit-pydantic/issues/new?assignees=&labels=feature&template=02_feature-request.md&title=), [bugs](https://github.com/lukasmasuch/streamlit-pydantic/issues/new?assignees=&labels=bug&template=01_bug-report.md&title=), or [documentation](https://github.com/lukasmasuch/streamlit-pydantic/issues/new?assignees=&labels=documentation&template=03_documentation.md&title=) problems.
- By participating in this project, you agree to abide by its [Code of Conduct](https://github.com/lukasmasuch/streamlit-pydantic/blob/main/.github/CODE_OF_CONDUCT.md).
- The [development section](#development) below contains information on how to build and test the project after you have implemented some changes.

## Development

```bash
pip install universal-build
python build.py --make
```

Refer to our [contribution guides](https://github.com/lukasmasuch/streamlit-pydantic/blob/main/CONTRIBUTING.md#development-instructions) for more detailed information on our build scripts and development process.

---

Licensed **MIT**. Created and maintained with ❤️&nbsp; by developers from Berlin.
