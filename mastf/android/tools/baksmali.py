import subprocess
import sys



def decompile(dex_path: str, dest_path: str, baksmali_path: str, options: list = None) -> None:
    if sys.platform in ("win32", "win64"):
        baksmali_path = f"{baksmali_path}.bat"
    else:
        baksmali_path = f"{baksmali_path}.sh"

    try:
        opts = []
        for option in options or []:
            if isinstance(option, str):
                opts.append(option)
            elif isinstance(option, (list, tuple)):
                key, val, *_ = option
                opts.append(f"{key} {val}")

        opts = " ".join(opts)
        cmd = f"{baksmali_path} {dex_path} -o {dest_path} {opts}"
        subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as err:
        raise RuntimeError(err.stderr.decode()) from err
