from typing import Any

import jinja2

from src.config import settings

template_loader = jinja2.FileSystemLoader(settings.TEMPLATES_DIR)
template_env = jinja2.Environment(enable_async=True, loader=template_loader)


async def render_template(*, template_name: str, context: dict[str, Any]) -> str:
    template = template_env.get_template(template_name)
    return await template.render_async(context)
