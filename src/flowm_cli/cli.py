"""Root Typer application wiring."""
from __future__ import annotations

import typer

from .constants import APP_NAME
from .install import register_install_commands
from .projects import projects_app
from .changes import changes_app
from .research import research_app
from .quality import quality_app
from .timeline import timeline_app
from .specs import specs_app

app = typer.Typer(name=APP_NAME, add_completion=False)
app.add_typer(projects_app, name="projects")
app.add_typer(changes_app, name="changes")
app.add_typer(research_app, name="research")
app.add_typer(quality_app, name="quality")
app.add_typer(specs_app, name="specs")
app.add_typer(timeline_app, name="timeline")


from . import __version__  # noqa: E402  (import after app creation)

register_install_commands(app, __version__)


def main() -> None:
    app()


__all__ = ["app", "main"]
