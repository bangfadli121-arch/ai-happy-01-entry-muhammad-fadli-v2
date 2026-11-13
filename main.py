import hashlib
import os
import shutil
import struct
import sys


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    destination = os.path.join(output_dir, "entry.png")

    if not os.path.isfile(source):
        print(f"Error: source file not found: {source}", file=sys.stderr)
        return 1

    try:
        os.makedirs(output_dir, exist_ok=True)
        shutil.copyfile(source, destination)
        source_size = os.path.getsize(source)
        destination_size = os.path.getsize(destination)
        source_hash = sha256(source)
        destination_hash = sha256(destination)
    except OSError as error:
        print(f"Error: could not copy or verify {source} to {destination}: {error}", file=sys.stderr)
        return 1

    if source_size != destination_size or source_hash != destination_hash:
        print(f"Error: copied file verification failed for {destination}", file=sys.stderr)
        return 1

    if source_size > 1048576:
        print(f"Error: source file exceeds the 1048576-byte limit: {source_size} bytes", file=sys.stderr)
        return 1

    try:
        with open(destination, "rb") as file:
            header = file.read(24)
    except OSError as error:
        print(f"Error: could not read copied file {destination}: {error}", file=sys.stderr)
        return 1

    png_signature = b"\x89PNG\r\n\x1a\n"
    if header.startswith(png_signature):
        if len(header) < 24 or header[12:16] != b"IHDR":
            print(f"Error: invalid PNG IHDR header in {destination}", file=sys.stderr)
            return 1
        width, height = struct.unpack(">II", header[16:24])
        if width > 1024 or height > 1024:
            print(f"Error: PNG dimensions exceed 1024x1024: {width}x{height}", file=sys.stderr)
            return 1
    elif not header.startswith(b"\xff\xd8\xff"):
        print(f"Error: copied file is neither a PNG nor a JPEG: {destination}", file=sys.stderr)
        return 1

    print(f"Copied {destination} ({destination_size} bytes, sha256 {destination_hash})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
