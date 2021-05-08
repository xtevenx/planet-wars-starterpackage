import sys
import threading
import time

from planet_wars import PlanetWars
from player import Player


def print_finish(winner: int, reason: str = None):
    if reason:
        sys.stderr.write(f"{reason}\n")

    if winner:
        sys.stderr.write(f"Player {winner} wins!\n")
    else:
        sys.stderr.write("Draw!\n")
    sys.stderr.flush()


def play_game(map_path: str, turn_time: float, max_turns: int, p1_command: str, p2_command: str):
    with open(map_path, "r") as fp:
        pw = PlanetWars(fp.read())

    player_one = Player(p1_command)
    player_two = Player(p2_command)
    while pw.get_winner() == 0 and pw.num_turns() <= max_turns:
        p1_input = pw.get_state()
        p2_input = pw.get_state(invert=True)

        p1_thread = threading.Thread(target=player_one.get_response, args=(p1_input,))
        p2_thread = threading.Thread(target=player_two.get_response, args=(p2_input,))

        p1_thread.start()
        p2_thread.start()

        end_time = time.perf_counter() + turn_time
        p1_thread.join(timeout=end_time - time.perf_counter())
        if p1_thread.is_alive():
            if p2_thread.is_alive():
                print_finish(winner=0, reason="Both players timed out.")
            else:
                print_finish(winner=2, reason="Player 1 timed out.")
            break

        p2_thread.join(timeout=end_time - time.perf_counter())
        if p2_thread.is_alive():
            print_finish(winner=1, reason="Player 2 timed out.")
            break

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

        print_finish(winner=pw.get_winner(force=True))

    sys.stdout.write(pw.get_output())
    sys.stdout.flush()


if __name__ == "__main__":
    play_game(
        map_path="./generated.txt",
        turn_time=1.0,
        max_turns=200,
        p1_command="python ./level2.py",
        p2_command="python ./level3.py"
    )
