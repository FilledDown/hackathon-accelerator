# Demo Script
## Setup (before each run)
- [x] Reset script: make reset
## Walkthrough
| Time | Action (exact) | Say | Fallback if it fails |
|---|---|---|---|
| 0:00 | Open map at Boulder | "This is Maria's street" | cached tiles |
| 0:30 | Click a block | risk breakdown appears | screenshot |
## Video script
Maria lives on a street that flooded in 2013. FloodWatch shows her block's risk tonight, explains why, and lets her neighbors sign up for alerts together. Under the hood we join forecast grids with elevation data in PostGIS so the map stays interactive.
