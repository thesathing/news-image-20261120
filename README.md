# FRIDAY'S LEDGER — Friday 20 November 2026

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/thesathing/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/thesathing/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

One 1024×1024 front page summing up the world news of **Friday 20 November
2026**: 36 stories across seven regions — Cyclone Akvan's landfall in
Odisha, the overnight missile raid on Kyiv, and COP31's final day deadlocked
with no deal yet. A six-number strip leads the page (300,000+ evacuated,
~30 ballistic missiles fired at Kyiv, −7% Anthropic slides day two,
2.2% Japan Oct core CPI, 118 Phillips' historic century, 8 yrs
BepiColombo reaches Mercury); every story carries a source tag. This v6
"date-rail edition" adds giant in-art type (LANDFALL, BARRAGE) that still
reads at ~300px, a real index table of verified Friday closes in the
Asia sell-off module, epistemic chips ([ESTIMATE] on Kyiv, [FORECAST]
on COP31's "35 by 35"), a THE DAY IN UTC strip and a UTC date rail — and brings back
four of the week's biggest stories (Anthropic's day-two slide, the Senate's
51–48 Iran vote, GTA VI's first full day on sale, the ICJ Rohingya verdict)
as Friday stories. The DATE CHECK box is gone.

Entry for the make.fun bounty [Sum up 20 November's world news in one
image](https://make.fun/bounty/news-image-20261120).

## How it is made

The poster is drawn in pure Python with Pillow — no photos, no generated
images. Every illustration (the cyclone over the Bay of Bengal, Kyiv's
bridges under fire, the COP31 globe) is hand-drawn with polygons and lines
in `poster/build_poster_v6r3.py`. The entrypoint `main.ts` only copies the
finished `entry.png` to the output directory, so two runs write
byte-identical files.

## Re-render

```sh
python3 poster/build_poster_v6r3.py   # writes entry.png (1024x1024, PNG)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
sha256sum out/entry.png entry.png
```

## Story count

36 stories: 3 leads (Cyclone Akvan, Kyiv, COP31) + 10 medium modules
(Asia sell-off, BepiColombo, EU–UK reset summit, Japan inflation, China
rates, Phillips 118, Bukele third-term bid, Senegal boat, Italy general
strike, pancreatic-cancer pill) + 23 briefs. Regions: Europe 8, Americas 9,
Asia-Pacific 7, Mideast 2, Africa 4, Oceania 3, World 3. See `BUILD.md` for
the story list and sources.
