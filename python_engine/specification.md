Within this document, `P` represents the set of all planets and `F` represents
the set of all fleets.

Game state
----------

Each game state is multiple parts, separated by newlines:
  - The first `|P|` are information for the planets:

    ```text
    P xCoord yCoord owner numShips growthRate
    ```

  - The remaining `|F|` are information for the fleets:

    ```text
    F owner numShips sourcePlanet destinationPlanet totalTripLength turnsRemaining
    ```

Move format
-----------

For a player's turn, they send a number of moves, then the string `go`, with
each value separated by a newline. A move is in the following format:

```text
sourcePlanet destinationPlanet numShips
```

Output format
-------------

The output is split into two parts, separated by a pipe character:
  - The first part is the information for the planets. The planets are
    separated by colons and formatted as follows:

    ```text
    x,y,owner,numShips,growthRate
    ```

  - The second part is the information for the turns. The turns are
    separated by colons and formatted as follows:
      - A turn has multiple values separated by commas:
          - The first `|P|` values are information for the planet states:

            ```text
            owner.numShips
            ```

          - The remaining `|F|` values are information for the fleets:

            ```text
            owner.numShips.sourcePlanet.destinationPlanet.totalTripLength.turnsRemaining
            ```

Miscellaneous
-------------

  - The distance between planets is the smallest integer greater than the
    Euclidean distance between the planets' coordinates.
