import json

from pydantic import BaseModel
from scripts.models.patrol.patrol_schema import PatrolSchema
from scripts.models.shortevent.short_event_schema import ShortEventSchema
from scripts.models.thought.thought_schema import ThoughtSchema


def dump_model_schema(config: BaseModel, output_name: str):
    """Creates the JSON schemas based on the passed Pydantic model and writes it to a file"""
    model_schema = config.model_json_schema()

    with open(output_name, "w") as json_file:
        json_file.write(json.dumps(model_schema, indent=2))


# noinspection PyTypeChecker
def main():
    dump_model_schema(PatrolSchema, "schemas/patrol.schema.json")
    dump_model_schema(ShortEventSchema, "schemas/shortevent.schema.json")
    dump_model_schema(ThoughtSchema, "schemas/thought.schema.json")


if __name__ == "__main__":
    main()
