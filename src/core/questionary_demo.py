import questionary


def demo_text():
    answer = questionary.text("What's your name?").ask()
    print(f"  -> '{answer}'\n")


def demo_password():
    answer = questionary.password("Enter a secret:").ask()
    print(f"  -> (hidden input, got '{answer}')\n")


def demo_confirm():
    answer = questionary.confirm("Do you want to continue?").ask()
    print(f"  -> {answer}\n")


def demo_select():
    answer = questionary.select(
        "Pick a sequence:",
        choices=["r270x", "r271x", "r272x"],
    ).ask()
    print(f"  -> '{answer}'\n")


def demo_checkbox():
    answers = questionary.checkbox(
        "Select preprocessing methods (space to toggle):",
        choices=["trim_adapters", "quality_filter", "dedup", "align"],
    ).ask()
    print(f"  -> {answers}\n")


def demo_autocomplete():
    answer = questionary.autocomplete(
        "Author name (start typing):",
        choices=["Alice Smith", "Bob Jones", "Carol White", "Dave Brown"],
    ).ask()
    print(f"  -> '{answer}'\n")


def demo_text_with_validation():
    def must_be_nonempty(val):
        return True if val.strip() else "Cannot be empty."

    answer = questionary.text(
        "Enter a sequence ID:",
        validate=must_be_nonempty,
    ).ask()
    print(f"  -> '{answer}'\n")


def demo_path():
    answer = questionary.path("Path to raw data file:").ask()
    print(f"  -> '{answer}'\n")


DEMOS = {
    "text         — free text input": demo_text,
    "password     — hidden input": demo_password,
    "confirm      — yes/no prompt": demo_confirm,
    "select       — pick one from a list": demo_select,
    "checkbox     — pick multiple from a list": demo_checkbox,
    "autocomplete — fuzzy select with typing": demo_autocomplete,
    "text+validate — input with validation": demo_text_with_validation,
    "path         — file path with tab completion": demo_path,
    "quit": None,
}


def main():
    print("=== questionary demo ===\n")
    while True:
        choice = questionary.select(
            "Which question type do you want to try?",
            choices=list(DEMOS.keys()),
        ).ask()

        if choice == "quit" or choice is None:
            print("Done.")
            break

        fn = DEMOS[choice]
        print()
        fn()


if __name__ == "__main__":
    main()
