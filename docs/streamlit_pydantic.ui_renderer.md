<!-- markdownlint-disable -->

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `streamlit_pydantic.ui_renderer`





---

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L824"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `pydantic_input`

```python
pydantic_input(
    key: str,
    input_class: Type[BaseModel],
    use_sidebar: bool = False
) → Dict
```

Auto-generates input UI elements for a selected Pydantic class. 



**Args:**
 
 - <b>`key`</b> (str):  A string that identifies the form. Each form must have its own key. 
 - <b>`input_class`</b> (Type[BaseModel]):  The input class (based on Pydantic BaseModel). 
 - <b>`use_sidebar`</b> (bool, optional):  If `True`, optional input elements will be rendered on the sidebar. 



**Returns:**
 
 - <b>`Dict`</b>:  A dictionary with the current state of the input data. 


---

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L843"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `pydantic_output`

```python
pydantic_output(output_data: Any) → None
```

Auto-generates output UI elements for all properties of a (Pydantic-based) model instance. 



**Args:**
 
 - <b>`output_data`</b> (Any):  The output data. 


---

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L857"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `pydantic_form`

```python
pydantic_form(
    key: str,
    input_class: Type[~T],
    submit_label: str = 'Submit',
    clear_on_submit: bool = False
) → Union[~T, NoneType]
```

Auto-generates a Streamlit form based on the given (Pydantic-based) input class. 



**Args:**
 
 - <b>`key`</b> (str):  A string that identifies the form. Each form must have its own key. 
 - <b>`input_class`</b> (Type[BaseModel]):  The input class (based on Pydantic BaseModel). 
 - <b>`submit_label`</b> (str):  A short label explaining to the user what this button is for. Defaults to “Submit”. 
 - <b>`clear_on_submit`</b> (bool):  If True, all widgets inside the form will be reset to their default values after the user presses the Submit button. Defaults to False. 



**Returns:**
 
 - <b>`Optional[BaseModel]`</b>:  An instance of the given input class,  if the submit button is used and the input data passes the Pydantic validation. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
