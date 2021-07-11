<!-- markdownlint-disable MD033 MD041 -->
<h1 align="center">
    Streamlit Pydantic
</h1>

<p align="center">
    <strong>Auto-generate Streamlit UI elements from Pydantic models.</strong>
</p>


<p align="center">
    <a href="https://pypi.org/project/streamlit-pydantic/" title="PyPi Version"><img src="https://img.shields.io/pypi/v/streamlit-pydantic?color=green&style=flat"></a>
    <a href="https://pypi.org/project/streamlit-pydantic/" title="Python Version"><img src="https://img.shields.io/badge/Python-3.6%2B-blue&style=flat"></a>
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

Streamlit-pydantic makes it easy to auto-generate UI elements from [Pydantic](https://github.com/samuelcolvin/pydantic/) models. Just define your data model and turn it into a full-fledged UI form. It supports data validation, nested models, and field limitations. Streamlit-pydantic can be easily integrated into any Streamlit app.

<sup>Alpha Version: Only suggested for experimental usage.</sup>

---

<p align="center">
     Try out and explore various examples in our playground <a href="https://share.streamlit.io/lukasmasuch/streamlit-pydantic/main/playground/playground_app.py">here</a>.
</p>

---

## Highlights

- 🪄&nbsp; Auto-generated UI elements from Pydantic models.
- 📇&nbsp; Out-of-the-box data validation. 
- 📑&nbsp; Supports nested Pydantic models.
- 📏&nbsp; Supports field limits and customizations.
- 🎈&nbsp; Easy to integrate into any Streamlit app.

## Getting Started

### Installation

> _Requirements: Python 3.6+._

```bash
pip install streamlit-pydantic
```

### Usage

1. Create a script (`my_script.py`) with a Pydantic model and render it via `pydantic_form`:

    ```python
    import streamlit as st
    from pydantic import BaseModel
    import streamlit_pydantic as sp

    class ExampleModel(BaseModel):
        some_text: str
        some_number: int
        some_boolean: bool

    data = sp.pydantic_form(key="my_form", input_class=ExampleModel)
    if data:
        st.json(data.json())
    ```

2. Run the streamlit server on the python script: `streamlit run my_script.py`

3. You can find additional examples in the [examples](#examples) section below.

## Support & Feedback

| Type                     | Channel                                              |
| ------------------------ | ------------------------------------------------------ |
| 🚨&nbsp; **Bug Reports**       | <a href="https://github.com/lukasmasuch/streamlit-pydantic/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+label%3Abug+sort%3Areactions-%2B1-desc+" title="Open Bug Report"><img src="https://img.shields.io/github/issues/lukasmasuch/streamlit-pydantic/bug.svg?label=bug"></a>                                 |
| 🎁&nbsp; **Feature Requests**  | <a href="https://github.com/lukasmasuch/streamlit-pydantic/issues?q=is%3Aopen+is%3Aissue+label%3Afeature+sort%3Areactions-%2B1-desc" title="Open Feature Request"><img src="https://img.shields.io/github/issues/lukasmasuch/streamlit-pydantic/feature.svg?label=feature%20request"></a>                                 |
| 👩‍💻&nbsp; **Usage Questions**   |  <a href="https://github.com/lukasmasuch/streamlit-pydantic/issues?q=is%3Aopen+is%3Aissue+label%3Asupport+sort%3Areactions-%2B1-desc" title="Open Support Request"> <img src="https://img.shields.io/github/issues/lukasmasuch/streamlit-pydantic/support.svg?label=support%20request"></a> |
| 📢&nbsp; **Announcements**  | <a href="https://twitter.com/lukasmasuch" title="Follow me on Twitter"><img src="https://img.shields.io/twitter/follow/lukasmasuch.svg?style=social&label=Follow"> |

<br>

## Examples

---

<p align="center">
     👉&nbsp; Try out and explore these examples in our playground <a href="https://share.streamlit.io/lukasmasuch/streamlit-pydantic/main/playground/playground_app.py">here</a>
</p>

---

The following collection of examples demonstrate how Streamlit Pydantic can be applied in more advanced scenarios. You can find additional - even more advanced - examples in the [examples folder](./examples) or in the [playground](https://share.streamlit.io/lukasmasuch/streamlit-pydantic/main/playground/playground_app.py). 

### Simple Form

```python
import streamlit as st
from pydantic import BaseModel

import streamlit_pydantic as sp


class ExampleModel(BaseModel):
    some_text: str
    some_number: int
    some_boolean: bool

data = sp.pydantic_form(key="my_form", input_class=ExampleModel)
if data:
    st.json(data.json())
```

### Date Validation

```python
import streamlit as st
from pydantic import BaseModel, Field, HttpUrl
from pydantic.color import Color

import streamlit_pydantic as sp


class ExampleModel(BaseModel):
    url: HttpUrl
    color: Color
    email: str = Field(..., max_length=100, regex=r"^\S+@\S+$")


data = sp.pydantic_form(key="my_form", input_class=ExampleModel)
if data:
    st.json(data.json())
```

### Complex Nested Model

```python
from enum import Enum
from typing import Set

import streamlit as st
from pydantic import BaseModel, Field, ValidationError, parse_obj_as

import streamlit_pydantic as sp


class OtherData(BaseModel):
    text: str
    integer: int


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
    single_object: OtherData = Field(
        ...,
        description="Another object embedded into this model.",
    )


data = sp.pydantic_form(key="my_form", input_class=ExampleModel)
if data:
    st.json(data.json())
```

### Render Input

```python
from pydantic import BaseModel

import streamlit_pydantic as sp


class ExampleModel(BaseModel):
    some_text: str
    some_number: int = 10  # Optional
    some_boolean: bool = True  # Option


input_data = sp.pydantic_input("model_input", ExampleModel, use_sidebar=True)
```

### Render Output

```python
import datetime

from pydantic import BaseModel, Field

import streamlit_pydantic as sp


class ExampleModel(BaseModel):
    text: str = Field(..., description="A text property")
    integer: int = Field(..., description="An integer property.")
    date: datetime.date = Field(..., description="A date.")


instance = ExampleModel(text="Some text", integer=40, date=datetime.date.today())
sp.pydantic_output(instance)
```

### Custom Form

```python
import streamlit as st
from pydantic import BaseModel

import streamlit_pydantic as sp


class ExampleModel(BaseModel):
    some_text: str
    some_number: int = 10
    some_boolean: bool = True


with st.form(key="pydantic_form"):
    sp.pydantic_input(key="my_input_model", input_class=ExampleModel)
    submit_button = st.form_submit_button(label="Submit")
```

## Documentation

The API documentation can be found [here](./docs). To generate UI elements, you can use the high-level [`pydantic_form`](./docs/streamlit_pydantic.ui_renderer.md#function-pydantic_form) method. Or the more flexible lower-level [`pydantic_input`](./docs/streamlit_pydantic.ui_renderer.md#function-pydantic_input) and [`pydantic_output`](./docs/streamlit_pydantic.ui_renderer.md#function-pydantic_output) methods. See the [examples](#examples) section on how to use those methods.

## Limitations

TBD

## Contribution

- Pull requests are encouraged and always welcome. Read our [contribution guidelines](https://github.com/lukasmasuch/streamlit-pydantic/tree/main/CONTRIBUTING.md) and check out [help-wanted](https://github.com/lukasmasuch/streamlit-pydantic/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+label%3A"help+wanted"+sort%3Areactions-%2B1-desc+) issues.
- Submit Github issues for any [feature request and enhancement](https://github.com/lukasmasuch/streamlit-pydantic/issues/new?assignees=&labels=feature&template=02_feature-request.md&title=), [bugs](https://github.com/lukasmasuch/streamlit-pydantic/issues/new?assignees=&labels=bug&template=01_bug-report.md&title=), or [documentation](https://github.com/lukasmasuch/streamlit-pydantic/issues/new?assignees=&labels=documentation&template=03_documentation.md&title=) problems.
- By participating in this project, you agree to abide by its [Code of Conduct](https://github.com/lukasmasuch/streamlit-pydantic/blob/main/.github/CODE_OF_CONDUCT.md).
- The [development section](#development) below contains information on how to build and test the project after you have implemented some changes.

## Development

To build the project and run the style/linter checks, execute:

```bash
pip install universal-build
python build.py --make --check
```

Refer to our [contribution guides](https://github.com/lukasmasuch/streamlit-pydantic/blob/main/CONTRIBUTING.md#development-instructions) for more detailed information on our build scripts and development process.

---

Licensed **MIT**. Created and maintained with ❤️&nbsp; by developers from Berlin.
