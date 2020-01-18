import argparse
import os
import shlex
import subprocess

import tools.play_utils
import tools.map_generator as map_generator
import tools.map_generator_v2

GAME_ENGINE_COMMAND = "java -jar tools/PlayGame-1.2.jar"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Play multiple Planet Wars games with a random maps.")
    parser.add_argument(
        "--old_maps", action="store_true", dest="old_maps",
        help="whether to generate maps using the old map generator.")
    parser.add_argument(
        "--max_turn_time", action="store", default=1000, type=int,
        help="maximum time (in ms) that a bot can have on its turn.", dest="max_turn_time")
    parser.add_argument(
        "--max_num_turns", action="store", default=200, type=int,
        help="maximum number of turns that a game can last.", dest="max_num_turns")
    parser.add_argument(
        "--manual_commands", action="store_true", dest="manual_commands",
        help="use `player_one` and `player_two` values directly instead of automatically "
             "determining commands from the filenames.")
    parser.add_argument(
        "player_one", action="store", type=str, help="command to run the first bot.")
    parser.add_argument(
        "player_two", action="store", type=str, help="command to run the second bot.")
    parser.add_argument(
        "number_games", action="store", type=int, help="number of games to play.")
    arguments = parser.parse_args()

    if not arguments.old_maps:
        map_generator = tools.map_generator_v2

    if not arguments.manual_commands:
        player_one = tools.play_utils.get_command(arguments.player_one)
        player_two = tools.play_utils.get_command(arguments.player_two)
    else:
        player_one = arguments.player_one
        player_two = arguments.player_two

    """ Play the games below! Very cool!"""

    # (draw, bot one, bot two)
    result_tracker_list = [0, 0, 0]

    for game_number in range(arguments.number_games):
        map_path = f"maps/multiple{game_number + 1}.txt"
        map_generator.save_map(map_path)
        command = "{} {} {} {} \"\" \"{}\" \"{}\"".format(
            GAME_ENGINE_COMMAND, map_path, arguments.max_turn_time, arguments.max_num_turns,
            player_one, player_two
        )

        result = subprocess.run(
            shlex.split(command), stdout=open(os.devnull, "w+"), stderr=subprocess.PIPE
        )

        verdict = result.stderr.decode().strip().split("\n")[-1]
        if verdict.count(" ") == 2:
            result_tracker_list[int(verdict.split(" ")[1])] += 1
        else:
            result_tracker_list[0] += 1

        print(f"Game {game_number + 1} verdict: {verdict}", end="  ")
        print(f"(+{result_tracker_list[1]}={result_tracker_list[0]}-{result_tracker_list[2]})")

    print("---")
    print(f"  Player 1 wins: {result_tracker_list[1]}")
    print(f"  Player 2 wins: {result_tracker_list[2]}")
    print(f"  Draws: {result_tracker_list[0]}")
