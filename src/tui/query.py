import questionary
import pandas as pd
from dataclasses import dataclass, field
from pathlib import Path

import db.interface as database
from storage.files import FileHandle
from tui.styles import MENU_STYLE

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

def print_top_ten(conditions: DataConditions) -> None:
    df = database.get_screens_by_metadata(
        authors = conditions.authors,
        target_ids = conditions.targets,
        seqs = conditions.sequences
    )
    print(df.sort_values(by="mle", ascending=False).head(10))

def export(conditions: DataConditions) -> FileHandle | None:
    df = database.get_screens_by_metadata(
        authors = conditions.authors,
        target_ids = conditions.targets,
        seqs = conditions.sequences
    )
    if df is None:
        print("Query returned no entries!")
        return None

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
    fh = FileHandle(path, use_zip=False)
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
        f"Confirm sequences to add to query:\n {', '.join(seqs)}"
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

def nl_query_clear(conditions: DataConditions) -> None:
    conditions.authors = []
    conditions.targets = []
    conditions.sequences = []
    return None

def nl_query_menu(): # (natural language)
    conditions = DataConditions()
    while True:
        print("\nTop 10 sequences of selected query:")
        print_top_ten(conditions)
        print()
        menu = {
            "Export selected query to CSV":
                lambda: (export(conditions)),
            "Clear query":
                lambda: (nl_query_clear(conditions)),
            "Add author(s)":
                lambda: (nl_subquery_authors(conditions)),
            "Add target ID(s)":
                lambda: (nl_subquery_targets(conditions)),
            "Add sequence(s)":
                lambda: (nl_subquery_seq(conditions)),
        }
        choices = [
            questionary.Separator(f"Current query: {conditions.message()}"),
            questionary.Separator(" "),
            "Export selected query to CSV",
            questionary.Separator(" "),
            "Clear query",
            "Add author(s)",
            "Add target ID(s)",
            "Add sequence(s)",
            questionary.Separator(" "),
            "Go back",
            questionary.Separator(" ")
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
