"""Demo runner with a menu: API server, classic demos, library tour."""

import importlib.util
import os
import runpy
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

from python_material.arrays.custom_sorter import sort_with_bubble_sort
from python_material.arrays.second_largest import find_second_largest
from python_material.common import SortDirection
from python_material.strings.vowel_counter import count_unique_vowels

ROOT = Path(__file__).resolve().parent.parent
API_URL = "http://127.0.0.1:8000"
STARTUP_TIMEOUT = 20.0


def run_classic_demos() -> None:
    """Run the array/string demos (the original non-interactive output)."""
    print(f"Second largest: {find_second_largest([5, 1, 5, 3])}")
    print(f"Sorted: {sort_with_bubble_sort([3, 1, 2], SortDirection.ASCENDING)}")
    print(f"Unique vowels: {count_unique_vowels('Minneapolis')}")


def run_library_tour() -> None:
    """Run the CRUD tour script in-process on a throwaway database."""
    runpy.run_path(str(Path(__file__).resolve().parent / "library_demo.py"))


def _server_deps_ready() -> bool:
    """Return True when fastapi and uvicorn import without installing."""
    return importlib.util.find_spec("fastapi") is not None and (
        importlib.util.find_spec("uvicorn") is not None
    )


def _wait_for_health(proc: subprocess.Popen[str]) -> bool:
    """Poll /health until the server answers, dies, or time runs out."""
    deadline = time.monotonic() + STARTUP_TIMEOUT
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(API_URL + "/health", timeout=2) as resp:
                if resp.status == 200:
                    return True
        except (urllib.error.URLError, OSError, TimeoutError):
            time.sleep(0.5)

    return False


def run_api_server() -> None:
    """Start uvicorn, open the Scalar UI, stop on Enter (always stops)."""
    if not _server_deps_ready():
        print("API server needs: python3 -m pip install -e '.[api]'")
        return

    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src") + ":" + env.get("PYTHONPATH", "")
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "python_material.library.api:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    try:
        if not _wait_for_health(proc):
            print("Server did not start (port 8000 busy?). It is stopped.")
            return
        print(f"Serving at {API_URL} — Scalar UI opening in your browser.")
        webbrowser.open(f"{API_URL}/scalar")
        print("Press Enter to stop the server.")
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            print()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("Server stopped; localhost:8000 is free again.")


def menu() -> None:
    """Loop the demo menu until the user exits (EOF runs classic demos)."""
    while True:
        print("Library demos")
        print("1. Start Library CRUD API (Scalar UI opens; Enter stops it)")
        print("2. Run classic demos (arrays, strings)")
        print("3. Run library CRUD tour (throwaway database)")
        print("0. Exit")
        try:
            choice = input("Choose: ").strip()
        except EOFError:
            run_classic_demos()
            return
        if choice == "1":
            run_api_server()
        elif choice == "2":
            run_classic_demos()
        elif choice == "3":
            run_library_tour()
        elif choice == "0":
            return
        else:
            print(f"Unknown option {choice!r}; try 0-3.")


def main() -> None:
    """Run the available demos."""
    menu()


if __name__ == "__main__":
    main()
