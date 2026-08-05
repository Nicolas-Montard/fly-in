*This project has been created as part of the 42 curriculum by nmontard.*
 
# Fly-In
 
## Description
 
Fly-In is a drone fleet simulator: given a text description of a
map (hubs, zones, and the connections between them), the program
computes the shortest, safest path from a starting point to a goal,
then simulates a fleet of drones following that path turn by turn,
while respecting per-zone and per-connection capacity limits and
movement costs. The simulation is rendered live in a graphical
window built with `pygame`.
 
The project is split into three main stages:
 
1. **Parsing** — reading and strictly validating a custom map file
   format, turning it into a graph of hubs and connections.
2. **Pathfinding** — computing the lowest-cost path from the start
   hub to the end hub with a Dijkstra-based algorithm that accounts
   for zone-specific movement costs and impassable zones.
3. **Simulation & visualization** — moving every drone along the
   computed path turn by turn, enforcing capacity constraints along
   the way, and rendering the whole process in real time.
## Instructions
 
### Requirements
 
- Python 3.10 (or later)
- [`pydantic`](https://docs.pydantic.dev/) — data validation for the
  graph's domain models
- [`pygame`](https://www.pygame.org/) — real-time visualization
Install the dependencies:
 
```bash
make install
```
 
### Running the program
 
```bash
make run
```
 
The program will prompt for a map file path:
 
```
Map name (including path): maps/easy_level_1.txt
```
 
If the map is valid and the goal is reachable, a `pygame` window
opens and the simulation starts automatically.
 
### Controls
 
| Key           | Effect                                   |
|---------------|-------------------------------------------|
| `↑` (Up)      | Speed up the simulation (up to 60 turns/s) |
| `↓` (Down)    | Slow down the simulation (down to 1 turn/s)|
| `Esc`         | Close the program                         |
| Window close  | Close the program                         |
 
Once every drone has reached the goal, the window stays open (the
simulation is paused on the final frame) until manually closed.
 
### Map file format
 
A map is a plain text file, parsed line by line. Comments start
with `#` and are ignored, as are blank lines.
 
```
nb_drones: <int>
 
start_hub: <name> <x> <y> [metadata]
end_hub: <name> <x> <y> [metadata]
hub: <name> <x> <y> [metadata]
 
connection: <name1>-<name2> [metadata]
```
 
- The first non-comment line must declare `nb_drones`.
- Exactly one `start_hub` and one `end_hub` must be defined.
- Hub names must be unique and may not contain dashes or spaces
  (dashes are reserved as the separator in `connection:` lines).
- Metadata is optional, enclosed in `[...]`, and written as
  `key=value` pairs separated by spaces, in any order:
  - Hubs: `zone` (`normal` | `blocked` | `restricted` | `priority`,
    default `normal`), `color` (any pygame color name, default
    `black`), `max_drones` (default `1`, ignored on `start_hub`/
    `end_hub`).
  - Connections: `max_link_capacity` (default `1`).
- Connections are bidirectional; `a-b` and `b-a` are considered
  duplicates and are rejected.
Any malformed line raises a parsing error naming the offending line
number and the cause.
 
## Algorithm choices and implementation strategy
 
### Domain model
 
The graph is built from a small set of `pydantic` models — `Hub`,
`Connection`, `Drone` — which gives strict runtime validation of
every field (types, allowed zone values, positive capacities) for
free, instead of hand-writing that validation throughout the
codebase. `Graph` ties everything together and exposes the
operations the rest of the program needs: looking up a hub by name,
listing a hub's neighbors, finding the connection between two hubs,
and moving a drone from one location to another while keeping
occupancy counts consistent.
 
### Parsing
 
The parser (`Parser`) reads the map file once, line by line,
validating as it goes rather than in a separate pass — a
`connection:` line, for instance, can only reference hubs that were
*already* defined earlier in the file, which the sequential design
enforces naturally. Every failure raises a single custom exception,
`ParsingError`, carrying the line number and a human-readable
explanation, so the very first mistake in a map file is reported
precisely instead of surfacing as a generic crash. Once the file has
been fully validated, `build_graph()` turns the intermediate,
loosely-typed data into the actual `Hub`/`Connection`/`Drone`
objects the simulation runs on.
 
### Pathfinding
 
`Pathfinder` implements Dijkstra's algorithm over the graph. Instead
of a uniform edge weight, the cost of *entering* a hub depends on
its zone type:
 
| Zone         | Cost   | Notes                                             |
|--------------|--------|----------------------------------------------------|
| `normal`     | 1      | Standard movement.                                 |
| `priority`   | 0.99   | Same practical cost as `normal`, tie-broken in favor of priority zones when routes are otherwise equal. |
| `restricted` | 2      | Costs an extra turn; modeled as a two-step move (see below). |
| `blocked`    | —      | Never entered; skipped entirely during the search.  |
 
The algorithm also treats a hub or connection at full capacity as
temporarily unusable for that pass, so a path is only considered
valid if it actually has room to be walked, not just a low cost. If
the goal is unreachable — whether due to `blocked` zones or a graph
that is simply disconnected — the pathfinder returns `None`, and the
simulation reports the map as unsolvable instead of starting.
 
### Simulation
 
All drones follow the *same* precomputed shortest path, advancing
one step per simulation turn. A `restricted` zone takes two turns to
enter: on the first turn the drone moves onto the `Connection`
object linking the two hubs (an intermediate, drawable location in
its own right), and only on the second turn does it land on the
destination hub — mirroring the "costs 2 turns" rule from the map
format directly in the simulation's state machine rather than just
in the pathfinding cost. Capacity limits on hubs and connections are
re-checked at the moment of each move, so a drone will wait rather
than overfill a bottleneck, even though the path itself was computed
assuming free capacity.
 
Simulation speed and rendering are deliberately decoupled: the
`pygame` event loop runs at a fixed high frame rate regardless of
how many simulation turns happen per second, using a delta-time
accumulator to trigger a turn only once enough real time has passed.
This keeps keyboard input (speed changes, quitting) responsive even
when the simulation itself is running slowly at 1 turn per second.
 
## Visual representation
 
The `Visualizer` renders the graph's map coordinates onto a fixed
`pygame` window, scaling and centering the layout automatically so
that maps of very different shapes and densities (a single straight
line, a sprawling maze, a wide grid) all fit and stay centered
rather than being pinned to one corner.
 
- **Hubs** are drawn as colored circles (using each hub's declared
  `color`, or black as a safe fallback for invalid color names),
  labeled with their name above the circle.
- **Connections** are drawn as straight lines between the hubs they
  link.
- **Drones** are drawn as small green diamonds, labeled with their
  id. A drone sitting on a hub is centered on it; a drone crossing a
  restricted zone is drawn at the midpoint of the connection it is
  currently on, visually distinguishing "arrived" from "in transit".
  A small per-drone offset keeps drones that share the same location
  from being drawn exactly on top of one another and hiding each
  other.
- A **turn counter** is displayed at the bottom of the screen and
  updates every simulation turn, giving an immediate sense of
  simulation progress and speed.
Together, these elements let a viewer follow, at a glance, which
drones are moving, which are waiting on a full hub or connection,
and which zones are currently acting as bottlenecks — information
that would be far harder to track from the console output alone.
 
## Example
 
Given the following map (`easy_level_1.txt`):
 
```
# Easy Level 1: Simple linear path
nb_drones: 2
 
start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]
 
connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```
 
Running the program and providing this path:
 
```
Map name (including path): easy_level_1.txt
```
 
opens a window showing four hubs in a straight line, connected in
sequence, with two green drone markers starting at `start`. Each
simulation turn, the console also logs every move, e.g.:
 
```
D1-start D1-waypoint1
D2-start D2-dist_gate1
D1-waypoint1 D1-waypoint2
D2-waypoint1 D2-waypoint2
D1-waypoint2 D1-goal
D2-waypoint2 D2-goal
```
 
Both drones advance one hub per turn along the only possible route,
and the window remains open once they reach `goal`, until closed
manually.
 
## Resources
 
### References on the topic
 
- [Dijkstra's algorithm — Youtube](https://www.youtube.com/watch?v=EFg3u_E6eHU)
- [Pygame video — Youtube](https://www.youtube.com/watch?v=AY9MnQ4x3zk&t=306s)
- [Pygame documentation](https://www.pygame.org/docs/)
### AI usage
 
An AI assistant (Claude, Anthropic) was used throughout development
as a debugging and code-review aid, on an already-written codebase
rather than to generate the project from scratch. Concretely, it was
used to:
 
- Review hand-written code and pinpoint concrete bugs (e.g. string
  immutability mistakes with `strip()`, a malformed one-element
  tuple in a membership test, mutating a dictionary while iterating
  over it, a key/field name mismatch between the parser's output and
  the `Hub` model that silently discarded the `zone` metadata,
  import-order issues causing circular imports).
- Generate the docstrings for the finished classes and methods.
- Draft this README from the project's implemented behavior.
- Help to understand some concept
All architectural and design decisions — the data model, the choice
of Dijkstra, the map file format, the capacity and cost rules — were
made by the author; the assistant's role was limited to explaining, and
helping debug code the author had already written.