<!-- markdownlint-disable -->

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `streamlit_pydantic.ui_renderer`





---

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `name_to_title`

```python
name_to_title(name: str) → str
```

Converts a camelCase or snake_case name to title case. 


---

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L25"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `function_has_named_arg`

```python
function_has_named_arg(func: Callable, parameter: str) → bool
```






---

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L36"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `has_output_ui_renderer`

```python
has_output_ui_renderer(data_item: BaseModel) → bool
```






---

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L40"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `has_input_ui_renderer`

```python
has_input_ui_renderer(input_class: Type[BaseModel]) → bool
```






---

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L44"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `is_compatible_audio`

```python
is_compatible_audio(mime_type: str) → bool
```






---

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L48"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `is_compatible_image`

```python
is_compatible_image(mime_type: str) → bool
```






---

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L52"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `is_compatible_video`

```python
is_compatible_video(mime_type: str) → bool
```






---

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L810"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `pydantic_input`

```python
pydantic_input(
    input_class: Type[BaseModel],
    session_input_key: str = 'input_data',
    use_sidebar: bool = False
) → None
```

Shows input UI elements for a selected Pydantic class. 



**Args:**
 
 - <b>`input_class`</b> (Type[BaseModel]):  The input class (based on Pydantic BaseModel). 
 - <b>`session_input_key`</b> (str, optional):  The key used to store the input data inside the session. Defaults to `input_data`. 
 - <b>`use_sidebar`</b> (bool, optional):  If `True`, optional input elements will be rendered on the sidebar. 


---

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L826"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `pydantic_output`

```python
pydantic_output(output_data: Any) → None
```

Renders the output data based on an instance of a Pydantic model. 



**Args:**
 
 - <b>`output_data`</b> (Any):  The output data. 


---

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L56"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `InputUI`




<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L57"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    streamlit_container: Any,
    input_class: Type[BaseModel],
    session_input_key: str = 'input_data',
    use_sidebar: bool = False
)
```








---

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L87"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `render_ui`

```python
render_ui() → None
```






---

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L624"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `OutputUI`




<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L625"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(output_data: Any, input_data: Optional[Any] = None)
```








---

<a href="https://github.com/lukasmasuch/streamlit-pydantic/blob/main/src/streamlit_pydantic/ui_renderer.py#L629"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `render_ui`

```python
render_ui() → None
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
