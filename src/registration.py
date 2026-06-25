# basic schema:
# init: check if postgresql server is operational

# Available data:
# - author_info
#   - author, email
# - sequence_info
#   - sequence_id, hairpin_seq, edit_A_idx, edit_region_start, edit_region_end,
#     var_region_start, var_region_end
# - methods_info
#   - method_id, method_path, method_desc, method_writeup
# - screen_metadata
#   - screen_id, sequence_id, author, submission_date, num_reads_ordered,
#     primer_seq_5, primer_seq_3, processing_date, rawdata_path
# - screen_methods
#   - screen_id, method_id, position
# - emerge_data
#   - id, screen_id, seq, n, k, mle

# data dependencies:
# emerge_data needs screen_id [screen_metadata] to be registered.
# screen_metadata needs author [author_info] and sequence_id [sequence_info]
# to be registered.
# then, path:
# [author_info] and [sequence_info] must be filled
# [methods_info] is pre-filled by admin
# then, new screen registration is selected by an author for a sequence_id (e.g. r270x)
# a questionnaire is filled out to populate screen_metadata
# then, the rawdata path is provided and the system analyzes it to produce
# nkmle data

# registration control flow 1: main menu with options to sign in to the system,
# recquisition data, register a new sequence, or register a new screen (signin-locked)
# or `methods management` (tbd)
# NEED: a menu class in core, need functions for registry of author_info
# and sequence_metadata, and need an interface function in db to display avail
# options to the menu + populate new authors/sequences in a controlled way
# --> this will probably live in a main.py

# registration control flow 2: registry of a new screen. selection of an available
# sequence. questionnaire to fill screen_metadata. selection of available methods
# for preprocessing and data mining, if multiple options are available.
# execution of selected methods.

