import math

_INVERT: dict[int, int] = {0: 0, 1: 2, 2: 1}


class Planet:

    def __init__(self, planet_id: int, x: float, y: float, owner: int,
                 num_ships: int, growth_rate: int) -> None:
        self.planet_id: int = planet_id
        self.x: float = x
        self.y: float = y
        self.owner: int = owner
        self.num_ships: int = num_ships
        self.growth_rate: int = growth_rate

    def output_info(self) -> str:
        """Format full planet information for visualizer.

        This to be printed at the start of output."""

        return "{},{},{},{},{}".format(self.x, self.y, self.owner,
                                       self.num_ships, self.growth_rate)

    def output_state(self) -> str:
        """Format partial planet information for visualizer.

        This to be printed at every turn."""

        return "{}.{}".format(self.owner, self.num_ships)

    def game_state(self, invert: bool = False) -> str:
        """Format full planet information for game agents."""

        owner = _INVERT[self.owner] if invert else self.owner

        return "P {} {} {} {} {}".format(self.x, self.y, owner, self.num_ships,
                                         self.growth_rate)


class Fleet:

    def __init__(self, owner: int, num_ships: int, source_planet: int,
                 destination_planet: int, total_trip_length: int,
                 turns_remaining: int) -> None:
        self.owner: int = owner
        self.num_ships: int = num_ships
        self.source_planet: int = source_planet
        self.destination_planet: int = destination_planet
        self.total_trip_length: int = total_trip_length
        self.turns_remaining: int = turns_remaining

    def output_state(self) -> str:
        """Format full fleet information for visualizer.

        This to be printed at every turn."""

        return "{}.{}.{}.{}.{}.{}".format(self.owner, self.num_ships,
                                          self.source_planet,
                                          self.destination_planet,
                                          self.total_trip_length,
                                          self.turns_remaining)

    def game_state(self, invert: bool = False) -> str:
        """Format full fleet information for game agents."""

        owner = _INVERT[self.owner] if invert else self.owner

        return "F {} {} {} {} {} {}".format(owner, self.num_ships,
                                            self.source_planet,
                                            self.destination_planet,
                                            self.total_trip_length,
                                            self.turns_remaining)


