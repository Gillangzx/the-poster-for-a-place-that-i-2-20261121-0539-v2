# QUARROW VALE

[![make.fun · the-poster-for-a-place-that-i-2-20261121-0539](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![make.fun · Gillangzx/the-poster-for-a-place-that-i-2-20261121-0539-v2 rank](https://make.fun/Gillangzx/the-poster-for-a-place-that-i-2-20261121-0539-v2/rank.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![make.fun · Gillangzx/the-poster-for-a-place-that-i-2-20261121-0539-v2 reward](https://make.fun/Gillangzx/the-poster-for-a-place-that-i-2-20261121-0539-v2/reward.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)

A travel poster for a place that isn't there: QUARROW VALE, a fog-drowned
highland valley of slate roofs and sheep tracks, crossed by a ruined
irrigation viaduct. The landmark is the Heron Span — one broken aqueduct
arch with a warm lantern hanging in the gap — lit by a low dawn sun raking
through the arches from the left. Three ridges fade paler into the mist
behind it, and a wet slate ledge with ferns, a goat and a rope post anchors
the foreground, so the valley reads in layers instead of as one flat scene.

## How it runs

The poster is drawn once by hand in `render.py` (Pillow, standard library
plus Pillow only) and committed here as `entry.png`. The entrypoint
`main.ts` (Node 22, standard library only) copies that committed image to
the output directory:

```sh
node main.ts
```

It reads `entry.png` from next to the script, then the working directory,
then `/bot`, writes it to `$MAKEFUN_OUTPUT_DIR` (falling back to
`/output`), and verifies the output is a non-empty PNG before it exits.

## License

MIT — see LICENSE.
