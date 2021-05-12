import sys
import threading
import time

import planet_wars
import player


class GameResult:
    def __init__(self, winner: int = None, reason: str = None, output: str = None,
                 error: str = None) -> None:
        self.winner: int = winner
        self.reason: str = reason
        self.output: str = output
        self.error: str = error


def play_game(map_path: str, turn_time: float, max_turns: int, p1_command: str, p2_command: str
              ) -> GameResult:
    result = GameResult()

    try:
        with open(map_path, "r") as fp:
            pw = planet_wars.PlanetWars(fp.read())
    except FileNotFoundError:
        result.error = "Map file not found."
        return result

    try:
        player_one = player.Player(p1_command)
    except FileNotFoundError:
        result.error = "Unable to start player 1."
        return result

    try:
        player_two = player.Player(p2_command)
    except FileNotFoundError:
        result.error = "Unable to start player 2."
        return result

    while pw.get_winner() == 0 and pw.num_turns() <= max_turns:
        p1_input = pw.get_state()
        p2_input = pw.get_state(invert=True)

        p1_thread = threading.Thread(target=player_one.get_response, args=(p1_input,))
        p2_thread = threading.Thread(target=player_two.get_response, args=(p2_input,))

        p1_thread.start()
        p2_thread.start()

        end_time = time.perf_counter() + turn_time
        p1_thread.join(timeout=end_time - time.perf_counter())
        p2_thread.join(timeout=end_time - time.perf_counter())
        p1_timeout = p1_thread.is_alive()
        p2_timeout = p2_thread.is_alive()

        if p1_timeout or player_one.had_error:
            if p2_timeout or player_two.had_error:
                result.winner = 0
                result.reason = "Both players timed out."
            else:
                result.winner = 2
                result.reason = "Player 1 timed out."
            break
        if p2_timeout or player_two.had_error:
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
    import argparse

    parser = argparse.ArgumentParser("Play a Planet Wars game.")
    parser.add_argument(
        "map_path", action="store", type=str, help="path to the map file.")
    parser.add_argument(
        "turn_time", action="store", type=float, help="maximum seconds for each turn.")
    parser.add_argument(
        "max_turns", action="store", type=int, help="maximum number of turns.")
    parser.add_argument(
        "player_one", action="store", type=str, help="command to run the first bot.")
    parser.add_argument(
        "player_two", action="store", type=str, help="command to run the second bot.")
    arguments = parser.parse_args()

    ret = play_game(
        map_path=arguments.map_path,
        turn_time=arguments.turn_time,
        max_turns=arguments.max_turns,
        p1_command=arguments.player_one,
        p2_command=arguments.player_two,
    )

    if ret.error:
        sys.stderr.write(ret.error + "\n")
        sys.stderr.flush()
    else:
        print_finish(ret.winner, ret.reason)
        sys.stdout.write(ret.output)
        sys.stdout.flush()
