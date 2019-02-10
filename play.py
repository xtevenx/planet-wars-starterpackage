import os

from tools import map_generator

map_generator.generate_map()

bot1 = "python starterbots/python_starterbot/MyBot.py"
bot2 = "java -jar example_bots/DualBot.jar"

os.system(f"java -jar tools/PlayGame.jar maps/generated.txt 1000 200 \"\" \"{bot1}\" \"{bot2}\" " +
          "| python visualizer/visualize_locally.py")
