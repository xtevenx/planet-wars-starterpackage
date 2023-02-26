import queue
import shlex
import subprocess
import threading
import time
import typing


def nothing_handler(_: str) -> None:
    ...


KILL_TIMEOUT: float = 1.0

HANDLER_TYPE = typing.Callable[[str], typing.Any]
THREAD_EXIT: None = None


class Player:

    def __init__(self,
                 command: str,
                 stdin_handler: HANDLER_TYPE = nothing_handler,
                 stdout_handler: HANDLER_TYPE = nothing_handler,
                 stderr_handler: HANDLER_TYPE = nothing_handler,
                 **kwargs) -> None:

        self._process = subprocess.Popen(args=shlex.split(command),
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         universal_newlines=True,
                                         **kwargs)

        self._stdin_handler: HANDLER_TYPE = stdin_handler
        self._stdout_handler: HANDLER_TYPE = stdout_handler
        self._stderr_handler: HANDLER_TYPE = stderr_handler

        self.stdout_queue = queue.Queue()
        self.stderr_queue = queue.Queue()
        self._stdout_thread = threading.Thread(target=self._monitor_stdout)
        self._stderr_thread = threading.Thread(target=self._monitor_stderr)
        self._stdout_thread.start()
        self._stderr_thread.start()

    def stop(self) -> None:
        # I forget why this is neceessary. It's probably something to do with
        # subprocess.Popen running into an error or some sort.
        if not hasattr(self, "_process"):
            return

        try:
            self._process.terminate()
            self._process.wait(timeout=KILL_TIMEOUT)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait()

        self.stdout_queue.put(THREAD_EXIT)
        self.stderr_queue.put(THREAD_EXIT)

    def _monitor_stdout(self) -> None:
        for line in self._process.stdout:
            self.stdout_queue.put(line)
            self._stdout_handler(line)

    def _monitor_stderr(self) -> None:
        for line in self._process.stderr:
            self.stderr_queue.put(line)
            self._stderr_handler(line)

    def send_stdin(self, input_string: str) -> None:
        self._process.stdin.write(input_string)
        self._process.stdin.flush()

        self._stdin_handler(input_string)

    def is_alive(self) -> bool:
        return self._process.poll() is None


class PlayerThread(threading.Thread):
    """Thread to manage input/output with a Player object.

    To kill this thread:
      - Prevent any new calls to _do_turn() by sending THREAD_EXIT to self.input_queue.
      - Stop the current call to _do_turn() by sending THREAD_EXIT to
        self.player.stdout_queue.
    """

    def __init__(self, player: Player) -> None:
        self.player: Player = player

        # We receive items from this queue representing the game engine's inputs.
        self.input_queue = queue.Queue()

        # Float representing the time of the last input.
        self.input_time: float = 0

        # We put items into this queue representing the Player's outputs.
        self.output_queue = queue.Queue()

        # Float representing the time of the last output.
        self.output_time: float = 0

        # Boolean for whether the bot had an error.
        self.had_error: bool = False

        super().__init__(target=self._main_loop)
        self.start()

    def _main_loop(self) -> None:
        while (input_string := self.input_queue.get()) != THREAD_EXIT:
            self.input_time = time.perf_counter()
            output_list = self._do_turn(input_string)

            # Update output_time before pushing the queue to ensure the new
            # time is used in the main thread.
            self.output_time = time.perf_counter()
            self.output_queue.put(output_list)

    def _do_turn(self, input_string: str) -> list[str]:
        output_list: list[str] = []

        try:
            self.player.send_stdin(input_string)
            while (line := self.player.stdout_queue.get()) != THREAD_EXIT:
                line = str(line).strip()
                if line == "go":
                    break

                output_list.append(line)
        except OSError:
            self.had_error = True

        return output_list
