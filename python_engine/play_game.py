import sys
import threading
import time

from planet_wars import PlanetWars
from player import Player

MAP_PATH: str = "./generated.txt"
P1_COMMAND: str = "python ./level2.py"
P2_COMMAND: str = "python ./level3.py"

MAX_TURNS: int = 200
MOVE_TIME: float = 1.0


def print_finish(winner: int, reason: str = None):
    if reason:
        sys.stderr.write(f"{reason}\n")
    sys.stderr.write(f"Player {winner} wins!\n")
    sys.stderr.flush()


if __name__ == "__main__":
    with open(MAP_PATH, "r") as fp:
        pw = PlanetWars(fp.read())

    player_one = Player(P1_COMMAND)
    player_two = Player(P2_COMMAND)
    while pw.get_winner() == 0 and pw.num_turns() <= MAX_TURNS:
        p1_input = pw.get_state()
        p2_input = pw.get_state(invert=True)

        p1_thread = threading.Thread(target=player_one.get_response, args=(p1_input,))
        p2_thread = threading.Thread(target=player_two.get_response, args=(p2_input,))

        p1_thread.start()
        p2_thread.start()

        end_time = time.perf_counter() + MOVE_TIME
        p1_thread.join(timeout=end_time - time.perf_counter())
        if p1_thread.is_alive():
            # todo: handle player one (possibly both players) timed out...
            ...
        p2_thread.join(timeout=end_time - time.perf_counter())
        if p2_thread.is_alive():
            # todo: handle player two timed out...
            ...

        p1_moves = player_one.last_response
        p2_moves = player_two.last_response

        illegal_move = False
        for move_string in p1_moves:
            try:
                assert pw.add_fleet(1, *(int(x) for x in move_string.split()))
            except (ValueError, TypeError, AssertionError):
                print_finish(winner=2, reason=f"Player 1 illegal move: \"{move_string}\"")
                illegal_move = True
                break
        if illegal_move:
            break

        for move_string in p2_moves:
            try:
                assert pw.add_fleet(2, *(int(x) for x in move_string.split()))
            except (ValueError, TypeError, AssertionError):
                print_finish(winner=1, reason=f"Player 2 illegal move: \"{move_string}\"")
                illegal_move = True
                break
        if illegal_move:
            break

        pw.simulate_turn()

    else:
        # this is not strictly necessary, but the official engine does it so the
        # viewers expect it. Or... perhaps there's a bug that I can't find. :/
        pw.simulate_turn()

        if win_id := pw.get_winner(force=True):
            print_finish(winner=pw.get_winner())
        else:
            sys.stderr.write("Draw!\n")
            sys.stderr.flush()

    sys.stdout.write(pw.get_output())
    sys.stdout.flush()
