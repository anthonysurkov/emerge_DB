import questionary
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import HTML
from dataclasses import dataclass

import db.interface as database
from core.rnatui import RNA_Prompter

# registration control flow 1: main menu with options to sign in to the system,
# recquisition data, register a new sequence, or register a new screen (signin-locked)
# or `methods management` (tbd)
# NEED: a menu class in core, need functions for registry of author_info
# and sequence_metadata, and need an interface function in db to display avail
# options to the menu + populate new authors/sequences in a controlled way
# --> this will probably live in a main.py

SYSTEM_USER = None

# SIGN-IN --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
def create_account() -> bool:
    global SYSTEM_USER
    print("Enter `exit` at any point to abort")

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
        SYSTEM_USER = author
        return True
    else:
        return create_account()

def delete_account() -> None:
    global SYSTEM_USER
    choices = (
        database.get_authors() +
        [questionary.Separator(" "), "Go back"]
    )
    answer = questionary.select(
        "Available authors:",
        choices
    ).ask()
    if answer == "Go back":
        return
    else:
        if not questionary.confirm(
            f"Author: {answer} - delete account?"
            ).ask():
            return
        if SYSTEM_USER == answer:
            SYSTEM_USER = None
        status = database.remove_author(answer)
        if status is False:
            print("Cannot delete account registered with "
                "currently-stored EMERGe screens!"
             )

def sign_in() -> bool:
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
        return False
    if answer == "Create account":
        return create_account()
    else:
        SYSTEM_USER = answer
        return True

def sign_out() -> None:
    global SYSTEM_USER
    SYSTEM_USER = None

def get_system_user_message() -> str:
    global SYSTEM_USER
    signed_out = "\n   To register or manage EMERGe screens, please sign in!\n"
    if SYSTEM_USER:
        signed_in = f"\n   You are signed in as {SYSTEM_USER.upper()}\n"
    else:
        signed_in = None
    return (signed_in if SYSTEM_USER else signed_out)

def account_manager() -> None:
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

# DATA MANAGEMENT --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
def data_manager():
    print("This will, in the future, provide handles on editing/deleting "
        "registered sequences and EMERGe screens. For now, please contact "
        "Anthony (asurkov@cmu.edu) for manual editing of the EMERGe "
        "database system."
    )

# SEQUENCE MANAGEMENT --- --- --- --- --- --- --- --- --- --- --- --- --- ---
BASE_SYSTEM_PROMPT = (
    "Please select the appropriate "
    "regions of your RNA hairpin below.\n\n"
    "Example:\n"
    "...TTTGACCC<ansicyan>AGAG</ansicyan><ansibrightblue>A</ansibrightblue>"
    "<ansicyan>AAGA</ansicyan>TGAGCCTTTCTTTCTTTC"
    "GGCTC<ansigreen>NNNNNNNNNN</ansigreen>GGGTCAAAT...\n"
    "  <ansicyan>██</ansicyan> Target region\n"
    "  <ansibrightblue>██</ansibrightblue> Target adenosine\n"
    "  <ansigreen>██</ansigreen> Variable region\n\n"
    "Use the left and right arrow keys to move the cursor below."
)

@dataclass
class RegionSelection:
    substr: str
    idx: tuple[int, int]

def prompt_for_sequence_regions(
    rna_sequence: str,
    base_system_prompt: str = None
) -> dict[str, str]:
    responses: dict[str, RegionSelection] = {}
    if not base_system_prompt:
        base_system_prompt = BASE_SYSTEM_PROMPT

    unconfirmed = True
    while unconfirmed:
        rendered_sequence = rna_sequence

        regions = [
            ("target adenosine", "At", "ansibrightblue"),
            ("target region", "tr", "ansicyan"),
            ("variable region", "vr", "ansigreen")
        ]
        cursor_pos = None
        for region_label, key, color in regions:
            prompt = (
                base_system_prompt +
                f"\n<b>Please select the {region_label}.</b>\n"
            )
            allow_overlap = None
            if key == "tr" and "At" in responses:
                at_start, at_end = responses["At"].idx
                allow_overlap = set(range(at_start, at_end))
            prompter = RNA_Prompter(
                rendered_sequence,
                system_prompt=prompt,
                initial_cursor_position=cursor_pos,
                allow_overlap=allow_overlap,
            )
            response = prompter.prompt_for_substr()
            cursor_pos = prompter.buf.cursor_position
            if not response:
                return None
            substr, idx = response
            responses[key] = RegionSelection(substr, idx)
            html_start, html_end = prompter.html_span(*idx)
            rendered_sequence = (
                rendered_sequence[:html_start]
                + f"<{color}>{substr}</{color}>"
                + rendered_sequence[html_end:]
            )
        RNA_Prompter.clear_screen()
        print_formatted_text(HTML(base_system_prompt + "\n\n\n"))
        print_formatted_text(HTML(rendered_sequence))
        if questionary.confirm("Confirm selection?").ask():
            unconfirmed = False
    return responses

