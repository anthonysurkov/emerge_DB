import questionary

import db.interface as database

# registration control flow 1: main menu with options to sign in to the system,
# recquisition data, register a new sequence, or register a new screen (signin-locked)
# or `methods management` (tbd)
# NEED: a menu class in core, need functions for registry of author_info
# and sequence_metadata, and need an interface function in db to display avail
# options to the menu + populate new authors/sequences in a controlled way
# --> this will probably live in a main.py

SYSTEM_USER = None

# SIGN-IN --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
def create_account() -> None:
    global SYSTEM_USER
    print("Enter `exit` at any point to abort")

    author = questionary.text("Enter your name:").ask()
    if author == "exit":
        return

    email = questionary.text("Enter your email:").ask()
    if email == "exit":
        return

    if questionary.confirm(
        f"Author: {author}, Email: {email} - correct?"
        ).ask():
        database.insert_author(author, email)
        SYSTEM_USER = author
    else:
        return create_account()

def delete_account() -> None:
    print("placeholder function")

def sign_in() -> None:
    global SYSTEM_USER
    choices = (
        database.get_authors() +
        [questionary.Separator(" "), "Create account", "Go back"]
    )
    answer = questionary.select(
        "Available authors:",
        choices
    ).ask()
    if answer == "Go back":
        return
    if answer == "Create account":
        create_account()
    else:
        SYSTEM_USER = answer

def sign_out() -> None:
    global SYSTEM_USER
    SYSTEM_USER = None

def return_system_user() -> str:
    global SYSTEM_USER
    signed_out = "\n To register EMERGe screens, please sign in!\n"
    if SYSTEM_USER:
        signed_in = f"\n You are signed in as {SYSTEM_USER.upper()}\n"
    else:
        signed_in = None
    return (signed_in if SYSTEM_USER else signed_out)

def signin_management() -> None:
    global SYSTEM_USER

    signin_menu = {
        "Sign out": sign_out,
        "Delete an account": delete_account,
        "Go back": None
    }
    signin_choices = [
        "Sign out",
        "Delete an account",
        questionary.Separator(" "),
        "Go back",
    ]
    choice = questionary.select(message="", choices=signin_choices).ask()
    if choice == "Go back":
        return
    fn = signin_menu[choice]
    print()
    fn()

# DATA REQUISITION --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
def get_data():
    print("nuh-uh, not yet")

# SEQUENCE MANAGEMENT --- --- --- --- --- --- --- --- --- --- --- --- --- ---
# V1 (TEMPORARY) - SEE _README.md

# - sequence_info
#   - sequence_id, hairpin_seq, edit_A_idx, edit_region_start, edit_region_end,
#     var_region_start, var_region_end
def set_sequence():
    global SYSTEM_USER
    if not SYSTEM_USER:
        print("Please sign in!")
        return

    print("Enter `exit` at any point to abort")

    sequence_id = questionary.text(
        "Enter your sequence ID (typically, derivative of the mutation "
        "studied; e.g. `r270x_z`, `r270x`, `r255x`):"
    ).ask()
    if sequence_id == "exit":
        return

    hairpin_seq = questionary.text("Enter your hairpin sequence:").ask()
    if hairpin_seq == "exit":
        return

    edit_A_idx  = questionary.text("Enter your 0-indexed edit site:").ask()
    if edit_A_idx == "exit":
        return

    edit_reg_start = questionary.text(
        "Enter your 0-indexed edit region start:"
    ).ask()
    if edit_reg_start == "exit":
        return

    edit_reg_end = questionary.text(
        "Enter your 0-indexed edit region end:"
    ).ask()
    if edit_reg_end == "exit":
        return

    var_reg_start = questionary.text(
        "Enter your 0-indexed variable region start:"
    ).ask()
    if var_reg_start == "exit":
        return

    var_reg_end = questionary.text(
        "Enter your 0-indexed variable region end:"
    ).ask()
    if var_reg_end == "exit":
        return

    if questionary.confirm(
        f"Sequence ID: {sequence_id}\n"
        f"Hairpin sequence: {hairpin_seq}\n"
        f"Edit-A index: {edit_A_idx}\n"
        f"Edit region: {edit_reg_start} through {edit_reg_end}\n"
        f"Variable region: {var_reg_start} through {var_reg_end}\n"
    ).ask():
        database.insert_sequence_info(sequence_id, hairpin_seq, edit_A_idx,
            edit_reg_start, edit_reg_end, var_reg_start, var_reg_end
        )
    else:
        return set_sequence():


# EMERGE REGISTRATION --- --- --- --- --- --- --- --- --- --- --- --- --- ---
def registration():
    print("nuh-uh, not yet")

# METHODS MANAGEMENT --- --- --- --- --- --- --- --- --- --- --- --- --- ---
def methods_management():
    print("nuh-uh, not yet")

# MAIN --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
def main():
    global SYSTEM_USER

    print("\nWelcome to the EMERGe database system.\n")
    main_menu = {
        "Sign in": sign_in,
        "Data requisition": get_data,
        "Register sequence": set_sequence,
        "Register EMERGe screen": registration,
        "Methods management": methods_management,
        "Sign-in management": signin_management,
        "Quit": None
    }
    while True:
        choices = [
            questionary.Separator(" "),
            "Sign in",
            "Data requisition",
            "Register sequence",
            "Register EMERGe screen",
            questionary.Separator(return_system_user()),
            "Methods management",
            "Sign-in management",
            questionary.Separator(" "),
            "Quit",
            questionary.Separator(" ")
        ]

        choice = questionary.select(message="", choices=choices).ask()
        if choice == "Quit" or choice is None:
            print("Exit")
            break
        fn = main_menu[choice]
        print()
        fn()

if __name__ == "__main__":
    main()
