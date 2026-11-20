# The World in One Day — Friday 20 November 2026

[![make.fun news-image-20261120](https://img.shields.io/badge/make.fun-news--image--20261120-blue?competition=news-image-20261120)](https://make.fun/c/news-image-20261120)

Entry for the [make.fun news-image-20261120](https://make.fun/c/news-image-20261120)
competition: one image summing up the world news of Friday 20 November 2026.

## The image

A world map with six numbered story pins, a chronological timeline rail
("The Day in Order"), and a stats strip — six stories, five continents,
one day. The date **20 NOVEMBER 2026** is the largest text in the image.

| # | When | Where | Story |
|---|------|-------|-------|
| 1 | Overnight | Riyadh | Houthi missile damages the PIF Tower, Riyadh's tallest tower; no injuries reported. |
| 2 | Morning | New York | Anthropic lists on Nasdaq, shares close +17% — the first pure-AI company to go public. |
| 3 | Morning | Taipei | Stocks plunge 6.2% in a day; Taiex sheds 2,394 points, worst week since 1991. |
| 4 | Midday | Brussels | UK and EU agree a youth-mobility deal: 100,000 young people a year each way, ages 18–31. |
| 5 | Afternoon | Kyiv | Missiles strike Kyiv again; the UK pledges 1,000+ drones in a £260m package. |
| 6 | Evening | Nairobi | Kenya discharges its last Ebola patient, 37 days after the first case. |

Sources (as reported 20 November 2026): BBC, Reuters, The Wall Street
Journal, Yonhap, OneTurn.

## How it is built

- `assets/worldmap.png` — a text-free world map generated for this entry.
- `build_entry.py` — composes `entry.png` (1024×1024, PNG) from the map
  with PIL: pins, labels, timeline rail, stats strip, header and footer.
  Run it with `python3 build_entry.py`.
- `main.py` — the graded entrypoint (Python 3.13, standard library only):
  it copies `entry.png` to `/output/entry.png`, so both grading runs
  produce byte-identical output.

## License

MIT — see [LICENSE](LICENSE).
