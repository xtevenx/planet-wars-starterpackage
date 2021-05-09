import sys
import threading
import time

from planet_wars import PlanetWars
from player import Player


class GameResult:
    def __init__(self, winner: int = None, reason: str = None, output: str = None) -> None:
        self.winner: int = winner
        self.reason: str = reason
        self.output: str = output


def play_game(map_path: str, turn_time: float, max_turns: int, p1_command: str, p2_command: str
              ) -> GameResult:
    with open(map_path, "r") as fp:
        pw = PlanetWars(fp.read())

    result = GameResult()

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
                result.winner = 0
                result.reason = "Both players timed out."
            else:
                result.winner = 2
                result.reason = "Player 1 timed out."
            break

        p2_thread.join(timeout=end_time - time.perf_counter())
        if p2_thread.is_alive():
            result.winner = 1
            result.reason = "Player 2 timed out."
            break

        p1_moves = player_one.last_response
        p2_moves = player_two.last_response

        for move_string in p1_moves:
            try:
                assert pw.add_fleet(1, *(int(x) for x in move_string.split()))
            except (ValueError, TypeError, AssertionError):
                result.winner = 2
                result.reason = f"Player 1 illegal move: \"{move_string}\""
                break
        if result.winner:
            break

        for move_string in p2_moves:
            try:
                assert pw.add_fleet(2, *(int(x) for x in move_string.split()))
            except (ValueError, TypeError, AssertionError):
                result.winner = 1
                result.reason = f"Player 2 illegal move: \"{move_string}\""
                break
        if result.winner:
            break

        pw.simulate_turn()

    else:
        # this is not strictly necessary, but the official engine does it so the
        # viewers expect it. Or... perhaps there's a bug that I can't find. :/
        pw.simulate_turn()

        result.winner = pw.get_winner(force=True)

    result.output = pw.get_output()
    return result


def print_finish(winner: int, reason: str = None) -> None:
    if reason:
        sys.stderr.write(f"{reason}\n")

    if winner:
        sys.stderr.write(f"Player {winner} wins!\n")
    else:
        sys.stderr.write("Draw!\n")
    sys.stderr.flush()


if __name__ == "__main__":
    ret = play_game(
        map_path="./generated.txt",
        turn_time=1.0,
        max_turns=200,
        p1_command="python ./level2.py",
        p2_command="python ./level3.py"
    )

    print_finish(ret.winner, ret.reason)
    sys.stdout.write(ret.output)
    sys.stdout.flush()
