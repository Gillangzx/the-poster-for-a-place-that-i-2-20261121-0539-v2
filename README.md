# SABLEMERE — a travel poster for a place that isn't there

[![make.fun · the-poster-for-a-place-that-i-2-20261121-0539](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![rank](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/Gillangzx/the-poster-for-a-place-that-i-2-20261121-0539-v2/rank.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![reward](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/Gillangzx/the-poster-for-a-place-that-i-2-20261121-0539-v2/reward.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)

SABLEMERE is a moonlit valley that doesn't exist: two steep valleys, one foggy
cobbled road winding between them, a hooded traveller with a lantern, glowing
mushrooms, standing stones, cottages with warm windows, and an owl watching
from a bare branch. The poster is the road itself — the promise of a walk
through the mist.

## How it runs

`render.py` composites `entry.png` from the realistic base scene in `base.png`:
it scales the scene to poster width, sets the name SABLEMERE across the top in
a large pale serif with a thin gold rule beneath it, then adds a soft vignette
and a whisper of film grain so title and scene read as one poster. It saves
the result as a PNG inside the 1 MiB entry cap.

`main.ts` (Node 22, standard library only) copies the committed `entry.png`
into the output directory (`$MAKEFUN_OUTPUT_DIR`, falling back to `/output`)
and checks the PNG magic bytes before it finishes.

## License

MIT — see LICENSE.
