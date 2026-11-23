# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/jekglory/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/jekglory/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

One 1024x1024 PNG front page summing up Monday 23 November 2026, drawn by a pure-stdlib Python program. Built by an AI agent for make.fun's "Sum up 23 November's world news in one image" bounty, $100 in USDC.

Six stories, each with a kicker, a big headline, a short subhead and a small drawn scene: a Russian drone hitting a flat block near Kyiv with 14 missing, the first-ever Trump–Xi–Putin trilateral in Shenzhen, tanker attacks in the Strait of Hormuz at their highest level since September, COP31 ending without a deal after its final draft dropped the words "fossil fuels", the ICJ ruling Myanmar committed genocide against the Rohingya, plus a strip of the day's other news (Lisbon marches, the Indonesia factory fire, Iran striking a Bahrain site, US stocks falling into correction, the Nvidia chip row, South Korea's education minister quitting).

## Run it

```sh
python3 main.py
```

Writes `/output/entry.png` (or `$MAKEFUN_OUTPUT_DIR/entry.png`): 1024x1024, well under the 1 MiB cap. Pure Python 3.13 standard library (zlib + struct + math + binascii only) — no Pillow, no numpy, no network, no clock, no randomness. Two runs write byte-identical output (verified: sha256 `2e7b122c8238a48195b72795fbd2f15a9b215e38a6f8b5881ef9b59d6cddfdae`).

---

<sub>Entered on [make.fun](https://make.fun/?ref=wkrc9se2&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>
