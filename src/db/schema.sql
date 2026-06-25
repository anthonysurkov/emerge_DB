-- Author information: author name, author email.
CREATE TABLE author_info(
    author              TEXT PRIMARY KEY,
    email               TEXT
);

-- Targets information:
-- ID (e.g. r255x), full hairpin sequence, edit-A index, edit region start and
-- end, variable region start and end.
CREATE TABLE sequence_info (
    sequence_id         TEXT PRIMARY KEY,
    sequence_seq        TEXT,
    edit_A_idx          INT,
    edit_region_start   INT,
    edit_region_end     INT,
    CHECK (edit_region_start < edit_region_end),
    var_region_start    INT,
    var_region_end      INT,
    CHECK (var_region_start < var_region_end)
);

-- Methods information:
-- ID, path of .py/.R used for method, brief description, full write-up.
CREATE TABLE methods_info (
    method_id           SERIAL PRIMARY KEY,
    method_path         TEXT,
    method_desc         TEXT,
    method_writeup      TEXT
);

-- Screen information:
-- ID, mRNA target ID, author, date of submission for sequencing (approx.),
-- number of reads ordered for sequencing, 5' primer sequence,
-- 3' primer sequence, date of data processing, methods used for data
-- processing.
CREATE TABLE screen_metadata (
    screen_id           SERIAL PRIMARY KEY,
    sequence_id         TEXT REFERENCES sequence_info(sequence_id),
    author              TEXT REFERENCES author_info(author),
    submission_date     TIMESTAMP,
    num_reads_ordered   INT,
    primer_seq_5        TEXT,
    primer_seq_3        TEXT,
    processing_date     TIMESTAMP DEFAULT now(),
    rawdata_path        TEXT UNIQUE
);

-- Junction table. Links screen_metadata with methods_info.
-- Position column denotes the order in which methods were applied.
CREATE TABLE screen_methods (
    screen_id           INT REFERENCES screen_metadata(screen_id),
    method_id           INT REFERENCES methods_info(method_id),
    position            INT
);

-- EMERGe data:
-- Row ID, Screen ID, variable sequence screened 5' to 3', sample size n,
-- edited count k, maximum likelihood estimator (mle) of editing.
CREATE TABLE emerge_data (
    id                  SERIAL PRIMARY KEY,
    screen_id           INT REFERENCES screen_metadata(screen_id),
    seq                 TEXT,
    n                   INT,
    k                   INT,
    mle                 FLOAT
);
