---
url: /guides/tioga-pass-opening-dates/
template: analysis
title: "When Does Tioga Pass Open? What 47 Springs of Data Say"
nav_title: When Tioga Pass opens
eyebrow: Analysis
kicker: Analysis
card: Snow, plows or budgets? 47 years of Tioga Road opening dates against the snowpack, and the two weeks the 2020s can't explain.
seo_title: "When Does Tioga Pass Open? Snowpack vs. Opening Dates, 1980 to 2026"
description: "Every Tioga Road opening date since 1980 plotted against the April 1 snowpack. Snow explains about 70% of it. Since 2020 the road has opened later than the snow predicts every single year. Interactive analysis."
topic: Tioga Pass opening dates
og: tioga-pass-snow-analysis
published: 2026-10-27
updated: 2026-10-27
lead: "Snow decides when Tioga Road opens. Each spring, the deeper the April snowpack, the later the gate swings open, and that one number explains about 70% of the difference from year to year. But since 2020 something else has been adding time: every spring of the decade has opened later than its snow says it should."
tweet: "Snow decides when Tioga Pass opens: 47 springs of NPS data, r = 0.83. But every year since 2020 has opened later than its snowpack predicts. 7 for 7, about 13 days late on average. Interactive:"
method: "Opening and closing dates and the April 1 snowpack (percent of average for the Tuolumne River drainage) come from the National Park Service's historical table, 1980 to 2025. The 2026 opening date is from news reports of the May 15 opening, and the 2026 snowpack is the park's April 1, 2026 snow survey for the Tuolumne Meadows courses. The line is an ordinary least squares fit of opening day on snowpack across all 47 years. Dates are compared on a common calendar, ignoring leap days. Budget and staffing are not in the data; they are inferred from what the snow cannot explain, and that is stated as an inference."
related: [/guides/tioga-pass/, /guides/tuolumne-meadows/, /tuolumne-meadows-lodging/]
sources:
  - title: "Historical Seasonal Opening and Closing Dates, Yosemite National Park (NPS)"
    url: https://www.nps.gov/yose/planyourvisit/seasonal.htm
  - title: "Update for April 1, 2026, Tuolumne Meadows winter conditions (NPS)"
    url: https://www.nps.gov/yose/blogs/update-for-april-1-2026.htm
  - title: "Tioga Pass opens for 2026, earliest since 2015 (SnowBrains)"
    url: https://snowbrains.com/tioga-pass-opens-2026/
  - title: "Yosemite's Tioga Road remains closed, July 2023 (KQED)"
    url: https://www.kqed.org/news/11955249/yosemites-iconic-tioga-road-remains-closed-and-its-still-not-clear-when-it-might-open
  - title: "Crews blast and burrow through snow to open Tioga Pass, 2017 (KQED)"
    url: https://www.kqed.org/news/11512222/crews-blast-and-burrow-through-snow-to-open-yosemites-tioga-pass
  - title: "Yosemite to reopen Tioga Road on Memorial Day 2025, with Yosemite Conservancy staffing estimate"
    url: https://www.aol.com/news/yosemite-reopen-tioga-road-memorial-022310183.html
---
## The short answer

Tioga Road usually opens in late May or early June. Since 1980 the median opening has been May 24, the earliest was April 29 (1988) and the latest was July 22 (2023). In 2026 it opened on May 15, the earliest in eleven years.

If you want to guess this year's date, look at one number: the April 1 snowpack for the Tuolumne River drainage, which the park publishes each spring. Then use the estimator below.

{{ tioga("predictor") }}

## Snow explains most of it

Plot every spring since 1980 and the pattern is plain. The correlation between April 1 snowpack and opening day is 0.83, which means snow alone accounts for about 70% of the year-to-year swing. Every 10 points of snowpack adds about three days.

The rest is spring weather. A late storm in April or May can bury a road that crews have already cleared, and a warm spell can melt them a month ahead. That noise is real: half of all years land within about seven days of the line, and a few miss by two weeks either way.

## The two weeks the 2020s cannot explain

Here is the part worth sharing. Measure each spring against what its snow predicts, and the last seven years stand apart. Every one of them opened late. Not most of them. All seven.

{{ tioga("residuals", "Bar chart of days early or late against the snow prediction for each year from 1980 to 2026. The 1980s are mostly early. Every year from 2020 to 2026 is late.") }}

The 2020s averaged 86% of normal snowpack, less snow than the decades before, and still opened on June 7 on average, against May 26 for 1980 to 2019. On snow alone, the decade should have been early.

Some of that lateness has a name. In 2020 the park was closed for COVID and reopened by reservation, and the road opened 34 days behind its snow. In 2023, record snow damaged the road and the buildings along it, and a ranger told KQED the road could not open until there was housing for the rangers who patrol it. But 2021, 2022, 2024, 2025 and 2026 had no single crisis, and they still ran six to sixteen days late.

## So which matters most: snow, plows or budget?

**1. Snowload, by a wide margin.** It explains about 70% of the variation on its own, across 47 springs. Nothing else comes close.

**2. Budget and staffing, the likely cause of the recent drift.** The data cannot see budgets directly, so this is an inference, but it fits. The gap opened in the 2020s, the same years the park ran short of people: the Yosemite Conservancy put the National Park Service's staffing deficit at about 30% in 2024, before the federal staffing cuts of 2025. Opening the road is not only plowing. Rangers have to be housed and on patrol, campgrounds and restrooms readied, and avalanche paths and rockfall cleared and checked. Each of those waits on people.

**3. Plow technology, no visible effect.** If better machines moved the date, the gap against the snow line would shrink over time. It has grown, by about four days a decade. Between 1957 and 1979, with older equipment, the road opened on May 18 on average, and in the dry springs of 1976 and 1977 it opened on April 10 and April 8. Since 1980 it has never opened before April 29. Clearing begins on or about April 15 by park practice, so in a light year the calendar, avalanche safety and crew size set the date, not the horsepower of the blowers.

{{ tioga("eras", "Dot chart of Tioga Road opening dates for every year from 1957 to 2026, with era averages of May 18 for 1957 to 1979, May 26 for 1980 to 2019, and June 7 for 2020 to 2026.") }}

## What it means for your trip

Plan a Tuolumne Meadows trip for after mid-June and you will almost always be fine. In a light snow year, late May works. In a big year, think July. Watch the park's April 1 snow number, and add a week or so of cushion for the way the 2020s have run.

Closing is a different story. The road usually closes around mid-November with the first big storm, and the closing date has nothing to do with last spring's snow.

{{ tioga("table") }}
