import pathlib


def copy_files(file_list: str, indir: str, outdir: str):
    """Copy a list of file paths in a file from one directory to the other,
    preserving the paths.""" 
    with open(file_list) as fh:
        for line in fh:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            f_in = pathlib.Path(indir) / line.strip()
            f_out = pathlib.Path(outdir) / line.strip()
            f_out.parent.mkdir(parents=True, exist_ok=True)
            f_out.write_text(f_in.read_text())
