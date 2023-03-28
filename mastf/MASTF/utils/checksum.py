
import os
import hashlib

def checksum_from_path(file_path: str) -> tuple:
    if not os.path.exists(file_path):
        return None, None, None

    with open(file_path, 'rb', buffering=0) as fp:
        return get_file_cheksum(fp)


def get_file_cheksum(fp) -> tuple:
    """Efficient way to cumpute sha256, sha1 and md5 checksum"""
    fp.seek(0)
    sha256 = hashlib.sha256()
    sha1 = hashlib.sha1()
    md5 = hashlib.md5()

    buf = bytearray(128*1024)
    view = memoryview(buf)
    for chunk in iter(lambda: fp.readinto(view), 0):
        sha256.update(view[:chunk])
        sha1.update(view[:chunk])
        md5.update(view[:chunk])

    return sha256.hexdigest(), sha1.hexdigest(), md5.hexdigest()
