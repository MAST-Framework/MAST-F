import subprocess

def extractrsc(apk_path: str, dest_path: str, apktool_path: str = "apktool") -> None:
    try:
        subprocess.run(f"{apktool_path} d {apk_path} -s -o {dest_path}",
                       capture_output=True, check=True)
    except subprocess.CalledProcessError as err:
        raise RuntimeError(err.stderr) from err
