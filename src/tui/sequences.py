import questionary
from dataclasses import dataclass
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import HTML

from tui.rnatui import RNA_Prompter
import db.interface as database

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

def register_hairpin():
    tids = get_registered_targets()
    if not tids:
        print("No hairpins/target IDs currently registered.\n")
    else:
        print("Currently registered target IDs:\n")
        print("\n".join(
            f"  {index}. {target_id}"
            for index, target_id in enumerate(tids, start=1)
        ))
    print("\nEnter Ctrl+C at any point to abort\n")

    target_id = questionary.text(
        "Enter your target ID (derivative of the mutation "
        "studied; e.g. `r270x_z`, `r270x`, `r255x`). Please avoid dashes (`-`) "
        "and spaces! "
    ).ask()
    if target_id is None:
        return
    target_id = target_id.lower()

    unconfirmed = True
    while unconfirmed:
        hairpin_seq = questionary.text(
            "Copy-paste your hairpin sequence (no quotes, indents, or "
            "5'- 3'- markers):"
        ).ask()
        if hairpin_seq is None:
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
        f"Target ID: {target_id}\n"
        f"Hairpin sequence: {hairpin_seq}\n"
        f"Edit-A index: {edit_A_idx}\n"
        f"Edit region: {edit_reg_start} through {edit_reg_end}\n"
        f"Variable region: {var_reg_start} through {var_reg_end}\n"
    )
    if questionary.confirm("Confirm?").ask():
        if not database.insert_hairpin_info(target_id, hairpin_seq,
            edit_A_idx, edit_reg_start, edit_reg_end, var_reg_start, var_reg_end
        ):
            print("Hairpin registration failed. Is the target ID already "
                "registered?"
            )
    else:
        return register_sequence()

def get_registered_targets() -> list[str]:
    regis = database.get_target_ids()
    return regis or None

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
