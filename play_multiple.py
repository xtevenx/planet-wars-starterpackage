import os
import subprocess

import tools.map_generator_v2 as map_generator

bot1 = "python starterbots/python_starterbot/MyBot.py"
bot2 = "java -jar example_bots/DualBot.jar"

NUMBER_GAMES = 1000

result_tracker_list = [0, 0, 0]

for map_number in range(NUMBER_GAMES):
    map_generator.save_map("maps/generated.txt")
    command = f"java -jar tools/PlayGame-1.2.jar maps/generated.txt 1000 200 \"\" \"{bot1}\" \"{bot2}\""

    print("Map", map_number + 1, end=" --> ")
    process = subprocess.Popen(command, stdout=open(os.devnull, "w+"), stderr=subprocess.PIPE)

    output_line = process.stderr.readline().decode().strip()
    while output_line.split()[0] not in ("Player", "Draw!"):
        output_line = process.stderr.readline().decode().strip()

    print(output_line)

    output_line_as_list = output_line.split()
    if output_line_as_list[0] == "Player":
        result_tracker_list[int(output_line_as_list[1]) - 1] += 1
    else:
        result_tracker_list[2] += 1

    process.kill()

to_percent_factor = 100 / NUMBER_GAMES
result_tracker_list = tuple(map(lambda n: round(to_percent_factor * n, 2), result_tracker_list))

print(f"Player 1 win: {result_tracker_list[0]}%")
print(f"Player 2 win: {result_tracker_list[1]}%")
print(f"Draw: {result_tracker_list[2]}%")
