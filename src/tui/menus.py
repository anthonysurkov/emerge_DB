import questionary

from tui.session import Session
from tui.styles import MENU_STYLE
import tui.accounts as account
import tui.sequences as seqs
import tui.query as query
import tui.methods as methods
import tui.screens as screens

# DATA MANAGEMENT --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
def data_manager():
    raise NotImplementedError

# MAIN MENU --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
def compose_main_menu(session: Session) -> tuple[dict[str, str], list]:
    sign_label = "Sign out" if session.is_signed_in else "Sign in"
    sign_fxn = account.sign_out if session.is_signed_in else account.sign_in

    menu = {
        sign_label:
            lambda: (sign_fxn(session)),
        "Get data":
            query.nl_query_menu,
        "Register new target sequence":
            seqs.register_hairpin,
        "Register new EMERGe screen":
            lambda: screens.register_emerge(session),
        "(UNDER CONSTRUCTION) Data management (e.g. edit sequences, screens)":
            data_manager,
        "(UNDER CONSTRUCTION) Methods manager (e.g. change method write-ups)":
            methods.manager,
        "Account manager (e.g. delete account)":
            lambda: (account.manager(session)),
        "Quit": None
    }
    choices = [
        questionary.Separator(session.message()),
        sign_label,
        "Get data",
        "Register new target sequence",
        "Register new EMERGe screen",
        "(UNDER CONSTRUCTION) Data management (e.g. edit sequences, screens)",
        "(UNDER CONSTRUCTION) Methods manager (e.g. change method write-ups)",
        "Account manager (e.g. delete account)",
        questionary.Separator(" "),
        "Quit",
        questionary.Separator(" "),
        questionary.Separator("Suggestion? Bug report? Misbehaving data? "
            "Cat stuck in a tree?\n"
            "   Contact me! Anthony Surkov, asurkov@cmu.edu\n"
        ),
    ]
    return (menu, choices)

def run_main_menu(session: Session) -> None:
    while True:
        menu, choices = compose_main_menu(session)

        choice = questionary.select(
            message="",
            choices=choices,
            style=MENU_STYLE,
        ).ask()

        if choice == "Quit" or choice is None:
            return

        print()
        menu[choice]()
