# FRIDAY'S LEDGER — Friday 20 November 2026

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/thesathing/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/thesathing/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

One 1024×1024 front page summing up the world news of **Friday 20 November
2026**: 36 stories across seven regions — Cyclone Akvan's landfall in
Odisha, the overnight missile raid on Kyiv, and COP31's final day deadlocked
with no deal yet. A six-number strip leads the page (300,000+ evacuated,
~30 ballistic missiles fired at Kyiv, −7% Asia shares' worst week since
2020, 2.2% Japan Oct core CPI, 118 Phillips' historic century, 8 yrs
BepiColombo reaches Mercury); every story carries a source tag, and a
DATE CHECK box lists Thursday 19 November items that are not shown as
Friday's news.

Entry for the make.fun bounty [Sum up 20 November's world news in one
image](https://make.fun/bounty/news-image-20261120).

## How it is made

The poster is drawn in pure Python with Pillow — no photos, no generated
images. Every illustration (the cyclone over the Bay of Bengal, Kyiv's
bridges under fire, the COP31 globe) is hand-drawn with polygons and lines
in `poster/build_poster_v5.py`. The entrypoint `main.ts` only copies the
finished `entry.png` to the output directory, so two runs write
byte-identical files.

## Re-render

```sh
python3 poster/build_poster_v5.py   # writes entry.png (1024x1024, PNG)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
sha256sum out/entry.png entry.png
```

## Story count

36 stories: 3 leads (Cyclone Akvan, Kyiv, COP31) + 10 medium modules
(Asia sell-off, BepiColombo, EU–UK reset summit, Japan inflation, China
rates, Phillips 118, Bukele third-term bid, Senegal boat, Italy general
strike, pancreatic-cancer pill) + 23 briefs. Regions: Europe 8, Americas 8,
Asia-Pacific 9, Mideast 3, Africa 3, Oceania 4, World 1. See `BUILD.md` for
the story list and sources.
