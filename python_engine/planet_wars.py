import math


class Planet:
    def __init__(self, planet_id: int, x: float, y: float, owner: int, num_ships: int,
                 growth_rate: int) -> None:
        self.planet_id: int = planet_id
        self.x: float = x
        self.y: float = y
        self.owner: int = owner
        self.num_ships: int = num_ships
        self.growth_rate: int = growth_rate

    def info(self) -> str:
        return "{},{},{},{},{}".format(
            self.x, self.y, self.owner, self.num_ships, self.growth_rate)

    def state(self) -> str:
        return "{}.{}".format(self.owner, self.num_ships)


class Fleet:
    def __init__(self, owner: int, num_ships: int, source_planet: int, destination_planet: int,
                 total_trip_length: int, turns_remaining: int) -> None:
        self.owner: int = owner
        self.num_ships: int = num_ships
        self.source_planet: int = source_planet
        self.destination_planet: int = destination_planet
        self.total_trip_length: int = total_trip_length
        self.turns_remaining: int = turns_remaining

    def info(self) -> str:
        return "{}.{}.{}.{}.{}.{}".format(
            self.owner, self.num_ships, self.source_planet, self.destination_planet,
            self.total_trip_length, self.turns_remaining)


class PlanetWars:
    def __init__(self, state_string: str) -> None:
        self._planet_list: list[Planet] = []
        self._fleet_list: list[Fleet] = []

        self._parse_state(state_string.strip())

        self._initial_state: str = ":".join(p.info() for p in self._planet_list)
        self._turns_list: list[str] = []

        self._move_table: list[list] = [[0 for _ in self._planet_list] for _ in self._planet_list]

    def _parse_state(self, state_string: str) -> None:
        items = state_string.split("\n")
        for item in items:
            if item[0] == "P":
                self._parse_planet(item)
            else:
                self._parse_fleet(item)

    def _parse_planet(self, planet_string: str) -> None:
        # P xCoord yCoord owner numShips growthRate
        tokens: list[str] = planet_string.split()

        self._planet_list.append(
            Planet(
                planet_id=len(self._planet_list),
                x=float(tokens[1]),
                y=float(tokens[2]),
                owner=int(tokens[3]),
                num_ships=int(tokens[4]),
                growth_rate=int(tokens[5])
            )
        )

    def _parse_fleet(self, fleet_string: str) -> None:
        # F owner numShips sourcePlanet destinationPlanet totalTripLength turnsRemaining
        tokens: list[str] = fleet_string.split()

        self._fleet_list.append(
            Fleet(
                owner=int(tokens[1]),
                num_ships=int(tokens[2]),
                source_planet=int(tokens[3]),
                destination_planet=int(tokens[4]),
                total_trip_length=int(tokens[5]),
                turns_remaining=int(tokens[6])
            )
        )

    def simulate_turn(self) -> None:
        # process the accumulated moves in the move table
        self._process_moves()

        # three numbers for each planet representing the number of ships for
        # each owner (index is owner).
        ships_count: list[list[int, int, int]] = [[0, 0, 0] for _ in self._planet_list]

        # update `ships_count` with planets' ships
        for i, planet in enumerate(self._planet_list):
            planet.num_ships += planet.growth_rate * (planet.owner != 0)
            ships_count[i][planet.owner] = planet.num_ships

        # update fleet distances and update `ships_count`
        for fleet_index in range(len(self._fleet_list) - 1, -1, -1):
            fleet = self._fleet_list[fleet_index]
            fleet.turns_remaining -= 1

            if fleet.turns_remaining == 0:
                self._fleet_list.pop(fleet_index)
                ships_count[fleet.destination_planet][fleet.owner] += fleet.num_ships

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

        # update moves table for next turn
        self._move_table: list[list] = [[0 for _ in self._planet_list] for _ in self._planet_list]

    def _process_moves(self) -> None:
        for source_id, destination_list in enumerate(self._move_table):
            for destination_id, num_ships in enumerate(destination_list):
                if num_ships != 0:
                    distance = self._distance(source_id, destination_id)
                    self._fleet_list.append(
                        Fleet(
                            owner=self._planet_list[source_id].owner,
                            num_ships=num_ships,
                            source_planet=source_id,
                            destination_planet=destination_id,
                            total_trip_length=distance,
                            turns_remaining=distance
                        )
                    )

    def _update_output(self) -> None:
        planet_string: str = ",".join(p.state() for p in self._planet_list)
        fleet_string: str = ",".join(f.info() for f in self._fleet_list)
        self._turns_list.append(",".join((planet_string, fleet_string)))

    def get_output(self) -> str:
        return "|".join((self._initial_state, ":".join(self._turns_list)))

    def _distance(self, source_id: int, destination_id: int) -> int:
        source_planet = self._planet_list[source_id]
        destination_planet = self._planet_list[destination_id]
        dx = destination_planet.x - source_planet.x
        dy = destination_planet.y - source_planet.y
        return math.ceil(math.sqrt(dx ** 2 + dy ** 2))

    def add_fleet(self, owner: int, source_id: int, destination_id: int, num_ships: int) -> bool:
        source_planet = self._planet_list[source_id]
        destination_planet = self._planet_list[destination_id]

        if owner != source_planet.owner or num_ships > source_planet.num_ships:
            return False
        if source_planet == destination_planet or num_ships == 0:
            return True

        self._move_table[source_id][destination_id] += num_ships
        source_planet.num_ships -= num_ships
        return True
