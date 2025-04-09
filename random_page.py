""" 0xffae Pyscript. """

import asyncio
import sqlite3
from dataclasses import dataclass

from js import (  # pylint: disable=E0401
    URLSearchParams,
    console,
    document,
    location,
    prompt,
    window,
)
from pyodide.ffi.wrappers import add_event_listener  # pylint: disable=E0401
from pyscript import when  # pylint: disable=E0401


@dataclass
class Record:
    puid: str
    name: str
    hyperlink: str
    emoji: str
    bytes: str
    mime: str


# pylint: disable=W0613
@when("click", "#new_result_button")
async def new_result_click_handler(event):
    """New result event handler."""
    await random_select(new_puid=True)


@when("click", "#permalink_button")
async def permalink_click_handler(event):
    """Permalink event handler."""
    link = document.getElementById("permalink").value
    url = location.host
    prompt("0xffae permalink", f"{url}?permalink={link}")


@when("click", "#github_button")
async def github_click_handler(event):
    """Goto Github link handler."""
    window.open("https://github.com/ross-spencer/0xffae", "_blank").focus()


@when("click", "#results")
async def result_click_handler(event):
    """Show the original bytes."""
    click_toggle()


@when("click", "#original_button")
async def bytes_click_handler(event):
    """Show the original bytes."""
    click_toggle()


def clear_data():
    """Clear the metadata fields associated with the file input and
    output.
    """
    document.getElementById("resultsMetadata").innerHTML = ""
    document.getElementById("results").innerHTML = ""


def click_toggle():
    """Handle results click toggle."""
    toggle = document.getElementById("original_toggle").value
    if toggle == "off":
        console.log("toggle bytes")
        bytes_data = document.getElementById("bytes_cache").value
        document.getElementById("results").innerHTML = f"<pre>{bytes_data}</pre>"
        document.getElementById("original_toggle").value = "on"
    else:
        console.log("toggle emoji")
        emoji = document.getElementById("emoji_cache").value
        document.getElementById("results").innerHTML = emoji
        document.getElementById("original_toggle").value = "off"


def random_select_callback(event):
    """Wrapper for the file_select function."""
    asyncio.create_task(random_select())


# pylint: disable=C0103,W0603
db_conn = None


async def conn():
    """Create a persistent connection to the database for a session."""
    global db_conn
    if db_conn:
        return db_conn
    db_conn = sqlite3.connect("random.db")
    return db_conn


async def query_db(perma: str) -> Record:
    """Select a random record from the database.

    Columns:
        puid varchar(10) UNIQUE,
        emoji text,
        bytes text,
        name varchar(500),
        hyperlink varchar(255)
    """
    global db_conn
    if not db_conn:
        console.log("getting db connection")
        db_conn = await conn()
    cur = db_conn.cursor()
    if perma:
        cur.execute(
            f"select puid, emoji, bytes, name, mime, hyperlink from data where puid = '{perma}';",
        )
    else:
        cur.execute(
            "select puid, emoji, bytes, name, mime, hyperlink from data order by random() limit 1;",
        )
    res = cur.fetchone()
    return Record(
        name=res[3],
        hyperlink=res[5],
        puid=res[0],
        mime=res[4],
        emoji=res[1],
        bytes=res[2],
    )


async def random_select(new_puid=False):
    """Select something random from a database."""

    qs = URLSearchParams.new(location.search)
    perma = qs["permalink"]
    if new_puid:
        perma = False
    if perma:
        console.log(f"loading: {perma}")

    result = await query_db(perma)

    console.log("getting file format as emoji...")
    clear_data()

    mime = ""
    if not result.mime.lower().startswith("no mime"):
        mime = f"     <b>MIMEType</b>: {result.mime}<br/>"

    hidden = (
        f'<details class="noprint">'
        f"   <summary><ins>guess the format</ins> ▼</summary>"
        f"   <div>"
        f"     <strong><i>{result.puid}</i></strong><br/>"
        f"     <b>name</b>: {result.name}<br/>"
        f"{mime}"
        f'     <b>pronom</b>: <a href="{result.hyperlink}" target="_blank">{result.hyperlink.replace("https://www.", "")}</a><br/><br/>'
        f"   <div>"
        f"</details>"
    )

    document.getElementById("resultsMetadata").innerHTML = hidden
    document.getElementById("results").innerHTML = result.emoji
    document.getElementById("emoji_cache").value = result.emoji
    document.getElementById("bytes_cache").value = result.bytes
    document.getElementById("permalink").value = result.puid


def setup():
    """Create a Python proxy for the callback function if required."""
    add_event_listener(window, "py:all-done", random_select_callback)


if __name__ == "__main__":
    setup()