class PlanetWars:

    def __init__(self, state_string: str) -> None:
        self._planet_list: list[Planet] = []
        self._fleet_list: list[Fleet] = []

        self._parse_state(state_string.strip())

        self._initial_output: str = ":".join(p.output_info()
                                             for p in self._planet_list)
        self._turns_output: list[str] = []

        # adjacency list style table for bot moves
        self._move_table: list[list] = [[0 for _ in self._planet_list]
                                        for _ in self._planet_list]

    def _parse_state(self, state_string: str) -> None:
        for line in state_string.split("\n"):
            if line[0] == "P":
                self._parse_planet(line)
            else:
                self._parse_fleet(line)

    def _parse_planet(self, planet_string: str) -> None:
        # P xCoord yCoord owner numShips growthRate
        tokens: list[str] = planet_string.split()

        self._planet_list.append(
            Planet(planet_id=len(self._planet_list),
                   x=float(tokens[1]),
                   y=float(tokens[2]),
                   owner=int(tokens[3]),
                   num_ships=int(tokens[4]),
                   growth_rate=int(tokens[5])))

    def _parse_fleet(self, fleet_string: str) -> None:
        # F owner numShips sourcePlanet destinationPlanet totalTripLength turnsRemaining
        tokens: list[str] = fleet_string.split()

        self._fleet_list.append(
            Fleet(owner=int(tokens[1]),
                  num_ships=int(tokens[2]),
                  source_planet=int(tokens[3]),
                  destination_planet=int(tokens[4]),
                  total_trip_length=int(tokens[5]),
                  turns_remaining=int(tokens[6])))

    def simulate_turn(self) -> None:
        # process the accumulated moves in the move table
        self._process_moves()

        # three numbers for each planet representing the number of ships for
        # each owner (index is owner).
        ships_count: list[list[int]] = [[0, 0, 0] for _ in self._planet_list]

        # update `ships_count` with planets' ships
        for i, planet in enumerate(self._planet_list):
            planet.num_ships += planet.growth_rate * (planet.owner != 0)
            ships_count[i][planet.owner] = planet.num_ships

        # update fleet distances and update `ships_count`
        # iterate backwards since we're removing elements from the list
        for fleet_index in range(len(self._fleet_list) - 1, -1, -1):
            fleet = self._fleet_list[fleet_index]
            fleet.turns_remaining -= 1

            if fleet.turns_remaining == 0:
                self._fleet_list.pop(fleet_index)
                ships_count[fleet.destination_planet][
                    fleet.owner] += fleet.num_ships

        # do fleet planet interactions
        for i, ships in enumerate(ships_count):
            winner_ships = max(ships)

            if ships.count(winner_ships) == 1:
                winner_id = ships.index(winner_ships)
                ships[winner_id] = 0

                self._planet_list[i].owner = winner_id
                self._planet_list[i].num_ships = winner_ships - max(ships)
            else:
                self._planet_list[i].num_ships = 0

        # update the output list
        self._update_output()

        # clean move table for next turn
        self._move_table: list[list] = [[0 for _ in self._planet_list]
                                        for _ in self._planet_list]

    def _process_moves(self) -> None:
        for source_id, destination_list in enumerate(self._move_table):
            for destination_id, num_ships in enumerate(destination_list):
                if num_ships != 0:
                    distance = self._distance(source_id, destination_id)
                    self._fleet_list.append(
                        Fleet(owner=self._planet_list[source_id].owner,
                              num_ships=num_ships,
                              source_planet=source_id,
                              destination_planet=destination_id,
                              total_trip_length=distance,
                              turns_remaining=distance))

    def _update_output(self) -> None:
        planet_string: str = ",".join(p.output_state()
                                      for p in self._planet_list)
        fleet_string: str = ",".join(f.output_state()
                                     for f in self._fleet_list)
        self._turns_output.append(",".join((planet_string, fleet_string)))

    def get_output(self) -> str:
        """Format full game information for visualizer."""
        return "|".join((self._initial_output, ":".join(self._turns_output)))

    def _distance(self, source_id: int, destination_id: int) -> int:
        source_planet = self._planet_list[source_id]
        destination_planet = self._planet_list[destination_id]
        dx = destination_planet.x - source_planet.x
        dy = destination_planet.y - source_planet.y
        return math.ceil(math.sqrt(dx**2 + dy**2))

    def add_fleet(self, owner: int, source_id: int, destination_id: int,
                  num_ships: int) -> bool:
        """Try to add a fleet by the given arguments.

        Returns True if a fleet was successfully added."""

        try:
            source_planet = self._planet_list[source_id]
            destination_planet = self._planet_list[destination_id]
        except IndexError:
            return False

        if owner != source_planet.owner:
            return False
        if num_ships < 0 or num_ships > source_planet.num_ships:
            return False
        if source_planet == destination_planet or num_ships == 0:
            return True

        self._move_table[source_id][destination_id] += num_ships
        source_planet.num_ships -= num_ships
        return True

    def get_state(self, invert: bool = False) -> str:
        """Format game state information for game agents."""
        planet_string: str = "\n".join(
            p.game_state(invert) for p in self._planet_list)
        fleet_string: str = "\n".join(
            f.game_state(invert) for f in self._fleet_list)
        return "\n".join((planet_string, fleet_string, "go\n"))

    def get_winner(self, force: bool = False) -> int:
        """Check for a winner and return their ID.

        Set force=True to do tie-break on number of ships. This should
        be used when the turn limit is met.

        Return value of 0 means no winner."""

        if force:
            num_ships: list[int] = [0, 0, 0]
            for p in self._planet_list:
                num_ships[p.owner] += p.num_ships
            for f in self._fleet_list:
                num_ships[f.owner] += f.num_ships

            num_ships[0] = num_ships[1] * (num_ships[1] == num_ships[2])
            return num_ships.index(max(num_ships))

        is_alive: list[int] = [0, 0, 0]
        for p in self._planet_list:
            is_alive[p.owner] |= 1
        for f in self._fleet_list:
            is_alive[f.owner] |= 1

        if is_alive[1] + is_alive[2] == 1:
            return 1 if is_alive[1] else 2
        return 0

    def num_turns(self) -> int:
        return len(self._turns_output)
