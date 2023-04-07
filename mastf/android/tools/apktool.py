import subprocess

def decompile(dex_path: str, src_path: str) -> None:
    try:
        subprocess.run(f"apktool d {dex_path} -o {src_path}", 
                       capture_output=True, check=True)
    except subprocess.CalledProcessError as err:
        raise RuntimeError(err.stderr) from err
        