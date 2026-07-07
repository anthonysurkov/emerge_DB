import html as _html

from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.formatted_text import HTML, to_formatted_text
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style

class _HTMLLexer(Lexer):
    """Lexer that applies prompt_toolkit HTML tag colors to a plain-text buffer.

    Characters that carry a non-empty style are considered 'locked' (not
    selectable).  The set of their buffer positions is exposed as
    ``locked_positions`` so that key bindings can skip over them.
    """

    def __init__(self, html_text: str):
        self._html_text = html_text
        formatted = to_formatted_text(HTML(html_text))
        chars: list[tuple[str, str]] = []
        locked: set[int] = set()
        pos = 0
        for style, text, *_ in formatted:
            for ch in text:
                chars.append((style, ch))
                if style:
                    locked.add(pos)
                pos += 1
        self._chars = chars
        self.locked_positions = locked
        self.plain_text = "".join(ch for _, ch in chars)

        # Map plain-text character index → index in original html_text.
        # Built by scanning html_text and skipping over <tag> spans.
        self._plain_to_html: list[int] = []
        in_tag = False
        for i, ch in enumerate(html_text):
            if ch == "<":
                in_tag = True
            elif ch == ">":
                in_tag = False
            elif not in_tag:
                self._plain_to_html.append(i)

    def html_span(self, plain_start: int, plain_end: int) -> tuple[int, int]:
        """Convert plain-text [start, end) to positions in the original HTML string."""
        n = len(self._html_text)
        hs = self._plain_to_html[plain_start] if plain_start < len(self._plain_to_html) else n
        he = self._plain_to_html[plain_end] if plain_end < len(self._plain_to_html) else n
        return hs, he

    def lex_document(self, document):
        lines: list[list[tuple[str, str]]] = []
        current: list[tuple[str, str]] = []
        for style, ch in self._chars:
            if ch == "\n":
                lines.append(current)
                current = []
            else:
                current.append((style, ch))
        lines.append(current)

        def get_line(lineno: int):
            return lines[lineno] if lineno < len(lines) else []

        return get_line


class RNA_Prompter:
    def __init__(self, rna_sequence: str, system_prompt: str, initial_cursor_position: int | None = None):
        self.rna_sequence = rna_sequence
        self.system_prompt = system_prompt

        self._lexer = _HTMLLexer(rna_sequence)
        locked = self._lexer.locked_positions

        def _step(pos: int, direction: int) -> int:
            """Move one step in direction, then skip any locked positions."""
            pos += direction
            n = len(self._lexer.plain_text)
            while 0 <= pos < n and pos in locked:
                pos += direction
            return max(0, min(pos, n))

        kb = KeyBindings()
        kb.add("c-c")(self._exit)
        kb.add("q")(self._exit)
        kb.add("enter")(self._print_selection)

        # Override movement keys so the cursor never lands on a locked position.
        @kb.add("right", eager=True)
        def _right(event):
            buf = event.current_buffer
            buf.selection_state = None
            buf.cursor_position = _step(buf.cursor_position, 1)

        @kb.add("left", eager=True)
        def _left(event):
            buf = event.current_buffer
            buf.selection_state = None
            buf.cursor_position = _step(buf.cursor_position, -1)

        @kb.add("s-right", eager=True)
        def _shift_right(event):
            buf = event.current_buffer
            if not buf.selection_state:
                buf.start_selection()
            buf.cursor_position = _step(buf.cursor_position, 1)

        @kb.add("s-left", eager=True)
        def _shift_left(event):
            buf = event.current_buffer
            if not buf.selection_state:
                buf.start_selection()
            buf.cursor_position = _step(buf.cursor_position, -1)

        # Start the cursor at the requested position (or 0), skipping locked positions.
        initial_pos = initial_cursor_position if initial_cursor_position is not None else 0
        n = len(self._lexer.plain_text)
        initial_pos = max(0, min(initial_pos, n))
        while initial_pos < n and initial_pos in locked:
            initial_pos += 1

        self.buf = Buffer(
            document=Document(self._lexer.plain_text, cursor_position=initial_pos),
            read_only=True,
        )
        status_control = FormattedTextControl(lambda: self.get_status(self.buf))

        layout = Layout(
            HSplit([
                Window(content=FormattedTextControl(
                    HTML(self.system_prompt)), wrap_lines=True,
                    height=D(preferred=self.system_prompt.count('\n') + 1, max=self.system_prompt.count('\n') + 1)
                ),
                Window(height=1, char="─"),
                Window(height=3,
                    content=BufferControl(
                        buffer=self.buf,
                        lexer=self._lexer,
                    ), wrap_lines=True
                ),
                Window(height=1, char="─"),
                Window(height=1, content=status_control),
            ])
        )
        style = Style.from_dict({
            "": "bg:#1e1e1e #ffffff",
        })
        self.app = Application(
            layout=layout,
            key_bindings=kb,
            full_screen=False,
            style=style,
            mouse_support=True,
        )
        if not self.app:
            raise ValueError("prompt_toolkit Application must be"
                "configured to use `prompt_for_substr` fun"
            )

    def html_span(self, plain_start: int, plain_end: int) -> tuple[int, int]:
        """Convert plain-text indices to positions in the current rendered HTML string."""
        return self._lexer.html_span(plain_start, plain_end)

    def prompt_for_substr(
        self,
        indices: bool = False
    ) -> tuple[str, tuple[int, int]]:
        self.clear_screen()
        result = self.app.run()
        if result is None:
            return None
        start, end = result  # plain-text positions
        # Strip any locked characters that happen to fall inside the span.
        text = "".join(
            ch
            for i, ch in enumerate(self._lexer.plain_text[start:end], start)
            if i not in self._lexer.locked_positions
        )
        return (text, (start, end))

    def get_status(self, buf) -> None:
        sel = self.buf.selection_state
        if sel:
            start = min(sel.original_cursor_position, buf.cursor_position)
            end = max(sel.original_cursor_position, buf.cursor_position)
            selected = buf.text[start:end]
            return HTML(
                f"<b>Selected:</b> <ansiyellow>{_html.escape(repr(selected))}</ansiyellow>  "
                f"<ansibrightgreen>[Enter] lock-in  "
                f"[q/Ctrl-C] quit</ansibrightgreen>"
            )
        pos = buf.cursor_position
        return HTML(
            f"<ansigreen>Cursor: {pos}</ansigreen>  "
            f"<ansibrightgreen>[Shift+arrows] select  "
            f"[q/Ctrl-C] quit</ansibrightgreen>"
        )

    def _print_selection(self, event) -> None:
        sel = self.buf.selection_state
        if sel:
            start = min(sel.original_cursor_position, self.buf.cursor_position)
            end = max(sel.original_cursor_position, self.buf.cursor_position)
            event.app.exit(result=(start, end))

    @staticmethod
    def _exit(event) -> None:
        event.app.exit()

    @staticmethod
    def clear_screen() -> None:
        print("\033[2J\033[H", end="\n")
