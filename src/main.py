from core.menus import run_main_menu
from core.session import Session

def main() -> None:
    run_main_menu(Session())

if __name__ == "__main__":
    main()
