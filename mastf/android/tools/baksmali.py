import subprocess
import sys

def winpath(prog) -> str:
    return f"{prog}.bat"


def decompile(dex_path: str, dest_path: str, baksmali_path: str) -> None:
    if sys.platform in ('win32', 'win64'):
        baksmali_path = winpath(baksmali_path)
    
    try:
        subprocess.run(f"{baksmali_path} {dex_path} -o {dest_path}",
                       capture_output=True, check=True)
    except subprocess.CalledProcessError as err:
        raise RuntimeError(err.stderr) from err
