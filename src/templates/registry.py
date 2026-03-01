"""
Template Registry
─────────────────
Single source of truth for all available Manim templates.

Adding a new template:
    1. Create  src/templates/your_template.py  with a class that extends BaseTemplate.
    2. Import it below.
    3. Add one entry to TEMPLATE_REGISTRY.
    ← Nothing else needs to change. The planner reads this registry automatically.
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


def list_templates() -> list[dict]:
    """
    Returns a list of {name, description} dicts for every registered template.
    Used by the Scene Planner to decide which template fits each scene.
    """
    return [
        {"name": name, "description": tmpl.description()}
        for name, tmpl in TEMPLATE_REGISTRY.items()
    ]


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