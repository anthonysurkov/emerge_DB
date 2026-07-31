import questionary

from core.session import Session
from core.styles import MENU_STYLE
import db.interface as database

def create_account(session: Session) -> bool:
    print("Enter `exit` at any point to abort.")

    author = questionary.text("Enter your name:").ask()
    if author == "exit":
        return False

    email = questionary.text("Enter your email:").ask()
    if email == "exit":
        return False

    if questionary.confirm(
        f"Author: {author}, Email: {email} - correct?"
        ).ask():
        database.insert_author(author, email)
        session.sign_in(author)
        return True
    else:
        return create_account()

def delete_account(session: Session) -> bool:
    choices = (
        database.get_authors() +
        [questionary.Separator(" "), "Go back"]
    )
    answer = questionary.select(
        "Available authors:",
        choices,
        style=MENU_STYLE,
    ).ask()
    if answer == "Go back":
        return
    else:
        if not questionary.confirm(
            f"Author: {answer} - delete account?"
            ).ask():
            return False
        if session.user == answer:
            session.sign_out()
        status = database.remove_author(answer)
        if status is False:
            print("Cannot delete account registered with "
                "currently-stored EMERGe screens!"
             )
            return False
    return True

def sign_in(session: Session) -> bool:
    choices = (
        database.get_authors() +
        [questionary.Separator(" "), "Create account", "Go back"]
    )
    answer = questionary.select(
        "Available authors:",
        choices,
        style=MENU_STYLE,
    ).ask()
    if answer == "Go back":
        return False
    if answer == "Create account":
        return create_account(session)
    else:
        session.sign_in(answer)
        return True

def sign_out(session: Session) -> bool:
    session.sign_out()

def manager(session: Session) -> None:
    mgr_menu = {
        "Sign out":
            lambda: (sign_out(session)),
        "Delete an account":
            lambda: (delete_account(session)),
        "Go back": None
    }
    mgr_choices = [
        "Sign out",
        "Delete an account",
        questionary.Separator(" "),
        "Go back",
    ]
    choice = questionary.select(
        message="",
        choices=mgr_choices,
        style=MENU_STYLE,
    ).ask()
    if choice == "Go back":
        return
    fn = mgr_menu[choice]
    print()
    fn()
