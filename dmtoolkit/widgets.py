import json
from typing import Optional
from wtforms import StringField

class TagField(StringField):
    def __init__(self, *args, whitelist: Optional[list[str]] = None, **kwargs):
        super(TagField, self).__init__(*args, **kwargs)
        self.whitelist = whitelist or []

    def __call__(self, **kwargs):
        kwargs["class"] = "tagify"
        kwargs["data-tags"] = json.dumps(self.whitelist)
        return super(TagField, self).__call__(**kwargs)

    # Find a hook to transform the form data from a json object to a list of strings
    # This is so that you can set the original tags easily, and so we can parse the vals when validating the form
    def get_tags(self):
        """Easy way to get the tags."""
        # The form data is serialized as '[{"value": x}, {"value": y}]
        return [x["value"] for x in json.loads(self.data or "[]")]

    def set_tags(self, tags: list[str]):
        """Easy way to set the tags."""
        self.data = json.dumps([{"value": x} for x in tags])
        print(self.data)