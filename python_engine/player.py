import shlex
import subprocess
import time

KILL_TIMEOUT: float = 1.0


class Player:
    def __init__(self, command: str) -> None:
        self._process = subprocess.Popen(
            args=shlex.split(command),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

    def __del__(self) -> None:
        self._process.terminate()

        timeout_time = time.perf_counter() + KILL_TIMEOUT
        while time.perf_counter() < timeout_time:
            if self._process.poll() is not None:
                break
        else:
            self._process.kill()

    def get_response(self, input_string: str):
        self._process.stdin.write(input_string)
        self._process.stdin.flush()

        move_list: list[str] = []
        while (line := str(self._process.stdout.readline()).strip()) and line != "go":
            move_list.append(line)
        return move_list
