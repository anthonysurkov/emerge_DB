import time
import questionary
from core.styles import MENU_STYLE

import db.server as db_server
from core.menus import compose_main_menu
from core.session import Session

def main():
    session = Session()

    if not db_server.ping():
        print("Starting database server...")
        db_server.start()
        for _ in range(10):
            if db_server.ping():
                print("Server pinged!")
                break
            time.sleep(1)
        else:
            print("Could not start or connect to PostgreSQL.")
            return

    print("\nWelcome to the EMERGe database system.\n")
    while True:
        menu, choices = compose_main_menu(session)

        choice = questionary.select(
            message="",
            choices=choices,
            style=MENU_STYLE,
        ).ask()
        if choice == "Quit" or choice is None:
            print("Exit")
            break

        fn = menu[choice]
        print()
        fn()

if __name__ == "__main__":
    main()
