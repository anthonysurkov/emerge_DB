from process.mining.regex.ngsregex import regex_main

def main():
    """
    # Prior regex used to data mine for R270XZ NGS data:
    trgt = regex.compile(
        r"(?:GGGCTG){e<=1}(?<=TG)([AG]{3})(?=GC)(?:GCCGGG){e<=1}"
    )
    varb = regex.compile(
        r"(?:TTTCTTTCTTTC){s<=1}(?:CCCG){e<=1}"
        r"(?<=CG)([AGCT]{9})(?=CC)"
        r"(?:CCCGTTTG){e<=1}
    """
    rna_sequence = ("GTTTGTACAAAAAAGCAGGCCCTCTCCCAAGTCCACACAGAA"
        "CGGGGCTGAAAGCCGGGTTTCTTTCTTTCCCCGNNNNNNNNNCCCGTTTGCC"
        "CGTAGAGTCGCTGTTCCTGCCATGGAAAATCGATGTTCTT" # R270XZ
    )
    infile = "tests/regex_sys/r270x_z_chunk.fastq"

    df = regex_main(rna_sequence, infile, minimum_reads=0)
    print(df)
    df.to_csv("r270xz_chunk_automated.csv")

if __name__ == "__main__":
    main()
