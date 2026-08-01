from pathlib import Path
import questionary

import db.interface as database
from tui.styles import MENU_STYLE

def print_method_info(method_name: str) -> None:
    info = database.get_method_info(method_name)
    print(
        f"Method name: {info['method_name']}\n"
        f"Method path: {info['method_path']}\n"
        f"Method desc: {info['method_desc']}\n"
        f"Method writeup path: {info['method_writeup_path']}\n"
    )

def get_emerge_writeup(screen_id: int) -> str:
    print("Currently unimplemented")

def prompt_emerge_writeup() -> None:
    print("Currently unimplemented")

def prompt_method_writeup_update() -> bool:
    options = database.get_method_names()
    if not options:
        print("No methods currently registered.")
        return False

    name = questionary.select(
        "Please select the method to update. Enter Ctrl+C to abort.",
        choices=options
    ).ask()
    if name is None:
        return False

    print_method_info(name)
    response = questionary.text("Please enter the updated writeup path.").ask()
    if response is None:
        return False
    response_path = Path(response)
    if not response_path.exists():
        print(
            "Specified response path does not exist. Please double-check "
            "and try again."
        )
        return False
    if not questionary.confirm(
        "Are you sure you want to update this method?"
    ).ask():
        return False
    status = database.update_method_writeup(name, response)
    if status is False:
        print("Something went wrong. Writeup path was not updated.")
        return False
    return True

def prompt_method_desc_update() -> bool:
    options = database.get_method_names()
    if not options:
        print("No methods currently registered.")
        return False

    name = questionary.select(
        "Please select the method to update. Enter Ctrl+C to abort.",
        choices=options
    ).ask()
    if name is None:
        return False

    print_method_info(name)
    response = questionary.text("Please enter the updated description.").ask()
    if response is None:
        return False
    if not questionary.confirm(
        "Are you sure you want to update this method?"
    ).ask():
        return False
    status = database.update_method_desc(name, response)
    if status is False:
        print("Something went wrong. Description was not updated.")
        return False
    return True

def prompt_method_deletion() -> bool:
    options = database.get_method_names()
    if not options:
        print("No methods currently registered.")
        return False

    name_to_delete = questionary.select(
        "Please select the method to delete. Enter Ctrl+C to abort.",
        choices=options
    ).ask()
    if name_to_delete is None:
        return False

    print_method_info(name)
    if not questionary.confirm(
        "Are you sure you want to delete this registered method?"
    ).ask():
        return False

    status = database.remove_method(name_to_delete)
    if status is False:
        print("Cannot delete a method used by currently-stored EMERGe screens!")
        return False
    return True

def prompt_method_registry() -> None:
    print("New method registration")
    print("Enter Ctrl+C at any point to abort\n")

    unconfirmed = True
    while unconfirmed:
        method_response = questionary.text(
            "Enter method name (e.g. `primary_regex`). "
            "Please avoid dashes (`-`) and spaces!"
        ).ask()
        if method_response is None:
            return
        method_name = method_response.lower()

        method_not_ok = True
        while method_not_ok:
            method_response = questionary.text(
                "Paste method path:"
            ).ask()
            if method_response is None:
                return
            method_response = method_response.replace("\r","").replace("\n","")
            method_path = Path(method_response)
            if method_path.exists():
                break
            else:
                print("Provided method path did not resolve. "
                    "Please double-check and re-enter.\n"
                )

        method_response = questionary.text(
            "Enter/paste brief method description. "
            "Enter `None` (case-sensitive) to skip."
        ).ask()
        if method_response is None:
            return
        method_desc = (
            None if method_response == "None"
            else method_response.replace("\r","").replace("\n","")
        )

        method_response = questionary.text(
            "Paste path to method writeup. "
            "Enter `None` (case-sensitive) to skip."
        ).ask()
        if method_response is None:
            return
        method_writeup_path = (
            None if method_response == "None"
            else method_response.replace("\r","").replace("\n","")
        )

        print(
            f"Method name: {method_name}\n"
            f"Method path: {method_path}\n"
            f"Method desc: {method_desc}\n"
            f"Method writeup path: {method_writeup_path}\n"
        )
        if questionary.confirm("Does this look correct?").ask():
            unconfirmed=False

    method_path = Path(method_path)
    method_writeup_path = (
        None if method_writeup_path is None
        else Path(method_writeup_path)
    )
    database.insert_method_info(
        method_name,
        method_path,
        method_desc,
        method_writeup_path
    )

def manager() -> None:
    while True:
        current_method_names = database.get_method_names()
        mgr_menu = {
            "Register new method": prompt_method_registry,
            "Update method description": prompt_method_desc_update,
            "Update method write-up": prompt_method_writeup_update,
            "Get EMERGe screen write-up": prompt_emerge_writeup,
            "Delete registered method": prompt_method_deletion,
            "Go back": None
        }
        mgr_choices = [
            "Register new method",
            "Update method description",
            "Update method write-up",
            "Get EMERGe screen write-up",
            "Delete registered method",
            questionary.Separator(" "),
            "Go back",
            questionary.Separator(" "),
        ]
        if current_method_names == []:
            print("No currently registered methods!")
        else:
            print("Currently registered methods:\n")
            print("\n".join(
                f"  {index}. {name}"
                for index, name in enumerate(current_method_names, start=1)
            ))
        print()
        choice = questionary.select(
            message="",
            choices=mgr_choices,
            style=MENU_STYLE,
        ).ask()
        if choice == "Go back" or choice == None:
            return
        fn = mgr_menu[choice]
        print()
        fn()
