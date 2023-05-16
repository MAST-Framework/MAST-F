import subprocess
import sys


def getopts(options: list = None) -> str:
    opts = []
    for option in options or []:
        if isinstance(option, str):
            opts.append(option)
        elif isinstance(option, (list, tuple)):
            key, val, *_ = option
            opts.append(f"{key} {val}")

    return " ".join(opts)


def decompile(
    dex_path: str, dest_path: str, baksmali_path: str, options: list = None
) -> None:
    if sys.platform in ("win32", "win64"):
        baksmali_path = f"{baksmali_path}.bat"
    else:
        baksmali_path = f"{baksmali_path}.sh"

    try:
        opts = getopts(options)
        cmd = f"{baksmali_path} {dex_path} -o {dest_path} {opts}"
        subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as err:
        raise RuntimeError(err.stderr.decode()) from err


def to_java(dex_dir: str, dex_path: str, dest_path: str, jadx_path: str, options: list = None) -> None:
    if sys.platform in ("win32", "win64"):
        jadx_path = f"{jadx_path}.bat"

    try:
        cmd = f"cd {dex_dir} && {jadx_path} -d {dest_path} {getopts(options)} {dex_path}"
        subprocess.run(
            f"{cmd} && mv {dest_path}/sources/* {dest_path} && rm -rf {dest_path}/sources",
            shell=True,
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as err:
        raise RuntimeError(err.stderr.decode()) from err
