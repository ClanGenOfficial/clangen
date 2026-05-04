import itertools
import json
from typing import List, Union

from pydantic import BaseModel

from scripts.models.common.common_schema import CommonSchema
from scripts.models.patrol.patrol_schema import PatrolSchema
from scripts.models.shortevent.short_event_schema import ShortEventSchema
from scripts.models.thought.thought_schema import ThoughtSchema
from scripts.models.util import (
    create_generate_json_schema_with_externals,
    get_defs_from_pydantic_model,
)


def dump_model_schema(
    model: BaseModel,
    output_name: str,
    only_defs: bool = False,
    inherit_defs_from: Union[List[BaseModel], None] = None,
):
    """
    Creates the JSON schemas based on the passed Pydantic model and writes it to a file

    :param model: pydantic model to dump
    :param output_name: where to dump the schema to
    :param only_defs: whether to only include definitions (helpful for shared schemas)
    :param inherit_defs_from: where to inherit defs from; when using shared schema
    """

    if only_defs:
        json_object = get_defs_from_pydantic_model(model)
    else:
        if inherit_defs_from is not None:
            defs_to_remove = [
                *itertools.chain.from_iterable(
                    item["$defs"].keys()
                    for item in [
                        get_defs_from_pydantic_model(item) for item in inherit_defs_from
                    ]
                )
            ]

            refs_to_rename = dict(
                (f"#/$defs/{item}", f"common.schema.json#/$defs/{item}")
                for item in defs_to_remove
            )

            generate_json_schema_with_externals = (
                create_generate_json_schema_with_externals(
                    defs_to_remove, refs_to_rename
                )
            )

            json_object = model.model_json_schema(
                schema_generator=generate_json_schema_with_externals
            )
        else:
            json_object = model.model_json_schema()

    with open(output_name, "w", encoding="utf-8") as json_file:
        json_file.write(json.dumps(json_object, indent=2))


# noinspection PyTypeChecker
def main():
    dump_model_schema(CommonSchema, "schemas/common.schema.json", only_defs=True)
    dump_model_schema(
        PatrolSchema, "schemas/patrol.schema.json", inherit_defs_from=[CommonSchema]
    )
    dump_model_schema(
        ShortEventSchema,
        "schemas/shortevent.schema.json",
        inherit_defs_from=[CommonSchema],
    )
    dump_model_schema(
        ThoughtSchema, "schemas/thought.schema.json", inherit_defs_from=[CommonSchema]
    )


if __name__ == "__main__":
    main()
