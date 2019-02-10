import os
import subprocess

bot1 = "python starterbots/python_starterbot/MyBot.py"
bot2 = "java -jar example_bots/DualBot.jar"

win_track_list = [0, 0]

for map_number in range(100):
    command = f"java -jar tools/PlayGame-1.2.jar maps/map{map_number + 1}.txt 1000 200 \"\" \"{bot1}\" \"{bot2}\""

    print("Map", map_number + 1, end=" --> ")
    process = subprocess.Popen(command, stdout=open(os.devnull, "w+"), stderr=subprocess.PIPE)

    output_line = process.stderr.readline().decode().strip()
    while output_line.split()[0] not in ("Player", "Draw!"):
        output_line = process.stderr.readline().decode().strip()

    print(output_line)

    output_line_as_list = output_line.split()
    if output_line_as_list[0] == "Player":
        win_track_list[int(output_line_as_list[1]) - 1] += 1
    else:
        win_track_list[0] += 0.5
        win_track_list[1] += 0.5

    process.kill()

print(win_track_list)
