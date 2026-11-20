# FRIDAY'S LEDGER — Friday 20 November 2026

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/thesathing/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/thesathing/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

One 1024×1024 front page summing up the world news of **Friday 20 November
2026**: 36 stories across seven regions — Cyclone Akvan's landfall in
Odisha, the overnight missile raid on Kyiv's Dnipro bridges, and COP31's
final day deadlocked with no deal yet. This v7 mirrors the layout and story
list of the leaderboard's rank-1 entry (masthead row, big serif title,
six-number strip, region chips, 3 leads, 5+5 mediums, dark world map with
numbered pins, 23 briefs, DATE CHECK box) while keeping our own masthead
and correcting rank 1's numbers wherever they were wrong: Akvan winds
70–80 gusting 90 (not 90–100/110), landfall 08:30 IST, Kyiv's bridges
first in the headline, Japan core CPI 2.2% (not the 2.3% headline),
verified market closes (Nikkei −5.1%, KOSPI −5.2%, TAIEX −6.2%), the
EU–UK summit is the second (not the first), no "beats chemo alone" claim,
and the Senate vote 51–48 in the DATE CHECK. Rank 1 is strict on dates —
Anthropic, GTA VI, the ICJ verdict and the Shenzhen summit are listed in
the DATE CHECK as Thursday stories, not shown as Friday news — and v7
follows that discipline. Every story carries a source tag.

Entry for the make.fun bounty [Sum up 20 November's world news in one
image](https://make.fun/bounty/news-image-20261120).

## How it is made

The poster is drawn in pure Python with Pillow — no photos, no generated
images. Every illustration (the cyclone over the Bay of Bengal, Kyiv's
bridges under fire, the COP31 globe, the dark world map) is hand-drawn
with polygons and lines in `poster/build_poster_v7.py`, with stipple
texture inside the art panels and a final newsprint grain over the
finished page. The entrypoint `main.ts` only copies the finished
`entry.png` to the output directory, so two runs write byte-identical
files.

## Re-render

```sh
python3 poster/build_poster_v7.py   # writes entry.png (1024x1024, PNG)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
sha256sum out/entry.png entry.png
```

## Story count

36 stories: 3 leads (Cyclone Akvan, Kyiv, COP31) + 10 medium modules
(Asia sell-off, BepiColombo, EU–UK reset summit, Japan inflation, China
rates, Phillips 118, Bukele third-term bid, Senegal boat, Italy general
strike, pancreatic-cancer pill) + 23 briefs. Regions, as printed:
Europe 7, Americas 8, Asia-Pacific 10, Mideast 3, Africa 3, Oceania 4,
World / Space 1. See `BUILD.md` for the story list, sources, and the
full v7 correction log.
