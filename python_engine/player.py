import shlex
import subprocess
import time

KILL_TIMEOUT: float = 1.0


def _retrieve_function(stream):
    return lambda: str(stream.readline()).strip()


class Player:
    def __init__(self, command: str) -> None:
        self._process = subprocess.Popen(
            args=shlex.split(command),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        self.last_response: list[str] = []
        self.had_error: bool = False

    def __del__(self) -> None:
        if not hasattr(self, "_process"):
            return

        self._process.terminate()

        timeout_time = time.perf_counter() + KILL_TIMEOUT
        while time.perf_counter() < timeout_time:
            if self._process.poll() is not None:
                break
        else:
            self._process.kill()

    def get_response(self, input_string: str) -> list[str]:
        try:
            return self._get_response(input_string)
        except OSError:
            self.had_error = True
            return []

    def _get_response(self, input_string: str) -> list[str]:
        self._process.stdin.write(input_string)
        self._process.stdin.flush()

        self.last_response = []
        for line in iter(_retrieve_function(self._process.stdout), "go"):
            self.last_response.append(line)
        return self.last_response
