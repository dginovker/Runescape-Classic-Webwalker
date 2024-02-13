# RSC Webwalker

![Image showing nodes around Gnome Stronghold entrance](https://i.imgur.com/J0m93lq.png)

GUI program for generating a `graph.txt` of traversable paths around Runescape Classic.

Very useful for writing highly efficient bot walking APIs that can go anywhere in the map.

## Features

* Load the RSC map (that was shamelessly stolen from APOS)
* Load the existing graph.json
* Plant nodes and edges
* Label edges (in case you need custom code besides just "walkTo" to go between two nodes, i.e open a Gate, use a Ladder)

## Hotkeys

* Arrowkeys to move around the map
* `+` and `-` to zoom
* `Esc` to deselect the currently selected node

## How to run

* `pip install -r requirements.txt`
* `python webwalk_editor.py`

## How to use with a Bot Client

* I plan to add this manually to APOS and IdleRSC. Simply use their `walkTowards` API method (todo)
* If you want to integrate this manually, 1. Parse `graph.txt` (I kept it as simple as possible) 2. Find a node in the graph you can walk to from your start 3. Astar until you get close to the end 4. Walk to your end position. You will also need to implement custom handlers for all the labeled edges, since those edges probably need custom logic
