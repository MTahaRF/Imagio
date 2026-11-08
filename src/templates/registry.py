"""
Template Registry
─────────────────
Single source of truth for all available Manim templates.

Adding a new template:
    1. Create  src/templates/your_template.py  with a class that extends BaseTemplate.
    2. Import it below.
    3. Add one entry to TEMPLATE_REGISTRY.
    4. Add required capabilities to TEMPLATE_REQUIRED_CAPABILITIES when needed.
    The planner receives only templates whose required capabilities are enabled.
"""

from .title_slide        import TitleSlideTemplate
from .bullet_points      import BulletPointsTemplate
from .split_slide        import SplitSlideTemplate
from .equation_transform import EquationTransformTemplate
from .graph_plot         import GraphPlotTemplate
from .definition_slide   import DefinitionSlideTemplate
from .code_walkthrough   import CodeWalkthroughTemplate
from .comparison_slide   import ComparisonSlideTemplate
from .picture_slide      import PictureSlideTemplate
from .blank              import BlankTemplate


TEMPLATE_REGISTRY: dict = {
    "title_slide":        TitleSlideTemplate(),
    "bullet_points":      BulletPointsTemplate(),
    "split_slide":        SplitSlideTemplate(),
    "equation_transform": EquationTransformTemplate(),
    "graph_plot":         GraphPlotTemplate(),
    "definition_slide":   DefinitionSlideTemplate(),
    "code_walkthrough":   CodeWalkthroughTemplate(),
    "comparison_slide":   ComparisonSlideTemplate(),
    "picture_slide":      PictureSlideTemplate(),
    "blank":              BlankTemplate(),
}

TEMPLATE_REQUIRED_CAPABILITIES: dict[str, frozenset[str]] = {
    "picture_slide": frozenset({"image_generation"}),
}


def list_templates(
    enabled_capabilities: set[str] | frozenset[str] | None = None,
) -> list[dict]:
    """
    Returns planner metadata for templates supported by the enabled capabilities.
    Passing None lists every registered template for catalog/display use.
    """
    return [
        {"name": name, "description": tmpl.description()}
        for name, tmpl in TEMPLATE_REGISTRY.items()
        if enabled_capabilities is None
        or TEMPLATE_REQUIRED_CAPABILITIES.get(name, frozenset())
        <= enabled_capabilities
    ]


def get_template_requirements(name: str) -> frozenset[str]:
    if name not in TEMPLATE_REGISTRY:
        available = ", ".join(TEMPLATE_REGISTRY)
        raise KeyError(
            f"Template '{name}' not found. Available templates: {available}"
        )
    return TEMPLATE_REQUIRED_CAPABILITIES.get(name, frozenset())


def get_template(name: str):
    """
    Retrieves a template instance by name.
    Raises KeyError with a helpful message if the name is not registered.
    """
    if name not in TEMPLATE_REGISTRY:
        available = ", ".join(TEMPLATE_REGISTRY.keys())
        raise KeyError(
            f"Template '{name}' not found. Available templates: {available}"
        )
    return TEMPLATE_REGISTRY[name]