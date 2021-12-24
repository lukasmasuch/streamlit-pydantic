import dataclasses
import datetime
import inspect
import json
import mimetypes
import re
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

import pandas as pd
import streamlit as st
from pydantic import BaseModel, ValidationError, parse_obj_as
from pydantic.json import pydantic_encoder

from streamlit_pydantic import schema_utils

OVERWRITE_STREAMLIT_KWARGS_PREFIX = "st_kwargs_"


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
    ):
        self._key = key

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
            # Convert dataclasses
            import pydantic

            self._input_class = pydantic.dataclasses.dataclass(model).__pydantic_model__  # type: ignore
        else:
            self._input_class = model

        self._schema_properties = self._input_class.schema(by_alias=True).get(
            "properties", {}
        )
        self._schema_references = self._input_class.schema(by_alias=True).get(
            "definitions", {}
        )

        # TODO: check if state has input data

    def render_ui(self) -> Dict:
        if _has_input_ui_renderer(self._input_class):
            # The input model has a rendering function
            # The rendering also returns the current state of input data
            self._session_state[self._session_input_key] = self._input_class.render_input_ui(  # type: ignore
                self._streamlit_container, self._session_state[self._session_input_key]
            ).dict()
            return self._session_state[self._session_input_key]

        required_properties = self._input_class.schema(by_alias=True).get(
            "required", []
        )

        properties_in_expander = []

        for property_key in self._schema_properties.keys():
            streamlit_app = self._streamlit_container
            if property_key not in required_properties:
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

            # check if the input_class is an instance
            if isinstance(self._input_class, BaseModel):
                instance_value = self._input_class.dict().get(property_key)
                if instance_value in [None, ""]:
                    instance_value = self._input_class.dict(by_alias=True).get(
                        property_key
                    )
                if instance_value not in [None, ""]:
                    property["init_value"] = instance_value

            try:
                value = self._render_property(streamlit_app, property_key, property)
                if not self._is_value_ignored(property_key, value):
                    self._store_value(property_key, value)
            except Exception as e:
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

        return self._session_state[self._session_input_key]

    def _get_overwrite_streamlit_kwargs(self, key: str, property: Dict) -> Dict:

        streamlit_kwargs: Dict = {}

        for kwarg in property:
            if kwarg.startswith(OVERWRITE_STREAMLIT_KWARGS_PREFIX):
                streamlit_kwargs[
                    kwarg.replace(OVERWRITE_STREAMLIT_KWARGS_PREFIX, "")
                ] = property[kwarg]
        return streamlit_kwargs

    def _get_default_streamlit_input_kwargs(self, key: str, property: Dict) -> Dict:
        label = property.get("title")
        if label and self._lowercase_labels:
            label = label.lower()

        streamlit_kwargs = {
            "label": label,
            "key": str(self._session_state.run_id) + "-" + str(self._key) + "-" + key,
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
                try:
                    streamlit_kwargs["value"] = datetime.time.fromisoformat(  # type: ignore
                        property.get("default")
                    )
                except Exception:
                    pass
            return streamlit_app.time_input(**{**streamlit_kwargs, **overwrite_kwargs})
        elif property.get("format") == "date":
            if property.get("init_value"):
                streamlit_kwargs["value"] = property.get("init_value")
            elif property.get("default"):
                try:
                    streamlit_kwargs["value"] = datetime.date.fromisoformat(  # type: ignore
                        property.get("default")
                    )
                except Exception:
                    pass
            return streamlit_app.date_input(**{**streamlit_kwargs, **overwrite_kwargs})
        elif property.get("format") == "date-time":
            if property.get("init_value"):
                streamlit_kwargs["value"] = property.get("init_value")
            elif property.get("default"):
                try:
                    streamlit_kwargs["value"] = datetime.datetime.fromisoformat(  # type: ignore
                        property.get("default")
                    )
                except Exception:
                    pass
            with self._streamlit_container.container():
                self._streamlit_container.subheader(streamlit_kwargs.get("label"))
                if streamlit_kwargs.get("description"):
                    self._streamlit_container.text(streamlit_kwargs.get("description"))
                selected_date = None
                selected_time = None
                date_col, time_col = self._streamlit_container.columns(2)
                with date_col:
                    date_kwargs = {"label": "Date", "key": key + "-date-input"}
                    if streamlit_kwargs.get("value"):
                        try:
                            date_kwargs["value"] = streamlit_kwargs.get(  # type: ignore
                                "value"
                            ).date()
                        except Exception:
                            pass
                    selected_date = self._streamlit_container.date_input(**date_kwargs)

                with time_col:
                    time_kwargs = {"label": "Time", "key": key + "-time-input"}
                    if streamlit_kwargs.get("value"):
                        try:
                            time_kwargs["value"] = streamlit_kwargs.get(  # type: ignore
                                "value"
                            ).time()
                        except Exception:
                            pass
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
            return None

        bytes = uploaded_file.getvalue()
        if property.get("mime_type"):
            if _is_compatible_audio(property["mime_type"]):
                # Show audio
                streamlit_app.audio(bytes, format=property.get("mime_type"))
            if _is_compatible_image(property["mime_type"]):
                # Show image
                streamlit_app.image(bytes)
            if _is_compatible_video(property["mime_type"]):
                # Show video
                streamlit_app.video(bytes, format=property.get("mime_type"))
        return bytes

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
            streamlit_app.code(streamlit_kwargs["value"])
            return streamlit_kwargs["value"]

        if property.get("format") == "multi-line" and not property.get("writeOnly"):
            # Use text area if format is multi-line (custom definition)
            return streamlit_app.text_area(**{**streamlit_kwargs, **overwrite_kwargs})
        else:
            # Use text input for most situations
            if property.get("writeOnly"):
                streamlit_kwargs["type"] = "password"
            return streamlit_app.text_input(**{**streamlit_kwargs, **overwrite_kwargs})

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

        streamlit_app.markdown("---")

        current_dict = self._get_value(key)
        if not current_dict:
            current_dict = {}

        key_col, value_col = streamlit_app.columns(2)

        with key_col:
            updated_key = streamlit_app.text_input(
                "Key", value="", key=key + "-new-key"
            )

        with value_col:
            # TODO: also add boolean?
            value_kwargs = {"label": "Value", "key": key + "-new-value"}
            if property["additionalProperties"].get("type") == "integer":
                value_kwargs["value"] = 0  # type: ignore
                updated_value = streamlit_app.number_input(**value_kwargs)
            elif property["additionalProperties"].get("type") == "number":
                value_kwargs["value"] = 0.0  # type: ignore
                value_kwargs["format"] = "%f"
                updated_value = streamlit_app.number_input(**value_kwargs)
            else:
                value_kwargs["value"] = ""
                updated_value = streamlit_app.text_input(**value_kwargs)

        streamlit_app.markdown("---")

        with streamlit_app.container():
            clear_col, add_col = streamlit_app.columns([1, 2])

            with clear_col:
                if streamlit_app.button("Clear Items", key=key + "-clear-items"):
                    current_dict = {}

            with add_col:
                if (
                    streamlit_app.button("Add Item", key=key + "-add-item")
                    and updated_key
                ):
                    current_dict[updated_key] = updated_value

        streamlit_app.write(current_dict)

        return current_dict

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

        name_reference_mapping: Dict[str, Dict] = {}

        for reference in reference_items:
            reference_title = _name_to_title(reference["title"])
            name_reference_mapping[reference_title] = reference

        streamlit_app.subheader(streamlit_kwargs["label"])  # type: ignore
        if "help" in streamlit_kwargs:
            streamlit_app.markdown(streamlit_kwargs["help"])

        selected_reference = streamlit_app.selectbox(
            key=streamlit_kwargs["key"],
            label=streamlit_kwargs["label"] + " - Options",
            options=name_reference_mapping.keys(),
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

        if property.get("init_value"):
            streamlit_kwargs["value"] = property.get("init_value")
        elif property.get("default"):
            streamlit_kwargs["value"] = property.get("default")
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
            streamlit_kwargs["value"] = number_transform(property.get("init_value"))
        elif property.get("default") is not None:
            streamlit_kwargs["value"] = number_transform(property.get("default"))  # type: ignore
        else:
            if "min_value" in streamlit_kwargs:
                streamlit_kwargs["value"] = streamlit_kwargs["min_value"]
            elif number_transform == int:
                streamlit_kwargs["value"] = 0
            else:
                # Set default value to step
                streamlit_kwargs["value"] = number_transform(streamlit_kwargs["step"])

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
                new_property["init_value"] = dict(property.get("init_value")).get(
                    property_key
                )

            value = self._render_property(streamlit_app, full_key, new_property)
            if not self._is_value_ignored(property_key, value):
                object_inputs[property_key] = value
        return object_inputs

    def _render_single_object_input(
        self, streamlit_app: Any, key: str, property: Dict
    ) -> Any:
        # Add title and subheader
        title = property.get("title")
        streamlit_app.subheader(title)
        if property.get("description"):
            streamlit_app.markdown(property.get("description"))

        object_reference = schema_utils.get_single_reference_item(
            property, self._schema_references
        )

        if property.get("init_value"):
            object_reference["init_value"] = property.get("init_value")
        else:
            object_reference["init_value"] = None
        return self._render_object_input(streamlit_app, key, object_reference)

    def _render_list_item(
        self,
        streamlit_app,
        parent_key: str,
        of_type: str,
        value,
        index: int,
        object_reference=None,
    ):

        label = "Item #" + str(index + 1)
        new_key = self._key + "_" + parent_key + "." + str(index)
        item_placeholder = streamlit_app.empty()

        with item_placeholder:

            input_col, button_col = streamlit_app.columns([9, 2])

            # vertical spacers
            button_col.markdown("")
            button_col.markdown("")

            remove_click = button_col.button("Remove", key=new_key + "-remove")

            value_kwargs = {}

            #  insert an input field when the remove button has not been clicked
            if not remove_click:
                with input_col:
                    if of_type == "object":

                        new_object_reference = object_reference
                        new_object_reference["init_value"] = value if value else None
                        new_object_reference["title"] = label

                        return self._render_object_input(
                            streamlit_app, new_key, new_object_reference
                        )

                    elif of_type == "integer":
                        value_kwargs["label"] = label
                        value_kwargs["value"] = value if value else 0  # type: ignore
                        value_kwargs["key"] = new_key
                        return input_col.number_input(**value_kwargs)
                    elif of_type == "number":
                        value_kwargs["label"] = label
                        value_kwargs["value"] = value if value else 0.0  # type: ignore
                        value_kwargs["format"] = "%f"
                        value_kwargs["key"] = new_key
                        return input_col.number_input(**value_kwargs)
                    else:
                        value_kwargs["label"] = label
                        value_kwargs["value"] = value if value else ""
                        value_kwargs["key"] = new_key
                        return input_col.text_input(**value_kwargs)
            else:
                # when the remove button is clicked clear the placeholder and return None
                item_placeholder.empty()
                return None

    def _render_list_controls(
        self,
        streamlit_app,
        key: str,
        data_list: List[Any],
    ):

        _, clear_col, add_col = streamlit_app.columns([7, 2, 2])

        with clear_col:
            if streamlit_app.button(
                "Clear All", key=self._key + "_" + key + "-clear-all"
            ):
                data_list = []

        with add_col:
            if streamlit_app.button(
                "Add Item", key=self._key + "_" + key + "-add-item"
            ):

                if len(data_list) > 0:
                    # if the list has items, make a copy of the last item
                    data_list.append(data_list[-1])
                else:
                    # If the list is empty, add a None to trigger a new empty item
                    data_list.append(None)

        return data_list

    def _render_property_list_input(
        self, streamlit_app: Any, key: str, property: Dict
    ) -> Any:

        # Add title and subheader
        streamlit_app.subheader(property.get("title"))
        if property.get("description"):
            streamlit_app.markdown(property.get("description"))

        items_placeholder = streamlit_app.empty()
        streamlit_app.markdown("---")
        button_bar_placeholder = streamlit_app.empty()

        object_list = []

        if self._get_value(key) is not None or self._get_value(key) == []:
            data_list = self._get_value(key)
        elif property.get("init_value"):
            data_list = property.get("init_value")
        else:
            data_list = []

        with button_bar_placeholder.container():
            data_list = self._render_list_controls(streamlit_app, key, data_list)

        with items_placeholder.container():
            if len(data_list) > 0:
                for index, item in enumerate(data_list):
                    output = self._render_list_item(
                        streamlit_app, key, property["items"]["type"], item, index
                    )
                    if output is not None:
                        object_list.append(output)

        return object_list

    def _render_object_list_input(
        self, streamlit_app: Any, key: str, property: Dict
    ) -> Any:

        # TODO: support max_items, and min_items properties

        # Add title and subheader
        streamlit_app.subheader(property.get("title"))
        if property.get("description"):
            streamlit_app.markdown(property.get("description"))

        items_placeholder = streamlit_app.empty()
        streamlit_app.markdown("---")
        button_bar_placeholder = streamlit_app.empty()

        object_reference = schema_utils.resolve_reference(
            property["items"]["$ref"], self._schema_references
        )

        object_list = []

        # Treat empty list as a session data "hit"
        if self._get_value(key) is not None or self._get_value(key) == []:
            data_list = self._get_value(key)
        elif property.get("init_value"):
            data_list = property.get("init_value")
        else:
            data_list = []

        with button_bar_placeholder.container():
            data_list = self._render_list_controls(streamlit_app, key, data_list)

        with items_placeholder.container():
            if len(data_list) > 0:
                for index, item in enumerate(data_list):
                    output = self._render_list_item(
                        streamlit_app,
                        key,
                        object_reference["type"],
                        item,
                        index,
                        object_reference=object_reference,
                    )
                    if output is not None:
                        object_list.append(output)
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
            return self._render_object_list_input(streamlit_app, key, property)

        if schema_utils.is_property_list(property):
            return self._render_property_list_input(streamlit_app, key, property)

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
        if value is None or value == "":
            streamlit.info("No value returned!")
        else:
            # TODO: Detect if it is a FileContent instance
            # TODO: detect if it is base64
            file_extension = ""
            if "mime_type" in property_schema:
                mime_type = property_schema["mime_type"]
                file_extension = mimetypes.guess_extension(mime_type) or ""

                if _is_compatible_audio(mime_type):
                    streamlit.audio(value.as_bytes(), format=mime_type)
                    return

                if _is_compatible_image(mime_type):
                    streamlit.image(value.as_bytes())
                    return

                if _is_compatible_video(mime_type):
                    streamlit.video(value.as_bytes(), format=mime_type)
                    return

            filename = (
                (property_schema["title"] + file_extension)
                .lower()
                .strip()
                .replace(" ", "-")
            )
            streamlit.markdown(
                f'<a href="data:application/octet-stream;base64,{value}" download="{filename}"><input type="button" value="Download File"></a>',
                unsafe_allow_html=True,
            )

    def _render_single_complex_property(
        self, streamlit: Any, property_schema: Dict, value: Any
    ) -> None:
        # Add title and subheader
        streamlit.subheader(property_schema.get("title"))
        if property_schema.get("description"):
            streamlit.markdown(property_schema.get("description"))

        streamlit.json(json.dumps(value, default=pydantic_encoder))

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

        model_schema = output_data.schema(by_alias=False)
        model_properties = model_schema.get("properties")
        definitions = model_schema.get("definitions")

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
                data_items.append(data_item.dict())
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
        input_state = pydantic_input(
            key,
            model,
            group_optional_fields=group_optional_fields,
            lowercase_labels=lowercase_labels,
            ignore_empty_values=ignore_empty_values,
        )
        submit_button = st.form_submit_button(label=submit_label)

        if submit_button:
            try:
                return parse_obj_as(model, input_state)
            except ValidationError as ex:
                error_text = "**Whoops! There were some problems with your input:**"
                for error in ex.errors():
                    if "loc" in error and "msg" in error:
                        location = ".".join(error["loc"]).replace("__root__.", "")
                        error_msg = "**" + location + ":** " + error["msg"]
                        error_text += "\n\n" + error_msg
                    else:
                        # Fallback
                        error_text += "\n\n" + str(error)
                st.error(error_text)
                return None
    return None
