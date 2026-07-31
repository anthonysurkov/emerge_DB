from dataclasses import dataclass

@dataclass
class Session:
    user: str | None = None

    @property
    def is_signed_in(self) -> bool:
        return self.user is not None

    def sign_in(self, user: str) -> None:
        if not user:
            raise ValueError("User cannot be empty")
        self.user = user

    def sign_out(self) -> None:
        self.user = None

    def message(self) -> str:
        if self.user:
            return f"\n   You are signed in as {self.user.upper()}\n"
        return(
            "\n   To register or manage EMERGe screens, "
            "please sign in!\n"
        )
