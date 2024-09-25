import logging
from functools import cache
from pathlib import Path

import jinja2

JINJA_UNDEFINED_HANDLER = jinja2.make_logging_undefined(
    logger=logging.getLogger(__file__),
    base=jinja2.StrictUndefined,
)

BASE_DIR = Path(__file__).resolve().parent.parent


@cache
def _get_environment() -> jinja2.Environment:
    loader = jinja2.FileSystemLoader(BASE_DIR / "templates")
    env = jinja2.Environment(
        loader=loader,
        undefined=JINJA_UNDEFINED_HANDLER,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env


def render_string_from_template(
    template_name: str,
    context: dict,
) -> str:
    env = _get_environment().get_template(template_name)
    return env.render(**context)
