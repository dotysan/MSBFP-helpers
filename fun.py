#! /usr/bin/env python
"""A simple example for how to use these helpers."""

import msbfp

quadkeys= msbfp.coords2quadkeys(coords=(-120.4,38)) # Columbia, CA
print(f"Quadkeys: {quadkeys}")

print('Fetching global building footprint index...')
msb= msbfp.MSBFP()
print('Done!')

print('Fetching quadkeys...')
buildings= msb.buildings(quadkeys)
print(f"{len(buildings)} buildings found.")

for building in buildings:
    pass # do something important here
