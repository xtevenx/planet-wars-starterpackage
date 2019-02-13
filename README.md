# Planet Wars Starter Package
Note: This challenge has been over for almost a decade; why are you still looking at it?

A round-up of all you need to start the 2010 Google AI Challenge Planet Wars Challenge (hereinafter Planet Wars Challenge) originally run by the University of Waterloo.

## Getting Started
Under `starterbots/` are slimmed down versions of the official starter packages for C++, C#, Java and Python.

Pick your language of choice and copy the contents to the root folder.
What you have is a bot with a very basic strategy.
Look at the file `MyBot.*` (different file extensions depending on programming language) to understand the basic strategy of the bot and how communication with the game engine works.

Look at `SPECIFICATION.md` for the official specifications of the game.

### Playing Games
Included in this starter package are three game playing scripts.
* `play.py` for playing an individual game from a generated map and viewing it.
* `play_all.py` for playing a game on all of the 100 provided maps. This is not recommended because the provided maps were generated with an outdated generator.
* `play_multiple.py` for playing multiple games on generated maps.

To use `play.py`, edit the top of the file under the variables `bot1` and `bot2`.
Those are the bots that are going to play against each other and are in the format of a executable command.

To use `play_all.py`, edit the file the same way as you would `play.py`.

To use `play_multiple.py`, edit the file the same way as you would with `play.py` but you can also edit `NUMBER_GAMES` to set the number of games you want to play.

## Note on Licensing
* The files in `example_bots/`, `maps/`, `starterbots/` and `tools/` were originally released under the Apache License for the Planet Wars Challenge.
* The files in `starterbots/python_starterbot/` have been edited.
* The files in `visualizer/` are from the Planet Wars Challenge (released under the Apache License) and have been edited.
* The file `visualizer/css/Hyades.jpg` is released under the Attribution-ShareAlike Version 2.5 Generic License.
* The file `SPECIFICATION.md` was archived from the original Planet Wars Challenge website and did not state licensing.
* The remainder of the files are released under the GNU General Public License Version 3. See `LICENSE.md` for more information
