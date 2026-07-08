import subprocess
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent

PYTHON_EXE = BASE_PATH / ".venv" / "Scripts" / "python.exe"
SCRIPT_PATH = BASE_PATH / "inventory_system_v4.py"


def run_inventory_update():

    result = subprocess.run(
        [str(PYTHON_EXE), str(SCRIPT_PATH)],
        capture_output=True,
        text=True
    )

    print("========== INVENTORY UPDATE ==========")
    print("Return Code:", result.returncode)
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)
    print("======================================")

    return result.returncode == 0

def run_inventory_update():

    print(">>> Starting inventory update...")

    result = subprocess.run(
        [str(PYTHON_EXE), str(SCRIPT_PATH)],
        capture_output=True,
        text=True
    )

    print("Return Code:", result.returncode)
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)

    return result.returncode == 0