import os

from tools import map_generator_v2 as map_generator

map_generator.save_map("maps/generated.txt")

bot1 = "python starterbots/python_starterbot/MyBot.py"
bot2 = "java -jar example_bots/DualBot.jar"

os.system(f"java -jar tools/PlayGame-1.2.jar maps/generated.txt 1000 200 \"\" \"{bot1}\" \"{bot2}\" " +
          "| python visualizer/visualize_locally.py")
