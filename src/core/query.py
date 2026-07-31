import questionary
import pandas as pd
from dataclasses import dataclass, field
from pathlib import Path

import db.interface as database
from core.files import FileHandle
from core.styles import MENU_STYLE

@dataclass
class DataConditions:
    authors: list[str] = field(default_factory=list)
    targets: list[str] = field(default_factory=list)
    sequences: list[str] = field(default_factory=list)

    def message(self) -> str:
        def phrase(items: list[str]) -> str:
            if len(items) < 2:
                return "".join(items)
            return ", ".join(items[:-1]) + f" and {items[-1]}"

        selection = (
            f"sequence {self.sequences[0]}"
            if len(self.sequences) == 1
            else f"sequences {phrase(self.sequences)}"
            if self.sequences
            else "all sequences"
        )

        screen_filters = []
        if self.authors:
            screen_filters.append(f"by {phrase(self.authors)}")
        if self.targets:
            screen_filters.append(f"targeting {phrase(self.targets)}")

        screens = (
            f"screens {' '.join(screen_filters)}"
            if screen_filters
            else "all registered screens"
        )
        selection = selection[0].upper() + selection[1:]
        return f"{selection} from {screens}."

def show_top(conditions: DataConditions) -> None:
    df = database.get_screens_by_metadata(
        authors = conditions.authors,
        target_ids = conditions.targets,
        seqs = conditions.sequences
    )
    print(df.nlargest(20, "mle"))

def export(conditions: DataConditions) -> FileHandle | None:
    df = database.get_screens_by_metadata(
        authors = conditions.authors,
        target_ids = conditions.targets,
        seqs = conditions.sequences
    )
    filename = questionary.text(
        "Filename [ending in .csv]:"
    ).ask()
    if filename is None:
        return None

    filename = filename.removesuffix(".csv") + ".csv"
    path = Path.cwd() / filename
    if path.exists():
        print(f"{filename} already exists. Please choose a different name.")
        return None

    df.to_csv(filename, index=None)
    fh = FileHandle(path)
    fh.activate()
    print(f"Exported to {fh.path}")

def nl_subquery_seq(conditions: DataConditions) -> list[str] | None:
    response = questionary.text(
        "Enter sequences separated by commas (5' to 3'):\n"
    ).ask()
    if response is None:
        return None
    seqs = [
        sequence.strip().upper().replace("T", "U")
        for sequence in response.split(",")
        if sequence.strip()
    ]
    confirm = questionary.confirm(
        f"Confirm sequences added to query:\n {', '.join(seqs)}"
    ).ask()
    if confirm:
        conditions.sequences.extend(seqs)
    return None

def nl_subquery_authors(conditions: DataConditions) -> list[str] | None:
    response = questionary.checkbox(
        "Select authors:\n",
        choices=database.get_authors(),
        style=MENU_STYLE,
    ).ask()
    if response is None:
        return None
    confirm = questionary.confirm(
        f"Confirm authors added to query:\n {', '.join(response)}"
    ).ask()
    if confirm:
        conditions.authors.extend(response)
    return None

def nl_subquery_targets(conditions: DataConditions) -> list[str] | None:
    response = questionary.checkbox(
        "Select target IDs:\n",
        choices=database.get_target_ids(),
        style=MENU_STYLE,
    ).ask()
    if response is None:
        return None
    confirm = questionary.confirm(
        f"Confirm targets added to query:\n {', '.join(response)}"
    ).ask()
    if confirm:
        conditions.targets.extend(response)
    return None

def nl_query_menu(): # (natural language)
    conditions = DataConditions()
    while True:
        menu = {
            "Show top-20 (by MLE, descending) of selected query":
                lambda: (show_top(conditions)),
            "Export selected query to CSV":
                lambda: (export(conditions)),
            "Query by sequence(s)":
                lambda: (nl_subquery_seq(conditions)),
            "Query by author(s)":
                lambda: (nl_subquery_authors(conditions)),
            "Query by target ID(s)":
                lambda: (nl_subquery_targets(conditions))
        }
        choices = [
            questionary.Separator(f"Query: {conditions.message()}"),
            questionary.Separator(" "),
            "Show top-20 (by MLE, descending) of selected query",
            "Export selected query to CSV",
            questionary.Separator(" "),
            "Query by sequence(s)",
            "Query by author(s)",
            "Query by target ID(s)",
            questionary.Separator(" "),
            "Go back"
        ]
        choice = questionary.select(
            message="",
            choices=choices,
            style=MENU_STYLE,
        ).ask()
        if choice == "Go back" or choice is None:
            break
        fn = menu[choice]
        print()
        fn()
