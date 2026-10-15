from followthemoney import model

from openlobbying import ACTOR_SCHEMATA


def is_actor(schema_name: str) -> bool:
    """Check if a schema should be treated as an actor profile."""
    schema = model.get(schema_name)
    return schema is not None and any(schema.is_a(s) for s in ACTOR_SCHEMATA)
