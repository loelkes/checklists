from pathlib import Path
import msgspec


class Base(msgspec.Struct, forbid_unknown_fields=True, rename="kebab"):
    """Base class for the configuration file format."""


class Document(Base):
    """Document definition.

    This configures the document metadata such as title, name, preamble, date
    and papersize.
    """

    preamble: str
    name: str
    title: str
    version: str | None = None
    date: str | None = None
    papersize: str = "4"
    compiler: str = "xelatex"

    def __post_init__(self):
        """Papersize values match configuration in preamble.inc of this
        repository.
        """
        if self.papersize not in ["4", "5", "6", "7"]:
            raise ValueError("papersize must be 4, 5, 6 or 7")


class ChecklistElement(Base):
    """Definition of an individual checklist item"""

    type: str
    title: str
    value: str | None = None
    steps: list[str] = []
    hints: list[str] = []

    def __post_init__(self):
        """Semantic validation of the checklist item"""
        if self.type not in ["item", "decision"]:
            raise ValueError("checklist element type must be item or decision")
        if self.type == "item" and self.value is None:
            raise ValueError("checklist item must have a value")
        if self.type == "decision" and not len(self.steps):
            raise ValueError("checklist decision must have at least one step")
        if self.type == "decision" and len(self.hints):
            raise ValueError("checklist decision can't have hints")


class ChecklistData(Base):
    """Data for the checklist"""

    title: str
    items: list[ChecklistElement]


class ChecklistConfig(Base):
    """Configuration for the checklist"""

    document: Document
    checklists: dict[str, ChecklistData]


def parse_config(filepath: Path | str) -> ChecklistConfig:
    """Decode a configuration file.

    Config file format is determined by the file extension and can be toml,
    yaml, yml or json.
    """
    if isinstance(filepath, str):
        filepath = Path(filepath)
    if filepath.suffix == ".toml":
        return msgspec.toml.decode(filepath.read_text(), type=ChecklistConfig)
    elif filepath.suffix == ".yaml" or filepath.suffix == ".yml":
        return msgspec.yaml.decode(filepath.read_text(), type=ChecklistConfig)
    elif filepath.suffix == ".json":
        return msgspec.json.decode(filepath.read_text(), type=ChecklistConfig)
    else:
        raise ValueError(f"Unsupported config file format: {filepath.suffix}")
