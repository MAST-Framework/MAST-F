import subprocess
import sys


def winpath(prog) -> str:
    return f"{prog}.bat"


def decompile(dex_path: str, dest_path: str, baksmali_path: str, options: dict = None) -> None:
    if sys.platform in ("win32", "win64"):
        baksmali_path = f"{baksmali_path}.bat"
    else:
        baksmali_path = f"{baksmali_path}.sh"

    try:
        opts = " ".join([f"{key} {value}" for key, value in (options or {}).keys()])
        subprocess.run(
            f"{baksmali_path} {dex_path} -o {dest_path} {opts}",
            shell=True,
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as err:
        raise RuntimeError(err.stderr.decode()) from err
