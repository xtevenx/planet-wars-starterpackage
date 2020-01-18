import argparse
import os
import subprocess
import sys

import tools.play_utils
import tools.map_generator as map_generator
import tools.map_generator_v2


def generate_map(f):
    if os.path.exists(f):
        response = input(f"File \"{f}\" already exists, do you want to overwrite it [Y/n]: ")
        if response.lower() == "y":
            print(f"Overwriting file \"{f}\".")
            map_generator.save_map(f)
    else:
        map_generator.save_map(f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play a Planet Wars game with a random map.")
    parser.add_argument(
        "--map_file_name", action="store", default="generated.txt",
        type=str, help="file to temporarily store the generated map.", dest="map_file_name")
    parser.add_argument(
        "--delete_map", action="store_true", dest="delete_map",
        help="whether to delete the generated map after playing the game.")
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
        "--log_filename", action="store", default="", type=str,
        help="file to store the game logs.", dest="log_filename")
    parser.add_argument(
        "--manual_commands", action="store_true", dest="manual_commands",
        help="use `player_one` and `player_two` values directly instead of automatically "
             "determining commands from the filenames.")
    parser.add_argument(
        "--no_visualize", action="store_true", dest="no_visualize",
        help="whether to skip running the visualizer after the game is played.")
    parser.add_argument(
        "player_one", action="store", type=str, help="command to run the first bot.")
    parser.add_argument(
        "player_two", action="store", type=str, help="command to run the second bot.")
    arguments = parser.parse_args()

    if not arguments.old_maps:
        map_generator = tools.map_generator_v2
    generate_map(arguments.map_file_name)

    if not arguments.manual_commands:
        player_one = tools.play_utils.get_command(arguments.player_one)
        player_two = tools.play_utils.get_command(arguments.player_two)
    else:
        player_one = arguments.player_one
        player_two = arguments.player_two

    subprocess.call(
        "java -jar tools/PlayGame-1.2.jar {} {} {} \"{}\" \"{}\" \"{}\" {}".format(
            arguments.map_file_name,
            arguments.max_turn_time,
            arguments.max_num_turns,
            arguments.log_filename,
            player_one,
            player_two,
            "" if arguments.no_visualize
            else "| {} visualizer/visualize_locally.py".format(tools.play_utils.PYTHON)
        ),
        stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr,
        shell=True
    )

    if arguments.delete_map:
        os.remove(arguments.map_file_name)
