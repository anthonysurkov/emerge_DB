import re
import regex
from dataclasses import dataclass
import questionary
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import HTML

from rnatui import RNA_Prompter

# advanced config
left_target_flank_errornum  = 1
right_target_flank_errornum = 1
linker_loop_errornum        = 1
left_varb_flank_errornum    = 1
right_varb_flank_errornum   = 1
ltf_lookbehind_length       = 2
rtf_lookahead_length        = 2
lvf_lookbehind_length       = 3
rvf_lookahead_length        = 2

"""
# Example using the E198K hairpin sequence:
# 5’-GTTTGTACAAAAAAGCAGGCCCTCTCCCAAGTCCACACATTTGA
# 5'-CCCAGA GAA AGATGAGCC-3'    <- left trgt flank, target, right trgt flank
# 5'-TTTCTTTCTTT-3'             <- linker loop
# 5'-GGCTC NNNNNNNNNN GGGTCA-3' <- left varb flank, variable, right varb flank
# 5'-AATGCCCGTAGAGTCGCTGTTCCTGCCATGGAAAATCGATGTTCTT-3’

trgt = regex.compile(
    r"(?:CCCAGA){e<=1}(?<=GA)([AG]{3})(?=AG)(?:AGATGA){e<=1}"
)
varb = regex.compile(
    r"(?:TTTCTTTCTTT){s<=1}(?:GGCTC){e<=1}"
    r"(?<=CTC)([AGCT]{10})(?=GG)"
    r"(?:GGGTCA){e<=1}"
)
The below patterns generalize this.
"""
def compile_regular_expressions(
    left_target_flank: str,
    left_target_flank_lookbehind: str,
    right_target_flank: str,
    right_target_flank_lookahead: str,
    target_region_length: int,
    linker_loop: str,
    left_varb_flank: str,
    left_varb_flank_lookbehind: str,
    right_varb_flank: str,
    right_varb_flank_lookahead: str,
    varb_region_length: int
) -> tuple[re.Pattern[str], re.Pattern[str]]:
    trgt = regex.compile(
        fr"(?:{left_target_flank}){{e<={left_target_flank_errornum}}}"
        fr"(?<={left_target_flank_lookbehind})"
        fr"([AG]{{{target_region_length}}})"
        fr"(?={right_target_flank_lookahead})"
        fr"(?:{right_target_flank}){{e<={right_target_flank_errornum}}}"
    )
    varb = regex.compile(
        fr"(?:{linker_loop}){{s<={linker_loop_errornum}}}"
        fr"(?:{left_varb_flank}){{e<={left_varb_flank_errornum}}}"
        fr"(?<={left_varb_flank_lookbehind})"
        fr"([AGCT]{{{varb_region_length}}})"
        fr"(?={right_varb_flank_lookahead})"
        fr"(?:{right_varb_flank}){{e<={right_varb_flank_errornum}}}"
    )
    return (trgt, varb)

@dataclass
class RegionSelection:
    substr: str
    idx: tuple[int, int]

BASE_SYSTEM_PROMPT = (
    "Welcome to Anthony's regex helper. Please select the appropriate regions "
    "of your RNA hairpin below.\n\n"
    "Example:\n"
    "...TTTGA<ansicyan>CCCAGA</ansicyan>G<ansibrightblue>A</ansibrightblue>"
    "A<ansiyellow>AGATGA</ansiyellow>GCC"
    "<ansimagenta>TTTCTTTCTTTC</ansimagenta>"
    "<ansigreen>GGCTC</ansigreen>NNNNNNNNNN<ansired>GGGTCA</ansired>AAT...\n"
    "Color key:\n"
    "  <ansicyan>██</ansicyan> Left target flank\n"
    "  <ansiyellow>██</ansiyellow> Right target flank\n"
    "  <ansibrightblue>██</ansibrightblue> Target adenosine\n"
    "  <ansimagenta>██</ansimagenta> Linker loop\n"
    "  <ansigreen>██</ansigreen> Left variable flank\n"
    "  <ansired>██</ansired> Right variable flank\n\n"
    "Note: this system will not double-check the biological validity of your "
    "entry.\n"
    "      This includes screening for potentially nonsensical selections, "
    "such as the left flank being\n"
    "      selected to the right of the right flank.\n"
    "      Be careful!\n"
)
def prompt_for_regex_regions(
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
            ("left target flank", "ltf", "ansicyan"),
            ("right target flank", "rtf", "ansiyellow"),
            ("target adenosine", "At", "ansibrightblue"),
            ("linker loop", "ll", "ansimagenta"),
            ("left variable flank", "lvf", "ansigreen"),
            ("right variable flank", "rvf", "ansired")
        ]

        cursor_pos = None
        for region_label, key, color in regions:
            prompt = (
                base_system_prompt
                + f"\nPlease select the {region_label}.\n"
            )
            prompter = RNA_Prompter(
                rendered_sequence,
                system_prompt=prompt,
                initial_cursor_position=cursor_pos,
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

def prompt_for_regex(
    rna_sequence: str
) -> tuple[re.Pattern[str], re.Pattern[str], str, str]:
    regions = prompt_for_regex_regions(rna_sequence)
    if not regions:
        return None

    ltf_lookbehind = regions["ltf"].substr[-ltf_lookbehind_length:]
    rtf_lookahead  = regions["rtf"].substr[:rtf_lookahead_length]
    lvf_lookbehind = regions["lvf"].substr[-lvf_lookbehind_length:]
    rvf_lookahead  = regions["rvf"].substr[:rvf_lookahead_length]
    varb_length    = regions["rvf"].idx[0] - regions["lvf"].idx[1]

    trgt_left      = regions["ltf"].idx[1]
    trgt_right     = regions["rtf"].idx[0]
    trgt_adenosine = regions["At"].idx
    if trgt_adenosine[1] - trgt_adenosine[0] != 1:
        raise ValueError("Target adenosine region must be of length 1")
    trgt_adenosine = trgt_adenosine[0]

    trgt_length    = trgt_right - trgt_left
    trgt_unedited  = rna_sequence[trgt_left:trgt_right]
    trgt_edited    = (
        rna_sequence[trgt_left:trgt_adenosine] +
        "G" +
        rna_sequence[trgt_adenosine+1:trgt_right]
    )

    regexes = compile_regular_expressions(
        left_target_flank            = regions["ltf"].substr,
        left_target_flank_lookbehind = ltf_lookbehind,
        right_target_flank           = regions["rtf"].substr,
        right_target_flank_lookahead = rtf_lookahead,
        target_region_length         = trgt_length,
        linker_loop                  = regions["ll"].substr,
        left_varb_flank              = regions["lvf"].substr,
        left_varb_flank_lookbehind   = lvf_lookbehind,
        right_varb_flank             = regions["rvf"].substr,
        right_varb_flank_lookahead   = rvf_lookahead,
        varb_region_length           = varb_length
    )
    return (regexes, trgt_unedited, trgt_edited)

