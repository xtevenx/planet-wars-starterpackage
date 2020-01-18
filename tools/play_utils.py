import platform
import subprocess

PYTHON = "python" if platform.system() == "Windows" else "python3"
COMMANDS_LOOKUP = {
    frozenset(("jar",)): "java -jar {}",
    frozenset(("js",)): "node {}",
    frozenset(("pl",)): "perl {}",
    frozenset(("py", "pyc", "pyo")): PYTHON + " {}",
}


def _command_exists(c: str) -> bool:
    status, response = subprocess.getstatusoutput(f"{c} --version")
    return status == 0


def get_command(f: str) -> str:
    ext = f.split(".")[-1]
    for extensions, command in COMMANDS_LOOKUP.items():
        if ext in extensions:
            base_command = command.split()[0]
            if not _command_exists(base_command):
                raise RuntimeError(f"You don't have `{base_command}` installed.")
            return command.format(f)
    else:
        return f"./{f}"
