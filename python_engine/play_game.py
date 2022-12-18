import queue
import sys
import time

import planet_wars
import player

# Amount of seconds to wait extra to prevent illegitimate timeouts.
TIMEOUT_LEEWAY: float = 0.1


class GameResult:

    def __init__(self,
                 winner: int | None = None,
                 reason: str | None = None,
                 output: str | None = None) -> None:

        # Can be one of four values: [0, 1, 2] if the game was played out
        # normally, or None if an error occurred.
        self.winner: int | None = winner

        # The justification for a game's result: None if the game was played
        # out normally. If self.winner is None, this should not be None.
        self.reason: str | None = reason

        # The string which can be used as input for a visualizer.
        # This is none when the instance is created. It should be set in the
        # play_game() function before it is returned.
        self.output: str | None = output


def init_planet_wars(map_path: str) -> planet_wars.PlanetWars | None:
    """Initialize a PlanetWars instance on a map file.

    Returns None if the map file could not be found or opened."""

    try:
        with open(map_path) as fp:
            return planet_wars.PlanetWars(fp.read())
    except (FileNotFoundError, OSError):
        return None


def init_player(*args, **kwargs) -> player.Player | None:
    """Initialize a Player instance for a certain command.

    Returns None if the command could not be executed."""

    try:
        return player.Player(*args, **kwargs)
    except (FileNotFoundError, OSError):
        return None


def add_moves(pw: planet_wars.PlanetWars, move_list: list[str],
              owner: int) -> str | None:
    """Add a set of moves to a PlanetWars instance.

    Returns a line if there was an error trying to add that fleet."""

    for move_string in move_list:
        try:
            assert pw.add_fleet(owner, *map(int, move_string.split()))
        except (ValueError, TypeError, AssertionError):
            return move_string


def play_game(
        map_path: str,
        turn_time: float,
        max_turns: int,
        p1_command: str,
        p2_command: str,
        p1_handler: player.HANDLER_TYPE = player.nothing_handler,
        p2_handler: player.HANDLER_TYPE = player.nothing_handler
) -> GameResult:
    """Play a game of Planet Wars!

    turn_time is in seconds.

    p1_command and p2_command should be shell commands starting the two players
    respectively.

    p1_handler and p2_handler are passed as stderr handlers for the two players
    respectively. They can take a string (a line of stderr for some game agent)
    and do something to process it.
    """

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
        # Putting something in the queue should make the thread pass it to the
        # player programs and start the turn.
        p1_thread.input_queue.put(pw.get_state())
        p2_thread.input_queue.put(pw.get_state(invert=True))

        turn_end = time.perf_counter() + TIMEOUT_LEEWAY

        try:
            block_duration = max(TIMEOUT_LEEWAY,
                                 turn_end - time.perf_counter())
            p1_output = p1_thread.output_queue.get(timeout=block_duration)
            p1_timeout = p1_thread.output_time - p1_thread.input_time > turn_time
        except queue.Empty:
            p1_timeout = True

        try:
            block_duration = max(TIMEOUT_LEEWAY,
                                 turn_end - time.perf_counter())
            p2_output = p2_thread.output_queue.get(timeout=block_duration)
            p2_timeout = p2_thread.output_time - p2_thread.input_time > turn_time
        except queue.Empty:
            p2_timeout = True

        p1_timeout = p1_timeout or p1_thread.had_error
        p2_timeout = p2_timeout or p2_thread.had_error

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

        p1_illegal_move = add_moves(pw, p1_output, 1)
        p2_illegal_move = add_moves(pw, p2_output, 2)

        if p1_illegal_move or p2_illegal_move:
            if p1_illegal_move and p2_illegal_move:
                result.winner = 0
                result.reason = "Both players had illegal moves."
            elif p1_illegal_move:
                result.winner = 2
                result.reason = f'Player 1 illegal move: \"{p1_illegal_move}\"'
            else:
                result.winner = 1
                result.reason = f'Player 2 illegal move: \"{p2_illegal_move}\"'
            break

        pw.simulate_turn()

    else:
        # This is not strictly necessary, but the official engine does it so
        # the viewers expect it. Or perhaps there's a bug that I can't find. :/
        # pw.simulate_turn()

        result.winner = pw.get_winner(force=True)

    # Send the exit signal to the PlayerThread._main_loop().
    p1_thread.input_queue.put(player.THREAD_EXIT)
    p2_thread.input_queue.put(player.THREAD_EXIT)

    # This sends the exit signal to the PlayerThread._do_turn().
    player_one.stop()
    player_two.stop()

    # Join the PlayerThread objects. This, along with the two blocks of code above,
    # should be done in the order given here. See PlayerThread documentation for more
    # information.
    p1_thread.join()
    p2_thread.join()

    result.output = pw.get_output()
    return result


def print_finish(winner: int | None, reason: str | None = None) -> None:
    if reason is not None:
        sys.stderr.write(f"{reason}\n")

    if winner is not None:
        if winner != 0:
            sys.stderr.write(f"Player {winner} wins!\n")
        else:
            sys.stderr.write("Draw!\n")
    sys.stderr.flush()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("Play a Planet Wars game.")
    parser.add_argument("map_path",
                        action="store",
                        type=str,
                        help="path to the map file.")
    parser.add_argument("turn_time",
                        action="store",
                        type=float,
                        help="maximum seconds for each turn.")
    parser.add_argument("max_turns",
                        action="store",
                        type=int,
                        help="maximum number of turns.")
    parser.add_argument("player_one",
                        action="store",
                        type=str,
                        help="command to run the first bot.")
    parser.add_argument("player_two",
                        action="store",
                        type=str,
                        help="command to run the second bot.")
    arguments = parser.parse_args()

    gr = play_game(
        map_path=arguments.map_path,
        turn_time=arguments.turn_time,
        max_turns=arguments.max_turns,
        p1_command=arguments.player_one,
        p2_command=arguments.player_two,
    )

    print_finish(gr.winner, gr.reason)
    if gr.output is not None:
        sys.stdout.write(gr.output)
        sys.stdout.flush()
