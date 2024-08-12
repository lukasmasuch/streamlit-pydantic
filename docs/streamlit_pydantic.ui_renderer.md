<!-- markdownlint-disable -->

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `streamlit_pydantic.ui_renderer`





---

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L1320"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `pydantic_input`

```python
pydantic_input(
    key: str,
    model: Type[BaseModel],
    group_optional_fields: GroupOptionalFieldsStrategy = 'no',
    lowercase_labels: bool = False,
    ignore_empty_values: bool = False
) → Dict
```

Auto-generates input UI elements for a selected Pydantic class. 



**Args:**
 
 - <b>`key`</b> (str):  A string that identifies the form. Each form must have its own key. 
 - <b>`model`</b> (Type[BaseModel]):  The input model. Either a class or instance based on Pydantic `BaseModel` or Python `dataclass`. 
 - <b>`group_optional_fields`</b> (str, optional):  If `sidebar`, optional input elements will be rendered on the sidebar.  If `expander`,  optional input elements will be rendered inside an expander element. Defaults to `no`. 
 - <b>`lowercase_labels`</b> (bool):  If `True`, all input element labels will be lowercased. Defaults to `False`. 
 - <b>`ignore_empty_values`</b> (bool):  If `True`, empty values for strings and numbers will not be stored in the session state. Defaults to `False`. 



**Returns:**
 
 - <b>`Dict`</b>:  A dictionary with the current state of the input data. 


---

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L1350"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `pydantic_output`

```python
pydantic_output(output_data: Any) → None
```

Auto-generates output UI elements for all properties of a (Pydantic-based) model instance. 



**Args:**
 
 - <b>`output_data`</b> (Any):  The output data. 


---

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L1364"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `pydantic_form`

```python
pydantic_form(
    key: str,
    model: Type[~T],
    submit_label: str = 'Submit',
    clear_on_submit: bool = False,
    group_optional_fields: GroupOptionalFieldsStrategy = 'no',
    lowercase_labels: bool = False,
    ignore_empty_values: bool = False
) → Union[~T, NoneType]
```

Auto-generates a Streamlit form based on the given (Pydantic-based) input class. 



**Args:**
 
 - <b>`key`</b> (str):  A string that identifies the form. Each form must have its own key. 
 - <b>`model`</b> (Type[BaseModel]):  The input model. Either a class or instance based on Pydantic `BaseModel` or Python `dataclass`. 
 - <b>`submit_label`</b> (str):  A short label explaining to the user what this button is for. Defaults to “Submit”. 
 - <b>`clear_on_submit`</b> (bool):  If True, all widgets inside the form will be reset to their default values after the user presses the Submit button. Defaults to False. 
 - <b>`group_optional_fields`</b> (str, optional):  If `sidebar`, optional input elements will be rendered on the sidebar.  If `expander`,  optional input elements will be rendered inside an expander element. Defaults to `no`. 
 - <b>`lowercase_labels`</b> (bool):  If `True`, all input element labels will be lowercased. Defaults to `False`. 
 - <b>`ignore_empty_values`</b> (bool):  If `True`, empty values for strings and numbers will not be stored in the session state. Defaults to `False`. 



**Returns:**
 
 - <b>`Optional[BaseModel]`</b>:  An instance of the given input class,  if the submit button is used and the input data passes the Pydantic validation. 


---

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L76"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `GroupOptionalFieldsStrategy`
An enumeration. 







---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
