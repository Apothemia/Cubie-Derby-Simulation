import json


# "stolen" from https://gist.github.com/jannismain/e96666ca4f059c3e5bc28abb711b5c92

class CompactJSONEncoder(json.JSONEncoder):
    """A JSON Encoder that puts small containers on single lines."""

    SINGLE_LINE_TYPES = (int, float, bool)
    """Acceptable types to put onto a single list line."""

    MAX_WIDTH = 70
    """Maximum width of a container that might be put on a single line."""

    MAX_ITEMS = 10
    """Maximum number of items in container that might be put on single line."""

    INDENTATION_CHAR = " "
    """Indentation character."""

    INDENTATION_WIDTH = 4
    """Number of indentation characters per level."""

    def __init__(self, *args, **kwargs):
        # using this class without indentation is pointless
        if kwargs.get("indent") is None:
            kwargs["indent"] = self.INDENTATION_WIDTH

        super().__init__(*args, **kwargs)
        self.indentation_level = 0

    def encode(self, o):
        """Encode JSON object *o* with respect to single line lists."""
        if isinstance(o, (list, tuple)):
            if self._put_on_single_line(o):
                return "[" + ", ".join(self.encode(el) for el in o) + "]"
            else:
                self.indentation_level += 1
                output = [self.indent_str + self.encode(el) for el in o]
                self.indentation_level -= 1
                return "[\n" + ",\n".join(output) + "\n" + self.indent_str + "]"
        elif isinstance(o, dict):
            if len(o) == 0:
                return "{}"

            if self._put_on_single_line(o):
                return "{ " + ", ".join(f"{self.encode(k)}: {self.encode(el)}" for k, el in o.items()) + " }"
            else:
                self.indentation_level += 1
                output = [self.indent_str + f"{json.dumps(k)}: {self.encode(v)}" for k, v in o.items()]
                self.indentation_level -= 1
                return "{\n" + ",\n".join(output) + "\n" + self.indent_str + "}"
        elif isinstance(o, float):  # Use scientific notation for floats, where appropriate
            return format(o, "g")
        elif isinstance(o, str):  # escape newlines
            o = o.replace("\n", "\\n")
            return f'"{o}"'
        else:
            return json.dumps(o)

    def iterencode(self, o, **kwargs):
        """Required to also work with `json.dump`."""
        return self.encode(o)

    def _put_on_single_line(self, o):
        if isinstance(o, (list, tuple)) and all(isinstance(i, self.SINGLE_LINE_TYPES) for i in o):
            return len(o) <= self.MAX_ITEMS and len(str(o)) - 2 <= self.MAX_WIDTH

        return False

    @property
    def indent_str(self) -> str:
        return self.INDENTATION_CHAR * (self.indentation_level * self.indent)
