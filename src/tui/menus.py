import questionary

from tui.session import Session
from tui.styles import MENU_STYLE
import tui.accounts as account
import tui.sequences as seqs
import tui.query as query
import tui.methods as methods

# DATA MANAGEMENT --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
def data_manager():
    print("This will, in the future, provide handles on editing/deleting "
        "registered sequences and EMERGe screens. For now, please contact "
        "Anthony (asurkov@cmu.edu) for manual editing of the EMERGe "
        "database system."
    )

# EMERGE REGISTRATION --- --- --- --- --- --- --- --- --- --- --- --- --- ---
def register_emerge():
    print('a')
"""
    global SYSTEM_USER
    if not SYSTEM_USER:
        print("Please sign in!")
        if not sign_in():
            return

    screens = database.get_screens_overview()
    if screens is None:
        print("No currently-registered screens available.")
    else:
        print(f"Currently-registered screens:\n {screens")

    sids = get_registered_sequences()
"""

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
            register_emerge,
        "Data management (e.g. edit sequences, screens)":
            data_manager,
        "Methods manager (e.g. change method write-ups)":
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
        "Data management (e.g. edit sequences, screens)",
        "Methods manager (e.g. change method write-ups)",
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
