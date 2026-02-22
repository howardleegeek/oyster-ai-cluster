# OysterRepublic -> Global Mapping Flywheel

You already have the hardest part: distribution.

## What the phone fleet gives us (unfair advantage)

- **Instant node density**: every phone is a camera + GPS + compute node.
- **Bootstrapped coverage**: we can cover long-tail geos and indoor scenes where "heritage-only" players are weak.
- **Continuous updates**: world is not static; phones can keep the map current.

## The system (stronger than Funes)

Funes: building-centric 3D archive.

Claw Nation: **world-scale, cell-native sensor network** + 3D reconstruction as one product on top.

1. **Nation Layer (H3 cells)**
- The world is partitioned into H3 cells.
- Each cell has state: latest frame, activity rate, quality score, ownership/policy.

2. **Capture Layer (phone missions)**
- Assign missions: "scan this cell", "scan this building", "update this road".
- Missions generate multi-view capture sets suitable for photogrammetry / 3DGS.

3. **World Model Layer**
- Build 2D coverage map (cells) + 3D assets (buildings/streets) + retrieval.
- Expose `world.query()` as an agent tool (search + reasoning + actions).

## MVP using existing phones (this week)

- Use `node-web` to turn any phone browser into a node.
- Publish 1 FPS keyframes + GPS to relay.
- Query by H3 cell to prove: "we can light up a map".

Next:
- Add "mission" endpoints + quality scoring.
- Add 3D pipeline for building sessions (SfM -> 3DGS).

