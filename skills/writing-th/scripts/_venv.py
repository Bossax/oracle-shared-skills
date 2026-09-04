"""Locate the skill's own interpreter.

The gate must behave the same whether or not some unrelated project venv happens
to be active in the caller's shell. This repo has several .venv directories; a
gate that only works under one of them is not deterministic.
"""
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent


def venv_python():
    """Path to the skill venv's interpreter, or None if it has not been created."""
    for rel in ("Scripts/python.exe", "bin/python3", "bin/python"):
        p = SKILL_ROOT / ".venv" / rel
        if p.exists():
            return p
    return None


def reexec_if_needed(module="pythainlp"):
    """Re-run this script under the skill venv when `module` is missing here."""
    try:
        __import__(module)
        return
    except ImportError:
        pass

    py = venv_python()
    if py is None:
        print(f"ERROR: {module} is not available and the skill venv is missing.")
        print(f"       Create it:  python -m venv {SKILL_ROOT / '.venv'}")
        print(f"       Then:       {SKILL_ROOT / '.venv'}/Scripts/python -m pip install "
              f"-r {SKILL_ROOT / 'scripts' / 'requirements.txt'}")
        sys.exit(2)

    if Path(sys.executable).resolve() == py.resolve():
        print(f"ERROR: {module} missing from the skill venv itself.")
        print(f"       {py} -m pip install -r {SKILL_ROOT / 'scripts' / 'requirements.txt'}")
        sys.exit(2)

    # subprocess, not os.execv: on Windows execv does not quote arguments that
    # contain spaces, and Thai deliverable filenames routinely do.
    proc = subprocess.run([str(py)] + sys.argv)
    sys.exit(proc.returncode)


def child_python():
    """Interpreter to spawn gate subprocesses with."""
    return str(venv_python() or sys.executable)
