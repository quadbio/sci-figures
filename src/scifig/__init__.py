"""scifig: style, mm layout, recurring elements and export for Nature-style research figures."""

from importlib.metadata import version

from .elements import BadgeHandle, badge, badge_handle, colorbar, embedding_axes, ink_on, scale_bar
from .export import save
from .layout import MM, add_axes_mm, new_figure, panel_letter
from .style import LINEWIDTHS, SIZES, apply_style

__all__ = [
    "BadgeHandle",
    "LINEWIDTHS",
    "MM",
    "SIZES",
    "add_axes_mm",
    "apply_style",
    "badge",
    "badge_handle",
    "colorbar",
    "embedding_axes",
    "ink_on",
    "new_figure",
    "panel_letter",
    "save",
    "scale_bar",
]
__version__ = version("sci-figures")
