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
