import sys

from planet_wars import PlanetWars
from player import Player

MAP_PATH: str = "./generated.txt"
P1_COMMAND: str = "python ./level2.py"
P2_COMMAND: str = "python ./level3.py"


if __name__ == "__main__":
    with open(MAP_PATH, "r") as fp:
        pw = PlanetWars(fp.read())

    player_one = Player(P1_COMMAND)
    player_two = Player(P2_COMMAND)
    while pw.get_winner() == 0:
        p1_moves = player_one.get_response(pw.get_state())
        p2_moves = player_two.get_response(pw.get_state(invert=True))

        p1_moves_int = [[int(x) for x in line.split()] for line in p1_moves]
        p2_moves_int = [[int(x) for x in line.split()] for line in p2_moves]

        for move in p1_moves_int:
            pw.add_fleet(1, *move)
        for move in p2_moves_int:
            pw.add_fleet(2, *move)

        pw.simulate_turn()

    # this is not strictly necessary, but the official engine does it so the
    # viewers expect it. Or... perhaps there's a bug that I can't find. :/
    pw.simulate_turn()

    sys.stdout.write(pw.get_output())
    sys.stdout.flush()

    sys.stderr.write("done.\n")
    sys.stderr.flush()
