import subprocess


def extractrsc(apk_path: str, dest_path: str, apktool_path: str = "apktool") -> None:
    run_apktool_decode(apk_path, dest_path, apktool_path, force=True, sources=False)


def run_apktool_decode(
    apk_path: str,
    dest_path: str,
    apktool_path: str = "apktool",
    force: bool = True,
    sources: bool = True,
    resources: bool = True,
) -> None:
    cmd = [f"{apktool_path} d {apk_path} -o {dest_path}"]
    if force:
        cmd.append("-f")

    if not sources:
        cmd.append("--no-src")

    if not resources:
        cmd.append("--no-res")

    try:
        subprocess.run(" ".join(cmd), shell=True, capture_output=True, check=True)
    except subprocess.CalledProcessError as err:
        raise RuntimeError(err.stderr) from err