def print_registered_sequences() -> None:
    regis = database.get_sequence_ids()
    if not regis:
        print("No sequence IDs currently registered.\n")
    else:
        print("Currently registered sequence IDs:")
        for row in regis:
            print("• " + row["sequence_id"])
        print()

def register_sequence():
    print_registered_sequences()
    print("Enter `exit` at any point to abort\n")

    sequence_id = questionary.text(
        "Enter your sequence ID (derivative of the mutation "
        "studied; e.g. `r270x_z`, `r270x`, `r255x`). Please avoid dashes (`-`) "
        "and spaces! "
    ).ask()
    if sequence_id == "exit" or sequence_id == None:
        return
    sequence_id = sequence_id.lower()

    unconfirmed = True
    while unconfirmed:
        hairpin_seq = questionary.text(
            "Copy-paste your hairpin sequence (no quotes, indents, or "
            "5'- 3'- markers):"
        ).ask()
        if hairpin_seq == "exit" or hairpin_seq == None:
            return
        hairpin_seq = (
            hairpin_seq
              .replace("T","U").upper()
              .replace("\r", "")
              .replace("\n", "")
        )
        print(hairpin_seq)
        if questionary.confirm(
            "Does this look correct? (corrected for thymine presence, "
            "newlines, and case)").ask():
            unconfirmed = False

    responses = prompt_for_sequence_regions(hairpin_seq)
    edit_A_idx     = responses["At"].idx[0]
    edit_reg_start = responses["tr"].idx[0]
    edit_reg_end   = responses["tr"].idx[1]
    var_reg_start  = responses["vr"].idx[0]
    var_reg_end    = responses["vr"].idx[1]

    print(
        f"Sequence ID: {sequence_id}\n"
        f"Hairpin sequence: {hairpin_seq}\n"
        f"Edit-A index: {edit_A_idx}\n"
        f"Edit region: {edit_reg_start} through {edit_reg_end}\n"
        f"Variable region: {var_reg_start} through {var_reg_end}\n"
    )
    if questionary.confirm("Confirm?").ask():
        if not database.insert_sequence_info(sequence_id, hairpin_seq,
            edit_A_idx, edit_reg_start, edit_reg_end, var_reg_start, var_reg_end
        ):
            print("Sequence registration failed. Is the sequence ID already "
                "registered?"
            )
    else:
        return register_sequence()


# EMERGE REGISTRATION --- --- --- --- --- --- --- --- --- --- --- --- --- ---
def register_emerge():
    global SYSTEM_USER
    if not SYSTEM_USER:
        print("Please sign in!")
        if not sign_in():
            return

# METHODS MANAGEMENT --- --- --- --- --- --- --- --- --- --- --- --- --- ---
def methods_manager():
    print("nuh-uh, not yet")

# MAIN --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
def compose_main_menu() -> tuple[dict[str, str], list]:
    global SYSTEM_USER
    sign_label = "Sign in" if SYSTEM_USER is None else "Sign out"
    sign_fxn = sign_in if SYSTEM_USER is None else sign_out
    sign_msg = get_system_user_message()

    menu = {
        sign_label: sign_fxn,
        "Get data": get_data,
        "Register new sequence": register_sequence,
        "Register new EMERGe screen": register_emerge,
        "Data management (e.g. edit sequences, screens)": data_manager,
        "Methods manager (e.g. change method write-ups)": methods_manager,
        "Account manager (e.g. delete account)": account_manager,
        "Quit": None
    }
    choices = [
        questionary.Separator(sign_msg),
        sign_label,
        "Get data",
        "Register new sequence",
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

def main():
    global SYSTEM_USER

    print("\nWelcome to the EMERGe database system.\n")
    while True:
        menu, choices = compose_main_menu()

        choice = questionary.select(message="", choices=choices).ask()
        if choice == "Quit" or choice is None:
            print("Exit")
            break
        fn = menu[choice]
        print()
        fn()

if __name__ == "__main__":
    main()
