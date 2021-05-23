import queue
import shlex
import subprocess
import threading
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

        self.stdout_queue = queue.Queue()
        self.stderr_queue = queue.Queue()
        self._stdout_thread = threading.Thread(target=self._monitor_stdout, daemon=True)
        self._stderr_thread = threading.Thread(target=self._monitor_stderr, daemon=True)
        self._stdout_thread.start()
        self._stderr_thread.start()

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

    def _monitor_stdout(self) -> None:
        for line in self._process.stdout:
            self.stdout_queue.put(line)

    def _monitor_stderr(self) -> None:
        for line in self._process.stderr:
            self.stderr_queue.put(line)

    def send_stdin(self, input_string: str) -> None:
        self._process.stdin.write(input_string)
        self._process.stdin.flush()


class TurnThread(threading.Thread):
    def __init__(self, player: Player, input_string: str) -> None:
        self.output_list: list[str] = []
        self.had_error: bool = False

        super().__init__(target=self._do_turn, args=(player, input_string), daemon=True)
        self.start()

    def _do_turn(self, player: Player, input_string: str) -> None:
        try:
            player.send_stdin(input_string)
            while (line := str(player.stdout_queue.get(block=True, timeout=None)).strip()) != "go":
                self.output_list.append(line)
        except OSError:
            self.had_error = True
