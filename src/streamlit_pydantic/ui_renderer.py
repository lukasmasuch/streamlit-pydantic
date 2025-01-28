import base64
import contextlib
import dataclasses
import datetime
import inspect
import json
import mimetypes
import re
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar

import pandas as pd
import streamlit as st
from pydantic import BaseModel, TypeAdapter, ValidationError
from pydantic import dataclasses as pydantic_dataclasses
from pydantic_extra_types.color import Color

from streamlit_pydantic import schema_utils

_OVERWRITE_STREAMLIT_KWARGS_PREFIX = "st_kwargs_"


def _pydantic_encoder(obj: Any) -> Any:
    """Simplified version of pydantic v1's deprecated json encoder."""
    if isinstance(obj, BaseModel):
        return obj.model_dump(mode="json")
    elif dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        # Object is a dataclass instance
        return dataclasses.asdict(obj)

    raise TypeError(
        f"Object of type '{obj.__class__.__name__}' is not JSON serializable"
    )


def _name_to_title(name: str) -> str:
    """Converts a camelCase or snake_case name to title case."""
    # If camelCase -> convert to snake case
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()
    # Convert to title case
    return name.replace("_", " ").strip().title()


def _function_has_named_arg(func: Callable, parameter: str) -> bool:
    try:
        sig = inspect.signature(func)
        for param in sig.parameters.values():
            if param.name == "input":
                return True
    except Exception:
        return False
    return False


def _has_output_ui_renderer(data_item: BaseModel) -> bool:
    return hasattr(data_item, "render_output_ui")


def _has_input_ui_renderer(input_class: Type[BaseModel]) -> bool:
    return hasattr(input_class, "render_input_ui")


def _is_compatible_audio(mime_type: str) -> bool:
    return mime_type in ["audio/mpeg", "audio/ogg", "audio/wav"]


def _is_compatible_image(mime_type: str) -> bool:
    return mime_type in ["image/png", "image/jpeg"]


def _is_compatible_video(mime_type: str) -> bool:
    return mime_type in ["video/mp4"]


class GroupOptionalFieldsStrategy(str, Enum):
    NO = "no"
    EXPANDER = "expander"
    SIDEBAR = "sidebar"


