-- Author information: author name, author email.
CREATE TABLE author_info(
    author              TEXT PRIMARY KEY,
    email               TEXT NOT NULL
);

-- Targets information:
-- ID (e.g. r255x), full hairpin sequence, edit-A index, edit region start and
-- end, variable region start and end.
CREATE TABLE hairpin_info (
    target_id           TEXT PRIMARY KEY,
    hairpin_seq         TEXT NOT NULL,
    edit_A_idx          INT NOT NULL,
    edit_region_start   INT NOT NULL,
    edit_region_end     INT NOT NULL,
    CHECK (edit_region_start < edit_region_end),
    var_region_start    INT NOT NULL,
    var_region_end      INT NOT NULL,
    CHECK (var_region_start < var_region_end)
);

-- Methods information:
-- ID, path of .py/.R used for method, brief description, full write-up.
CREATE TABLE methods_info (
    method_id           SERIAL PRIMARY KEY,
    method_name         TEXT NOT NULL UNIQUE,
    method_path         TEXT NOT NULL UNIQUE,
    method_desc         TEXT,
    method_writeup_path TEXT
);

-- Screen information:
-- ID, mRNA target ID, author, date of submission for sequencing (approx.),
-- number of reads ordered for sequencing, 5' primer sequence,
-- 3' primer sequence, date of data processing, methods used for data
-- processing.
CREATE TABLE screen_metadata (
    screen_id           SERIAL PRIMARY KEY,
    target_id           TEXT NOT NULL REFERENCES hairpin_info(target_id),
    author              TEXT NOT NULL REFERENCES author_info(author),
    enzyme              TEXT NOT NULL,
    submission_date     TIMESTAMP,
    num_reads_ordered   INT CHECK (num_reads_ordered >= 0),
    primer_seq_5        TEXT NOT NULL,
    primer_seq_3        TEXT NOT NULL,
    processing_date     TIMESTAMP DEFAULT now(),
    rawdata_path        TEXT NOT NULL UNIQUE
);

-- Junction table. Links screen_metadata with methods_info.
-- Position column denotes the order in which methods were applied.
CREATE TABLE screen_methods (
    screen_id           INT NOT NULL REFERENCES screen_metadata(screen_id),
    method_id           INT NOT NULL REFERENCES methods_info(method_id),
    exec_order          INT NOT NULL CHECK (exec_order >= 1),
    PRIMARY KEY (screen_id, exec_order)
);

-- EMERGe data:
-- Row ID, Screen ID, variable sequence screened 5' to 3', sample size n,
-- edited count k, maximum likelihood estimator (mle) of editing.
CREATE TABLE emerge_data (
    id                  SERIAL PRIMARY KEY,
    screen_id           INT NOT NULL REFERENCES screen_metadata(screen_id),
    seq                 TEXT NOT NULL,
    n                   INT NOT NULL CHECK (n >= 0),
    k                   INT NOT NULL CHECK (k >= 0 AND k <= n),
    mle                 FLOAT NOT NULL CHECK (mle >= 0 AND mle <= 1)
);
