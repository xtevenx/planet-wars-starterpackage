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
        ...

    def _update_output(self) -> None:
        ...