class InputUI:
    """Input UI renderer.

    lazydocs: ignore
    """

    def __init__(
        self,
        key: str,
        model: Type[BaseModel],
        streamlit_container: Any = st,
        group_optional_fields: GroupOptionalFieldsStrategy = "no",  # type: ignore
        lowercase_labels: bool = False,
        ignore_empty_values: bool = False,
        return_model: bool = False,
    ):
        self._key = key
        self._return_model = return_model

        self._session_state = st.session_state

        # Initialize Sessions State
        if "run_id" not in st.session_state:
            self._session_state.run_id = 0

        self._session_input_key = self._key + "-data"
        if self._session_input_key not in st.session_state:
            self._session_state[self._session_input_key] = {}

        self._lowercase_labels = lowercase_labels
        self._group_optional_fields = group_optional_fields
        self._streamlit_container = streamlit_container
        self._ignore_empty_values = ignore_empty_values

        if dataclasses.is_dataclass(model):
            self._input_class = model
            if isinstance(model, type):
                self._type_adapter = TypeAdapter(pydantic_dataclasses.dataclass(model))
            else:
                self._type_adapter = TypeAdapter(
                    pydantic_dataclasses.dataclass(model.__class__)
                )
            self._input_schema = self._type_adapter.json_schema()
        else:
            self._type_adapter = None
            self._input_schema = model.model_json_schema(by_alias=True)
            self._input_class = model

        self._schema_properties = self._input_schema.get("properties", {})
        self._schema_references = self._input_schema.get("$defs", {})
        self._schema_required = self._input_schema.get("required", {})

    def render_ui(self) -> Dict:
        if _has_input_ui_renderer(self._input_class):
            # The input model has a rendering function
            # The rendering also returns the current state of input data
            self._session_state[self._session_input_key] = (
                self._input_class.render_input_ui(  # type: ignore
                    self._streamlit_container,
                    self._session_state[self._session_input_key],
                ).model_dump()
            )
            return self._session_state[self._session_input_key]

        properties_in_expander = []

        # check if the input_class is an instance and build value dicts
        if isinstance(self._input_class, BaseModel):
            instance_dict = self._input_class.model_dump()
            instance_dict_by_alias = self._input_class.model_dump(by_alias=True)
        elif isinstance(self._input_class.__class__, type):  # for dataclasses
            instance_dict = dict(self._input_class.__dict__)
            instance_dict_by_alias = None
        else:
            instance_dict = None
            instance_dict_by_alias = None

        for property_key in self._schema_properties.keys():
            streamlit_app = self._streamlit_container
            if property_key not in self._schema_required:
                if self._group_optional_fields == "sidebar":
                    streamlit_app = self._streamlit_container.sidebar
                elif self._group_optional_fields == "expander":
                    properties_in_expander.append(property_key)
                    # Render properties later in expander (see below)
                    continue

            property = self._schema_properties[property_key]

            if not property.get("title"):
                # Set property key as fallback title
                property["title"] = _name_to_title(property_key)

            # if there are instance values, add them to the property dict
            if instance_dict is not None:
                instance_value = instance_dict.get(property_key)
                if instance_value in [None, ""] and instance_dict_by_alias:
                    instance_value = instance_dict_by_alias.get(property_key)
                if instance_value not in [None, ""]:
                    property["init_value"] = instance_value
                    # keep a reference of the original class to help with non-discriminated unions
                    # TODO: This will not succeed for attributes that have an alias
                    attr = getattr(self._input_class, property_key, None)
                    if attr is not None:
                        property["instance_class"] = str(type(attr))

            try:
                value = self._render_property(streamlit_app, property_key, property)
                if not self._is_value_ignored(property_key, value):
                    self._store_value(property_key, value)
            except Exception:
                pass

        if properties_in_expander:
            # Render optional properties in expander
            with self._streamlit_container.expander(
                "Optional Parameters", expanded=False
            ):
                for property_key in properties_in_expander:
                    property = self._schema_properties[property_key]

                    if not property.get("title"):
                        # Set property key as fallback title
                        property["title"] = _name_to_title(property_key)

                    try:
                        value = self._render_property(
                            self._streamlit_container, property_key, property
                        )

                        if not self._is_value_ignored(property_key, value):
                            self._store_value(property_key, value)

                    except Exception:
                        pass

        input_state = self._session_state[self._session_input_key]

        if self._return_model:
            # Validate and return a BaseModel or DataClass instance
            try:
                if self._type_adapter is not None:
                    self._type_adapter.validate_python(input_state)
                    if isinstance(self._input_class, type):
                        # DataClass model
                        return self._input_class(**input_state)  # type: ignore
                    else:
                        # DataClass instance
                        return self._input_class.__class__(**input_state)
                else:
                    # BaseModel
                    return self._input_class.model_validate(input_state)  # type: ignore
            except ValidationError as ex:
                error_text = "**Input failed validation:**"
                for error in ex.errors():
                    if "loc" in error and "msg" in error:
                        location = ".".join(error["loc"]).replace("__root__.", "")  # type: ignore
                        error_msg = f"**{location}:** " + error["msg"]
                        error_text += "\n\n" + error_msg
                    else:
                        # Fallback
                        error_text += "\n\n" + str(error)
                st.warning(error_text)
                return None  # type: ignore
        else:
            return input_state

    def _get_overwrite_streamlit_kwargs(self, key: str, property: Dict) -> Dict:
        streamlit_kwargs: Dict = {}

        for kwarg in property:
            if kwarg.startswith(_OVERWRITE_STREAMLIT_KWARGS_PREFIX):
                streamlit_kwargs[
                    kwarg.replace(_OVERWRITE_STREAMLIT_KWARGS_PREFIX, "")
                ] = property[kwarg]
        return streamlit_kwargs

    def _get_default_streamlit_input_kwargs(self, key: str, property: Dict) -> Dict:
        label = property.get("title")
        if label and self._lowercase_labels:
            label = label.lower()

        disabled = False
        if property.get("readOnly"):
            # Read only property -> only show value
            disabled = True

        streamlit_kwargs = {
            "label": label,
            "key": str(self._session_state.run_id) + "-" + str(self._key) + "-" + key,
            "disabled": disabled,
            # "on_change": detect_change, -> not supported for inside forms
            # "args": (key,),
        }

        if property.get("description"):
            streamlit_kwargs["help"] = property.get("description")
        elif property.get("help"):
            # Fallback to help. Used more frequently with dataclasses
            streamlit_kwargs["help"] = property.get("help")

        return streamlit_kwargs

    def _is_value_ignored(self, property_key: str, value: Any) -> bool:
        """Returns `True` if the value should be ignored for storing in session.

        This is the case if `ignore_empty_values` is activated and the value is empty and not already set/changed before.
        """
        return (
            self._ignore_empty_values
            and (
                type(value) == int or type(value) == float or isinstance(value, str)
            )  # only for int, float or str
            and not value
            and self._get_value(property_key) is None
        )

    def _store_value_in_state(self, state: dict, key: str, value: Any) -> None:
        key_elements = key.split(".")
        for i, key_element in enumerate(key_elements):
            if i == len(key_elements) - 1:
                # add value to this element
                state[key_element] = value
                return
            if key_element not in state:
                state[key_element] = {}
            state = state[key_element]

    def _get_value_from_state(self, state: dict, key: str) -> Any:
        key_elements = key.split(".")
        for i, key_element in enumerate(key_elements):
            if i == len(key_elements) - 1:
                # add value to this element
                if key_element not in state:
                    return None
                return state[key_element]
            if key_element not in state:
                state[key_element] = {}
            state = state[key_element]
        return None

    def _store_value(self, key: str, value: Any) -> None:
        return self._store_value_in_state(
            self._session_state[self._session_input_key], key, value
        )

    def _get_value(self, key: str) -> Any:
        return self._get_value_from_state(
            self._session_state[self._session_input_key], key
        )

    def _render_single_datetime_input(
        self, streamlit_app: Any, key: str, property: Dict
    ) -> Any:
        streamlit_kwargs = self._get_default_streamlit_input_kwargs(key, property)
        overwrite_kwargs = self._get_overwrite_streamlit_kwargs(key, property)

        if property.get("format") == "time":
            if property.get("init_value"):
                streamlit_kwargs["value"] = property.get("init_value")
            elif property.get("default"):
                with contextlib.suppress(Exception):
                    streamlit_kwargs["value"] = datetime.time.fromisoformat(  # type: ignore
                        property["default"]
                    )
            return streamlit_app.time_input(**{**streamlit_kwargs, **overwrite_kwargs})
        elif property.get("format") == "date":
            if property.get("init_value"):
                streamlit_kwargs["value"] = property.get("init_value")
            elif property.get("default"):
                with contextlib.suppress(Exception):
                    streamlit_kwargs["value"] = datetime.date.fromisoformat(  # type: ignore
                        property["default"]
                    )
            return streamlit_app.date_input(**{**streamlit_kwargs, **overwrite_kwargs})
        elif property.get("format") == "date-time":
            if property.get("init_value"):
                streamlit_kwargs["value"] = property.get("init_value")
            elif property.get("default"):
                with contextlib.suppress(Exception):
                    streamlit_kwargs["value"] = datetime.datetime.fromisoformat(  # type: ignore
                        property["default"]
                    )
            with self._streamlit_container.container():
                if not property.get("is_item"):
                    self._streamlit_container.subheader(streamlit_kwargs.get("label"))
                if streamlit_kwargs.get("description"):
                    self._streamlit_container.text(streamlit_kwargs.get("description"))
                selected_date = None
                selected_time = None

                # columns can not be used within a collection
                if property.get("is_item"):
                    date_col = self._streamlit_container.container()
                    time_col = self._streamlit_container.container()
                else:
                    date_col, time_col = self._streamlit_container.columns(2)
                with date_col:
                    date_kwargs = {**{**streamlit_kwargs, **overwrite_kwargs}}
                    date_kwargs["label"] = "Date"
                    date_kwargs["key"] = (f"{streamlit_kwargs.get('key')}-date-input",)

                    value = streamlit_kwargs.get("value")
                    if value:
                        with contextlib.suppress(Exception):
                            date_kwargs["value"] = value.date()
                    selected_date = self._streamlit_container.date_input(**date_kwargs)

                with time_col:
                    time_kwargs = {**{**streamlit_kwargs, **overwrite_kwargs}}
                    time_kwargs["label"] = "Time"
                    time_kwargs["key"] = f"{streamlit_kwargs.get('key')}-time-input"

                    value = streamlit_kwargs.get("value")
                    if value:
                        with contextlib.suppress(Exception):
                            time_kwargs["value"] = value.time()
                    selected_time = self._streamlit_container.time_input(**time_kwargs)

                return datetime.datetime.combine(selected_date, selected_time)
        else:
            streamlit_app.warning(
                "Date format is not supported: " + str(property.get("format"))
            )

    def _render_single_file_input(
        self, streamlit_app: Any, key: str, property: Dict
    ) -> Any:
        streamlit_kwargs = self._get_default_streamlit_input_kwargs(key, property)
        overwrite_kwargs = self._get_overwrite_streamlit_kwargs(key, property)

        file_extension = None
        if "mime_type" in property:
            file_extension = mimetypes.guess_extension(property["mime_type"])

        uploaded_file = streamlit_app.file_uploader(
            **{
                **streamlit_kwargs,
                "accept_multiple_files": False,
                "type": file_extension,
                **overwrite_kwargs,
            }
        )
        if uploaded_file is None:
            return b""

        file_bytes = uploaded_file.getvalue()
        if getattr(uploaded_file, "type"):
            if _is_compatible_audio(uploaded_file.type):
                # Show audio
                streamlit_app.audio(file_bytes, format=uploaded_file.type)
            if _is_compatible_image(uploaded_file.type):
                # Show image
                streamlit_app.image(file_bytes)
            if _is_compatible_video(uploaded_file.type):
                # Show video
                streamlit_app.video(file_bytes, format=uploaded_file.type)
        return base64.urlsafe_b64encode(file_bytes)

    def _render_single_string_input(
        self, streamlit_app: Any, key: str, property: Dict
    ) -> Any:
        streamlit_kwargs = self._get_default_streamlit_input_kwargs(key, property)
        overwrite_kwargs = self._get_overwrite_streamlit_kwargs(key, property)
        if property.get("init_value"):
            streamlit_kwargs["value"] = property.get("init_value")
        elif property.get("default"):
            streamlit_kwargs["value"] = property.get("default")
        elif property.get("example"):
            # TODO: also use example for other property types
            # Use example as value if it is provided
            streamlit_kwargs["value"] = property.get("example")

        if property.get("maxLength") is not None:
            streamlit_kwargs["max_chars"] = property.get("maxLength")

        if property.get("readOnly"):
            # Read only property -> only show value
            streamlit_kwargs["disabled"] = property.get("readOnly", False)

        if property.get("format") == "multi-line" and not property.get("writeOnly"):
            # Use text area if format is multi-line (custom definition)
            return streamlit_app.text_area(**{**streamlit_kwargs, **overwrite_kwargs})
        else:
            # Use text input for most situations
            if property.get("writeOnly"):
                streamlit_kwargs["type"] = "password"
            return streamlit_app.text_input(**{**streamlit_kwargs, **overwrite_kwargs})

    def _render_single_color_input(
        self, streamlit_app: Any, key: str, property: Dict
    ) -> Any:
        streamlit_kwargs = self._get_default_streamlit_input_kwargs(key, property)
        overwrite_kwargs = self._get_overwrite_streamlit_kwargs(key, property)
        if property.get("init_value") is not None:
            streamlit_kwargs["value"] = property["init_value"]
        elif property.get("default") is not None:
            streamlit_kwargs["value"] = property["default"]
        elif property.get("example") is not None:
            streamlit_kwargs["value"] = property["example"]

        if isinstance(streamlit_kwargs.get("value"), Color):
            streamlit_kwargs["value"] = streamlit_kwargs["value"].as_hex()
        elif isinstance(streamlit_kwargs.get("value"), str):
            streamlit_kwargs["value"] = Color(streamlit_kwargs["value"]).as_hex()

        if property.get("format") == "text":
            # Use text input if specified format is text
            return streamlit_app.text_input(**{**streamlit_kwargs, **overwrite_kwargs})
        else:
            # Use color picker input for most situations
            return streamlit_app.color_picker(
                **{**streamlit_kwargs, **overwrite_kwargs}
            )

    def _render_multi_enum_input(
        self, streamlit_app: Any, key: str, property: Dict
    ) -> Any:
        streamlit_kwargs = self._get_default_streamlit_input_kwargs(key, property)
        overwrite_kwargs = self._get_overwrite_streamlit_kwargs(key, property)

        select_options: List[str] = []
        if property.get("items").get("enum"):  # type: ignore
            # Using Literal
            select_options = property.get("items").get("enum")  # type: ignore
        else:
            # Using Enum
            reference_item = schema_utils.resolve_reference(
                property["items"]["$ref"], self._schema_references
            )
            select_options = reference_item["enum"]

        if property.get("init_value"):
            streamlit_kwargs["default"] = property.get("init_value")
        elif property.get("default"):
            try:
                streamlit_kwargs["default"] = property.get("default")
            except Exception:
                pass

        return streamlit_app.multiselect(
            **{**streamlit_kwargs, "options": select_options, **overwrite_kwargs}
        )

    def _render_single_enum_input(
        self, streamlit_app: Any, key: str, property: Dict
    ) -> Any:
        streamlit_kwargs = self._get_default_streamlit_input_kwargs(key, property)
        overwrite_kwargs = self._get_overwrite_streamlit_kwargs(key, property)

        select_options: List[str] = []
        if property.get("enum"):
            select_options = property.get("enum")  # type: ignore
        else:
            reference_item = schema_utils.get_single_reference_item(
                property, self._schema_references
            )
            select_options = reference_item["enum"]

        if property.get("init_value"):
            streamlit_kwargs["index"] = select_options.index(
                property.get("init_value")  # type: ignore
            )
        elif property.get("default") is not None:
            try:
                streamlit_kwargs["index"] = select_options.index(
                    property.get("default")  # type: ignore
                )
            except Exception:
                # Use default selection
                pass

        # if there is only one option then there is no choice for the user to be make
        # so simply return the value (This is relevant for discriminator properties)
        if len(select_options) == 1:
            return select_options[0]
        else:
            return streamlit_app.selectbox(
                **{**streamlit_kwargs, "options": select_options, **overwrite_kwargs}
            )

    def _render_single_dict_input(
        self, streamlit_app: Any, key: str, property: Dict
    ) -> Any:
        # Add title and subheader
        streamlit_app.subheader(property.get("title"))
        if property.get("description"):
            streamlit_app.markdown(property.get("description"))

        if self._get_value(key) is not None or self._get_value(key) == {}:
            data_dict = self._get_value(key)
        elif property.get("init_value"):
            data_dict = property.get("init_value")
        elif property.get("default"):
            data_dict = property.get("default")
        else:
            data_dict = {}

        is_object = True if property["additionalProperties"].get("$ref") else False

        add_col, clear_col, _ = streamlit_app.columns(3)

        add_col = add_col.empty()

        if self._clear_button_allowed(property):
            data_dict = self._render_dict_add_button(key, add_col, data_dict)

        if self._clear_button_allowed(property):
            data_dict = self._render_dict_clear_button(key, clear_col, data_dict)

        new_dict = {}

        for index, input_item in enumerate(data_dict.items()):
            updated_key, updated_value = self._render_dict_item(
                streamlit_app,
                key,
                input_item,
                index,
                property,
            )

            if updated_key is not None and updated_value is not None:
                new_dict[updated_key] = updated_value

            if is_object:
                streamlit_app.markdown("---")

        if not is_object:
            streamlit_app.markdown("---")

        return new_dict

    def _render_single_reference(
        self, streamlit_app: Any, key: str, property: Dict
    ) -> Any:
        reference_item = schema_utils.get_single_reference_item(
            property, self._schema_references
        )
        return self._render_property(streamlit_app, key, reference_item)

    def _render_union_property(
        self, streamlit_app: Any, key: str, property: Dict
    ) -> Any:
        streamlit_kwargs = self._get_default_streamlit_input_kwargs(key, property)

        reference_items = schema_utils.get_union_references(
            property, self._schema_references
        )

        # special handling when there are instance values and a discriminator property
        # to differentiate between object types
        if property.get("init_value") and property.get("discriminator"):
            disc_prop = property["discriminator"]["propertyName"]
            # find the index where the discriminator is equal to the init_value
            ref_index = next(
                i
                for i, x in enumerate(reference_items)
                if x["properties"][disc_prop]["enum"]
                == [property["init_value"][disc_prop]]
            )

            # add any init_value properties to the corresponding reference item
            reference_items[ref_index]["init_value"] = property["init_value"]
            streamlit_kwargs["index"] = ref_index
        elif property.get("init_value") and property.get("instance_class"):
            ref_index = next(
                i
                for i, x in enumerate(reference_items)
                if x["title"] in property["instance_class"]
            )
            reference_items[ref_index]["init_value"] = property["init_value"]
            streamlit_kwargs["index"] = ref_index

        name_reference_mapping: Dict[str, Dict] = {}

        for reference in reference_items:
            reference_title = _name_to_title(reference["title"])
            name_reference_mapping[reference_title] = reference

        streamlit_app.subheader(streamlit_kwargs["label"])  # type: ignore
        if "help" in streamlit_kwargs:
            streamlit_app.markdown(streamlit_kwargs["help"])

        selected_reference = streamlit_app.selectbox(
            **{
                **streamlit_kwargs,
                "label": streamlit_kwargs["label"] + " - Options",
                "options": name_reference_mapping.keys(),
            }
        )

        input_data = self._render_object_input(
            streamlit_app, key, name_reference_mapping[selected_reference]
        )

        streamlit_app.markdown("---")
        return input_data

    def _render_multi_file_input(
        self, streamlit_app: Any, key: str, property: Dict
    ) -> Any:
        streamlit_kwargs = self._get_default_streamlit_input_kwargs(key, property)
        overwrite_kwargs = self._get_overwrite_streamlit_kwargs(key, property)

        file_extension = None
        if "mime_type" in property:
            file_extension = mimetypes.guess_extension(property["mime_type"])

        uploaded_files = streamlit_app.file_uploader(
            **{
                **streamlit_kwargs,
                "accept_multiple_files": True,
                "type": file_extension,
                **overwrite_kwargs,
            }
        )
        uploaded_files_bytes = []
        if uploaded_files:
            for uploaded_file in uploaded_files:
                uploaded_files_bytes.append(uploaded_file.read())
        return uploaded_files_bytes

    def _render_single_boolean_input(
        self, streamlit_app: Any, key: str, property: Dict
    ) -> Any:
        streamlit_kwargs = self._get_default_streamlit_input_kwargs(key, property)
        overwrite_kwargs = self._get_overwrite_streamlit_kwargs(key, property)

        if "init_value" in property:
            streamlit_kwargs["value"] = property.get("init_value")
        elif "default" in property:
            streamlit_kwargs["value"] = property.get("default")

        # special formatting when rendering within a list/dict
        if property.get("is_item"):
            streamlit_app.markdown("##")

        return streamlit_app.checkbox(**{**streamlit_kwargs, **overwrite_kwargs})

    def _render_single_number_input(
        self, streamlit_app: Any, key: str, property: Dict
    ) -> Any:
        streamlit_kwargs = self._get_default_streamlit_input_kwargs(key, property)
        overwrite_kwargs = self._get_overwrite_streamlit_kwargs(key, property)

        number_transform = int
        if property.get("type") == "number":
            number_transform = float  # type: ignore
            streamlit_kwargs["format"] = "%f"

        if "multipleOf" in property:
            # Set stepcount based on multiple of parameter
            streamlit_kwargs["step"] = number_transform(property["multipleOf"])
        elif number_transform == int:
            # Set step size to 1 as default
            streamlit_kwargs["step"] = 1
        elif number_transform == float:
            # Set step size to 0.01 as default
            # TODO: adapt to default value
            streamlit_kwargs["step"] = 0.01

        if "minimum" in property:
            streamlit_kwargs["min_value"] = number_transform(property["minimum"])
        if "exclusiveMinimum" in property:
            streamlit_kwargs["min_value"] = number_transform(
                property["exclusiveMinimum"] + streamlit_kwargs["step"]
            )
        if "maximum" in property:
            streamlit_kwargs["max_value"] = number_transform(property["maximum"])

        if "exclusiveMaximum" in property:
            streamlit_kwargs["max_value"] = number_transform(
                property["exclusiveMaximum"] - streamlit_kwargs["step"]
            )

        if property.get("init_value") is not None:
            streamlit_kwargs["value"] = number_transform(property["init_value"])
        elif property.get("default") is not None:
            streamlit_kwargs["value"] = number_transform(property["default"])  # type: ignore
        else:
            if "min_value" in streamlit_kwargs:
                streamlit_kwargs["value"] = streamlit_kwargs["min_value"]
            elif number_transform == int:
                streamlit_kwargs["value"] = 0
            else:
                # Set default value to step
                streamlit_kwargs["value"] = number_transform(
                    streamlit_kwargs["step"]
                )

        if "min_value" in streamlit_kwargs and "max_value" in streamlit_kwargs:
            # TODO: Only if less than X steps
            return streamlit_app.slider(**{**streamlit_kwargs, **overwrite_kwargs})
        else:
            return streamlit_app.number_input(
                **{**streamlit_kwargs, **overwrite_kwargs}
            )

    def _render_object_input(self, streamlit_app: Any, key: str, property: Dict) -> Any:
        properties = property["properties"]
        object_inputs = {}
        for property_key in properties:
            new_property = properties[property_key]
            if not new_property.get("title"):
                # Set property key as fallback title
                new_property["title"] = _name_to_title(property_key)
            # construct full key based on key parts -> required later to get the value
            full_key = key + "." + property_key

            if property.get("init_value"):
                new_property["init_value"] = property["init_value"].get(property_key)
            if property.get("default"):
                new_property["default"] = property["default"].get(property_key)

            new_property["readOnly"] = property.get("readOnly", False)

            value = self._render_property(streamlit_app, full_key, new_property)
            if not self._is_value_ignored(property_key, value):
                object_inputs[property_key] = value

        return object_inputs

    def _render_single_object_input(
        self, streamlit_app: Any, key: str, property: Dict
    ) -> Any:
        # Add title and subheader
        title = property.get("title")
        if property.get("is_item"):
            streamlit_app.caption(title)
        else:
            streamlit_app.subheader(title)
        if property.get("description"):
            streamlit_app.markdown(property.get("description"))

        object_reference = schema_utils.get_single_reference_item(
            property, self._schema_references
        )

        object_reference["init_value"] = property.get("init_value", None)

        object_reference["default"] = property.get("default", None)

        object_reference["readOnly"] = property.get("readOnly", None)

        return self._render_object_input(streamlit_app, key, object_reference)

    def _render_list_item(
        self,
        streamlit_app: Any,
        parent_key: str,
        value: Any,
        index: int,
        property: Dict[str, Any],
    ) -> Any:
        label = "Item #" + str(index + 1)
        new_key = self._key + "-" + parent_key + "." + str(index)
        item_placeholder = streamlit_app.empty()

        with item_placeholder:
            input_col, button_col = streamlit_app.columns([8, 3])

            button_col.markdown("##")

            if self._remove_button_allowed(index, property):
                remove = False
            else:
                remove = button_col.button("Remove", key=new_key + "-remove")

            #  insert an input field when the remove button has not been clicked
            if not remove:
                with input_col:
                    new_property = {
                        "title": label,
                        "init_value": value if value else None,
                        "is_item": True,
                        "readOnly": property.get("readOnly"),
                        **property["items"],
                    }
                    return self._render_property(streamlit_app, new_key, new_property)

            else:
                # when the remove button is clicked clear the placeholder and return None
                item_placeholder.empty()
                return None

    def _render_dict_item(
        self,
        streamlit_app: Any,
        parent_key: str,
        in_value: Tuple[str, Any],
        index: int,
        property: Dict[str, Any],
    ) -> Any:
        new_key = self._key + "-" + parent_key + "." + str(index)
        item_placeholder = streamlit_app.empty()

        with item_placeholder.container():
            key_col, value_col, button_col = streamlit_app.columns([4, 4, 3])

            dict_key = in_value[0]
            dict_value = in_value[1]

            dict_key_key = new_key + "-key"
            dict_value_key = new_key + "-value"

            button_col.markdown("##")

            if self._remove_button_allowed(index, property):
                remove = False
            else:
                remove = button_col.button("Remove", key=new_key + "-remove")

            if not remove:
                with key_col:
                    updated_key = streamlit_app.text_input(
                        "Key",
                        value=dict_key,
                        key=dict_key_key,
                        disabled=property.get("readOnly", False),
                    )

                with value_col:
                    new_property = {
                        "title": "Value",
                        "init_value": dict_value,
                        "is_item": True,
                        "readOnly": property.get("readOnly"),
                        **property["additionalProperties"],
                    }
                    with value_col:
                        updated_value = self._render_property(
                            streamlit_app, dict_value_key, new_property
                        )

                    return updated_key, updated_value

            else:
                # when the remove button is clicked clear the placeholder and return None
                item_placeholder.empty()
                return None, None

    def _add_button_allowed(
        self,
        index: int,
        property: Dict[str, Any],
    ) -> bool:
        add_allowed = not (
            (property.get("readOnly", False) is True)
            or ((index) >= property.get("maxItems", 1000))
        )

        return add_allowed

    def _remove_button_allowed(
        self,
        index: int,
        property: Dict[str, Any],
    ) -> bool:
        remove_allowed = (property.get("readOnly") is True) or (
            (index + 1) <= property.get("minItems", 0)
        )

        return remove_allowed

    def _clear_button_allowed(
        self,
        property: Dict[str, Any],
    ) -> bool:
        clear_allowed = not (
            (property.get("readOnly", False) is True)
            or (property.get("minItems", 0) > 0)
        )

        return clear_allowed

    def _render_list_add_button(
        self,
        key: str,
        streamlit_app: Any,
        data_list: List[Any],
    ) -> List[Any]:
        if streamlit_app.button(
            "Add Item",
            key=self._key + "-" + key + "list-add-item",
        ):
            data_list.append(None)

        return data_list

    def _render_list_clear_button(
        self,
        key: str,
        streamlit_app: Any,
        data_list: List[Any],
    ) -> List[Any]:
        if streamlit_app.button(
            "Clear All",
            key=self._key + "_" + key + "-list_clear-all",
        ):
            data_list = []

        return data_list

    def _render_dict_add_button(
        self, key: str, streamlit_app: Any, data_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        if streamlit_app.button(
            "Add Item",
            key=self._key + "-" + key + "-add-item",
        ):
            data_dict[str(len(data_dict) + 1)] = None

        return data_dict

    def _render_dict_clear_button(
        self,
        key: str,
        streamlit_app: Any,
        data_dict: Dict[str, Any],
    ) -> Dict[str, Any]:
        if streamlit_app.button(
            "Clear All",
            key=self._key + "-" + key + "-clear-all",
        ):
            data_dict = {}

        return data_dict

    def _render_list_input(self, streamlit_app: Any, key: str, property: Dict) -> Any:
        # Add title and subheader
        streamlit_app.subheader(property.get("title"))
        if property.get("description"):
            streamlit_app.markdown(property.get("description"))

        is_object = True if property["items"].get("$ref") else False

        object_list = []

        # Treat empty list as a session data "hit"
        if self._get_value(key) is not None or self._get_value(key) == []:
            data_list = self._get_value(key)
        elif property.get("init_value"):
            data_list = property.get("init_value")
        elif property.get("default"):
            data_list = property.get("default")
        else:
            data_list = []

        add_col, clear_col, _ = streamlit_app.columns(3)

        add_col = add_col.empty()

        self._render_list_add_button(key, add_col, data_list)

        if self._clear_button_allowed(property):
            data_list = self._render_list_clear_button(key, clear_col, data_list)

        if len(data_list) > 0:
            for index, item in enumerate(data_list):
                output = self._render_list_item(
                    streamlit_app,
                    key,
                    item,
                    index,
                    property,
                )
                if output is not None:
                    object_list.append(output)

                if is_object:
                    streamlit_app.markdown("---")

            if not self._add_button_allowed(len(object_list), property):
                add_col = add_col.empty()

            if not is_object:
                streamlit_app.markdown("---")

        return object_list

    def _render_property(self, streamlit_app: Any, key: str, property: Dict) -> Any:
        if schema_utils.is_single_enum_property(property, self._schema_references):
            return self._render_single_enum_input(streamlit_app, key, property)

        if schema_utils.is_multi_enum_property(property, self._schema_references):
            return self._render_multi_enum_input(streamlit_app, key, property)

        if schema_utils.is_single_file_property(property):
            return self._render_single_file_input(streamlit_app, key, property)

        if schema_utils.is_multi_file_property(property):
            return self._render_multi_file_input(streamlit_app, key, property)

        if schema_utils.is_single_datetime_property(property):
            return self._render_single_datetime_input(streamlit_app, key, property)

        if schema_utils.is_single_color_property(property):
            return self._render_single_color_input(streamlit_app, key, property)

        if schema_utils.is_single_boolean_property(property):
            return self._render_single_boolean_input(streamlit_app, key, property)

        if schema_utils.is_single_dict_property(property):
            return self._render_single_dict_input(streamlit_app, key, property)

        if schema_utils.is_single_number_property(property):
            return self._render_single_number_input(streamlit_app, key, property)

        if schema_utils.is_single_string_property(property):
            return self._render_single_string_input(streamlit_app, key, property)

        if schema_utils.is_single_object(property, self._schema_references):
            return self._render_single_object_input(streamlit_app, key, property)

        if schema_utils.is_object_list_property(property, self._schema_references):
            return self._render_list_input(streamlit_app, key, property)

        if schema_utils.is_property_list(property):
            return self._render_list_input(streamlit_app, key, property)

        if schema_utils.is_single_reference(property):
            return self._render_single_reference(streamlit_app, key, property)

        if schema_utils.is_union_property(property):
            return self._render_union_property(streamlit_app, key, property)

        streamlit_app.warning(
            "The type of the following property is currently not supported: "
            + str(property.get("title"))
        )
        raise Exception("Unsupported property")


class OutputUI:
    """Output UI renderer.

    lazydocs: ignore
    """

    def __init__(self, output_data: Any, input_data: Optional[Any] = None):
        self._output_data = output_data
        self._input_data = input_data

    def render_ui(self) -> None:
        try:
            if isinstance(self._output_data, BaseModel):
                self._render_single_output(st, self._output_data)
                return
            if type(self._output_data) == list:
                self._render_list_output(st, self._output_data)
                return
        except Exception as ex:
            st.exception(ex)
            # TODO: Fallback to
            # st.json(jsonable_encoder(self._output_data))

    def _render_single_text_property(
        self, streamlit: Any, property_schema: Dict, value: Any
    ) -> None:
        # Add title and subheader
        streamlit.subheader(property_schema.get("title"))
        if property_schema.get("description"):
            streamlit.markdown(property_schema.get("description"))
        if value is None or value == "":
            streamlit.info("No value returned!")
        else:
            streamlit.code(str(value), language="plain")

    def _render_single_file_property(
        self, streamlit: Any, property_schema: Dict, value: Any
    ) -> None:
        # Add title and subheader
        streamlit.subheader(property_schema.get("title"))
        if property_schema.get("description"):
            streamlit.markdown(property_schema.get("description"))
        if value is None or len(value) == 0:
            streamlit.info("No value returned!")
        else:
            # TODO: detect if it is base64
            file_extension = ""
            if "mime_type" in property_schema:
                mime_type = property_schema["mime_type"]
                file_extension = mimetypes.guess_extension(mime_type) or ""

                if _is_compatible_audio(mime_type):
                    streamlit.audio(value, format=mime_type)
                    return

                if _is_compatible_image(mime_type):
                    streamlit.image(value)
                    return

                if _is_compatible_video(mime_type):
                    streamlit.video(value, format=mime_type)
                    return

            filename = (
                (property_schema["title"] + file_extension)
                .lower()
                .strip()
                .replace(" ", "-")
            )
            st.download_button("Download File", value, file_name=filename)

    def _render_single_complex_property(
        self, streamlit: Any, property_schema: Dict, value: Any
    ) -> None:
        # Add title and subheader
        streamlit.subheader(property_schema.get("title"))
        if property_schema.get("description"):
            streamlit.markdown(property_schema.get("description"))

        streamlit.json(json.dumps(value, default=_pydantic_encoder))

    def _render_single_output(self, streamlit: Any, output_data: BaseModel) -> None:
        try:
            if _has_output_ui_renderer(output_data):
                if _function_has_named_arg(output_data.render_output_ui, "input"):  # type: ignore
                    # render method also requests the input data
                    output_data.render_output_ui(streamlit, input=self._input_data)  # type: ignore
                else:
                    output_data.render_output_ui(streamlit)  # type: ignore
                return
        except Exception:
            # TODO
            pass
            # Use default auto-generation methods if the custom rendering throws an exception
            # logger.exception(
            #    "Failed to execute custom render_output_ui function. Using auto-generation instead"
            # )

        model_schema = output_data.model_json_schema(by_alias=False)
        model_properties = model_schema.get("properties")
        definitions = model_schema.get("$defs")

        if model_properties:
            for property_key in output_data.__dict__:
                property_schema = model_properties.get(property_key)
                if not property_schema.get("title"):
                    # Set property key as fallback title
                    property_schema["title"] = property_key

                output_property_value = output_data.__dict__[property_key]

                if _has_output_ui_renderer(output_property_value):
                    output_property_value.render_output_ui(streamlit)  # type: ignore
                    continue

                if isinstance(output_property_value, BaseModel):
                    # Render output recursivly
                    streamlit.subheader(property_schema.get("title"))
                    if property_schema.get("description"):
                        streamlit.markdown(property_schema.get("description"))
                    self._render_single_output(streamlit, output_property_value)
                    continue

                if property_schema:
                    if schema_utils.is_multi_file_property(property_schema):
                        for file in output_property_value:
                            self._render_single_file_property(
                                streamlit, property_schema, file
                            )
                        continue

                    if schema_utils.is_single_file_property(property_schema):
                        self._render_single_file_property(
                            streamlit, property_schema, output_property_value
                        )
                        continue

                    if (
                        schema_utils.is_single_string_property(property_schema)
                        or schema_utils.is_single_number_property(property_schema)
                        or schema_utils.is_single_datetime_property(property_schema)
                        or schema_utils.is_single_boolean_property(property_schema)
                    ):
                        self._render_single_text_property(
                            streamlit, property_schema, output_property_value
                        )
                        continue
                    if definitions and schema_utils.is_single_enum_property(
                        property_schema, definitions
                    ):
                        self._render_single_text_property(
                            streamlit, property_schema, output_property_value.value
                        )
                        continue

                    if isinstance(output_property_value, (set, dict, tuple)):
                        self._render_single_text_property(
                            streamlit, property_schema, output_property_value
                        )
                        continue

                    # TODO: render dict as table

                    self._render_single_complex_property(
                        streamlit, property_schema, output_property_value
                    )
            return

        # Display single field in code block:
        # if len(output_data.__dict__) == 1:
        #     value = next(iter(output_data.__dict__.values()))

        #     if type(value) in (int, float, str):
        #         # Should not be a complex object (with __dict__) -> should be a primitive
        #         # hasattr(output_data.__dict__[0], '__dict__')
        #         streamlit.subheader("This is a test:")
        #         streamlit.code(value, language="plain")
        #         return

        st.error("Cannot render output")
        # TODO: Fallback to json output
        # streamlit.json(jsonable_encoder(output_data))

    def _render_list_output(self, streamlit: Any, output_data: List) -> None:
        try:
            data_items: List = []
            for data_item in output_data:
                if _has_output_ui_renderer(data_item):
                    # Render using the render function
                    data_item.render_output_ui(streamlit)  # type: ignore
                    continue
                data_items.append(data_item.model_dump())
            # Try to show as dataframe
            streamlit.table(pd.DataFrame(data_items))
        except Exception:
            st.error("Cannot render output list")
            # TODO Fallback to
            # streamlit.json(jsonable_encoder(output_data))


def pydantic_input(
    key: str,
    model: Type[BaseModel],
    group_optional_fields: GroupOptionalFieldsStrategy = "no",  # type: ignore
    lowercase_labels: bool = False,
    ignore_empty_values: bool = False,
) -> Dict:
    """Auto-generates input UI elements for a selected Pydantic class.

    Args:
        key (str): A string that identifies the form. Each form must have its own key.
        model (Type[BaseModel]): The input model. Either a class or instance based on Pydantic `BaseModel` or Python `dataclass`.
        group_optional_fields (str, optional): If `sidebar`, optional input elements will be rendered on the sidebar.
            If `expander`,  optional input elements will be rendered inside an expander element. Defaults to `no`.
        lowercase_labels (bool): If `True`, all input element labels will be lowercased. Defaults to `False`.
        ignore_empty_values (bool): If `True`, empty values for strings and numbers will not be stored in the session state. Defaults to `False`.

    Returns:
        Dict: A dictionary with the current state of the input data.
    """
    return InputUI(
        key,
        model,
        group_optional_fields=group_optional_fields,
        lowercase_labels=lowercase_labels,
        ignore_empty_values=ignore_empty_values,
        return_model=False,
    ).render_ui()


def pydantic_output(output_data: Any) -> None:
    """Auto-generates output UI elements for all properties of a (Pydantic-based) model instance.

    Args:
        output_data (Any): The output data.
    """

    OutputUI(output_data).render_ui()


# Define generic type to allow autocompletion for the model fields
T = TypeVar("T", bound=BaseModel)


def pydantic_form(
    key: str,
    model: Type[T],
    submit_label: str = "Submit",
    clear_on_submit: bool = False,
    group_optional_fields: GroupOptionalFieldsStrategy = "no",  # type: ignore
    lowercase_labels: bool = False,
    ignore_empty_values: bool = False,
) -> Optional[T]:
    """Auto-generates a Streamlit form based on the given (Pydantic-based) input class.

    Args:
        key (str): A string that identifies the form. Each form must have its own key.
        model (Type[BaseModel]): The input model. Either a class or instance based on Pydantic `BaseModel` or Python `dataclass`.
        submit_label (str): A short label explaining to the user what this button is for. Defaults to “Submit”.
        clear_on_submit (bool): If True, all widgets inside the form will be reset to their default values after the user presses the Submit button. Defaults to False.
        group_optional_fields (str, optional): If `sidebar`, optional input elements will be rendered on the sidebar.
            If `expander`,  optional input elements will be rendered inside an expander element. Defaults to `no`.
        lowercase_labels (bool): If `True`, all input element labels will be lowercased. Defaults to `False`.
        ignore_empty_values (bool): If `True`, empty values for strings and numbers will not be stored in the session state. Defaults to `False`.

    Returns:
        Optional[BaseModel]: An instance of the given input class,
            if the submit button is used and the input data passes the Pydantic validation.
    """

    with st.form(key=key, clear_on_submit=clear_on_submit):
        input_state = InputUI(
            key,
            model,
            group_optional_fields=group_optional_fields,
            lowercase_labels=lowercase_labels,
            ignore_empty_values=ignore_empty_values,
            return_model=True,
        ).render_ui()

        if st.form_submit_button(label=submit_label):
            return input_state  # type: ignore
    return None
