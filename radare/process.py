"""Create emoji output using Radare2."""

import asyncio
import io
import logging
import os
import subprocess
import time
from xml.dom.minidom import parse

logger = logging.getLogger(__name__)

logging.basicConfig(
    format="%(asctime)-15s %(levelname)s :: %(filename)s:%(lineno)s:%(funcName)s() :: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level="INFO",
)

# Default to UTC time.
logging.Formatter.converter = time.gmtime


byte_dir = os.path.join(".", "pronom", "skeleton-suite")
sig_file = os.path.join(".", "pronom", "DROID_SignatureFile_V120.xml")


def radare_file(filepath: str, size: int):
    """Run radare emoji output."""
    out = subprocess.run(
        ["r2", "-q", "-c", f"pxe {size}", filepath], capture_output=True, check=False
    )
    out = out.stdout.decode()
    out_stream = io.StringIO(out)
    data = ""
    for b in out_stream:
        normalized = b.split(" ", 1)[1].rsplit("  ", 1)[0].strip()
        data = f"{data}{normalized}"
    return data


async def file_to_bytes(file_path: str) -> str:
    """Convert file to bytes."""
    data_arr = []
    with open(file_path, "rb") as file:
        while True:
            byte = file.read(1)
            if not byte:
                break
            data_arr.append(byte.hex().upper())
    return " ".join(data_arr)


async def process_skeleton_suite():
    """Process the skeleton suite."""
    logging.info("directory: %s", byte_dir)
    streams = {}
    for root, _, files in os.walk(byte_dir):
        for file in files:
            file_path = os.path.join(root, file)
            logger.info("%s: %s", file_path, os.path.exists(file_path))
            emoji_data = ""
            bytes_data = ""
            if os.path.isfile(file_path):
                file_stats = os.stat(file_path)
                emoji_data = radare_file(file_path, file_stats.st_size)
                bytes_data = await file_to_bytes(file_path)
            if "x-fmt" in file:
                name_slice = file.split("-", 3)[:-1]
                puid = f"x-fmt/{name_slice[len(name_slice)-1]}"
            else:
                name_slice = file.split("-", 2)[:-1]
                puid = f"fmt/{name_slice[len(name_slice)-1]}"
            streams[puid] = {"emojis": emoji_data, "bytes": bytes_data}
    return streams


async def process_signature():
    """Process the signature file."""
    with open(sig_file, "r", encoding="utf-8") as pronom_file:
        dom = parse(pronom_file)
    puids = {}
    ff = dom.getElementsByTagName("FileFormat")
    for f in ff:
        name = ""
        puid = ""
        version = ""
        mime = ""
        for item in f.attributes.items():
            try:
                if item[0] == "Name":
                    name = item[1]
                if item[0] == "PUID":
                    puid = item[1]
                if item[0] == "Version":
                    version = item[1]
                if item[0] == "MIMEType":
                    mime = item[1]
            except IndexError:
                continue
        puids[puid] = {"name": name, "version": version, "mime": mime}
    return puids


async def combine_records(puids: dict, puid_data: dict):
    """Combine PRONOM and Radare records.

    Insert based on:
        sqlite3 random.db "
            create table if not exists data
            (
                puid varchar(10),
                emoji text,
                bytes text,
                name varchar(500),
                hyperlink varchar(255)
            );"
    """
    for key, value in puids.items():
        try:
            byte_data = puid_data[key]
            hyperlink = f"https://www.nationalarchives.gov.uk/pronom/{key}"
            name = value["name"]
            if value["version"] != "":
                name = f"{name}: {value["version"]}"
            name = name.replace("'", "''").strip()
            mime = value["mime"].strip()
            if mime == "":
                mime = "no MIMEType recorded"
            print(
                f"sqlite3 random.db "
                f'"insert into data '
                f"(puid, emoji, bytes, name, mime, hyperlink)"
                f" values "
                f'(\'{key}\', \'{byte_data["emojis"]}\', \'{byte_data["bytes"]}\', \'{name}\', \'{mime}\', \'{hyperlink }\');"'
            )
        except KeyError as err:
            logger.info("no entry: '%s', (%s)", key, err)


async def pronom_runner():
    """Process PRONOM data."""
    puids = await process_signature()
    logger.info("puid count: %s", len(puids))
    puid_data = await process_skeleton_suite()
    await combine_records(puids, puid_data)


def main():
    """Primary entry point."""
    asyncio.run(pronom_runner())


if __name__ == "__main__":
    main()
