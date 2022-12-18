import queue
import sys
import time
import typing

import planet_wars
import player


class GameResult:
    def __init__(self, winner: int = None, reason: str = None, output: str = None) -> None:
        # `.winner` can be one of four values: [0, 1, 2] if the game was played
        # without hitches, or None if an error occurred.
        self.winner: int = winner

        # `.reason` is the justification for a game's result (can be None if the
        # game was played without anything extraordinary). If `.winner` is None,
        # `.reason` is instead the error which occurred.
        self.reason: str = reason

        # `.output` is the data which can be used as input for a visualizer.
        self.output: str = output


def init_planet_wars(map_path: str) -> typing.Optional[planet_wars.PlanetWars]:
    try:
        with open(map_path, "r") as fp:
            return planet_wars.PlanetWars(fp.read())
    except FileNotFoundError:
        return None


def init_player(*args, **kwargs) -> typing.Optional[player.Player]:
    try:
        return player.Player(*args, **kwargs)
    except (FileNotFoundError, OSError):
        return None


def add_moves(pw: planet_wars.PlanetWars, move_list: list[str], owner: int) -> typing.Optional[str]:
    for move_string in move_list:
        try:
            assert pw.add_fleet(owner, *(int(x) for x in move_string.split()))
        except (ValueError, TypeError, AssertionError):
            return move_string


def play_game(map_path: str, turn_time: float, max_turns: int, p1_command: str, p2_command: str,
              p1_handler: player.HANDLER_TYPE = player.NO_HANDLER,
              p2_handler: player.HANDLER_TYPE = player.NO_HANDLER) -> GameResult:
    if not (pw := init_planet_wars(map_path)):
        return GameResult(reason="Map file not found.")

    if not (player_one := init_player(p1_command, stderr_handler=p1_handler)):
        return GameResult(reason="Unable to start player one.")

    if not (player_two := init_player(p2_command, stderr_handler=p2_handler)):
        return GameResult(reason="Unable to start player_two")

    p1_thread = player.PlayerThread(player_one)
    p2_thread = player.PlayerThread(player_two)

    result = GameResult()
    while pw.get_winner() == 0 and pw.num_turns() <= max_turns:
        p1_thread.input_queue.put(pw.get_state())
        p2_thread.input_queue.put(pw.get_state(invert=True))

        end_time = time.perf_counter() + turn_time

        try:
            p1_output = p1_thread.output_queue.get(timeout=end_time - time.perf_counter())
            p1_timeout = p1_thread.output_time > end_time or p1_thread.had_error
        except queue.Empty:
            p1_output = []
            p1_timeout = True

        try:
            p2_output = p2_thread.output_queue.get(timeout=end_time - time.perf_counter())
            p2_timeout = p2_thread.output_time > end_time or p2_thread.had_error
        except queue.Empty:
            p2_output = []
            p2_timeout = True

        if p1_timeout or p2_timeout:
            if p1_timeout and p2_timeout:
                result.winner = 0
                result.reason = "Both players timed out."
            elif p1_timeout:
                result.winner = 2
                result.reason = "Player 1 timed out."
            else:
                result.winner = 1
                result.reason = "Player 2 timed out."
            break

        p1_bad_move = add_moves(pw, p1_output, 1)
        p2_bad_move = add_moves(pw, p2_output, 2)

        if p1_bad_move or p2_bad_move:
            if p1_bad_move and p2_bad_move:
                result.winner = 0
                result.reason = "Both players had illegal moves."
            elif p1_bad_move:
                result.winner = 2
                result.reason = f"Player 1 illegal move: \"{p1_bad_move}\""
            else:
                result.winner = 1
                result.reason = f"Player 2 illegal move: \"{p2_bad_move}\""
            break

        pw.simulate_turn()

    else:
        # this is not strictly necessary, but the official engine does it so the
        # viewers expect it. Or... perhaps there's a bug that I can't find. :/
        pw.simulate_turn()

        result.winner = pw.get_winner(force=True)

    player_one.stop()
    player_two.stop()

    p1_thread.input_queue.put(None)
    p2_thread.input_queue.put(None)
    p1_thread.join()
    p2_thread.join()

    result.output = pw.get_output()
    return result


def print_finish(winner: int, reason: str = None) -> None:
    if reason:
        sys.stderr.write(f"{reason}\n")

    if winner is not None:
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

    gr = play_game(
        map_path=arguments.map_path,
        turn_time=arguments.turn_time,
        max_turns=arguments.max_turns,
        p1_command=arguments.player_one,
        p2_command=arguments.player_two,
    )

    print_finish(gr.winner, gr.reason)
    if gr.winner is not None:
        sys.stdout.write(gr.output)
        sys.stdout.flush()
