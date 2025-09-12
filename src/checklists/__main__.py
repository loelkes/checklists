"""This file is called with python -m checklists"""

import argparse
from pathlib import Path
from pylatex import Command, Document
from pylatex.utils import NoEscape
from pylatex.base_classes import Arguments, Environment
from .config import parse_config


class LatexChecklist(Environment):
    """A class to wrap the checklist environment."""

    _latex_name = "checklist"


def parse_cli_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Checklists CLI")
    parser.add_argument("--config", type=str, required=True, help="Path to the configuration file")
    return parser.parse_args()


def cli() -> None:
    """Command line interface entrypoint for checklists.

    The script is designed to be compatible with the existing preamble.inc file
    and make logic in the repository.
    """
    args = parse_cli_args()
    config = parse_config(args.config)

    doc = Document(documentclass=Command("documentclass", options="10pt", arguments="article"))
    doc.preamble.append(NoEscape(rf"\def\papersize{{{config.document.papersize}}}"))
    doc.preamble.append(NoEscape(Path(config.document.preamble).read_text()))
    doc.append(Command("title", config.document.title))

    # Iterate checklists in a document
    for data in config.checklists.values():
        with doc.create(LatexChecklist(arguments=Arguments(data.title))) as checklist:
            # Iterate items of the checklist
            for item in data.items:
                if item.type == "item":
                    checklist.append(Command("item", arguments=Arguments(item.title, item.value)))
                    # Iterate hints for the item
                    for hint in item.hints:
                        checklist.append(Command("hint", arguments=Arguments(hint)))
                elif item.type == "decision":
                    checklist.append(Command("decision", arguments=Arguments(item.title)))
                    # Iterate steps for the decision
                    for step in item.steps:
                        checklist.append(Command("step", arguments=Arguments(step)))

    doc.generate_tex(config.document.name)
    doc.generate_pdf(config.document.name, clean_tex=False, compiler=config.document.compiler)


if __name__ == "__main__":
    cli()
