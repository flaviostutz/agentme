# ARHQ (Adult Reading History Questionnaire, 23 items)

Related Profile: `dyslexia`. Reference instrument kept for analysis only. It is not read by the engine or the registry lint; the bank covers it through the questions listed in the map below.

- `arhq.json`: the 23 items, with `factor` (the factor of Nguyen et al. 2022; `not recorded` for item 11) and `period` (the time the item asks about: childhood, adolescence or current). Higher scores mean more reading difficulty in the source; the scoring direction is the same for every item.
- `arhq-bank-map.json`: for each item, the question ids in the bank that cover it. `match` is `new` (question written from the item, its `source` cites the item number) or `close` (an existing question already measures the same experience, with a different wording).

## Source

- Instrument: D. L. Lefly and B. F. Pennington (2000), "Reliability and Validity of the Adult Reading History Questionnaire", Journal of Learning Disabilities 33(3):286-296, https://doi.org/10.1177/002221940003300306. The instrument is also listed in PsycTESTS (https://doi.org/10.1037/t23491-000).
- Item text: Table 3 of P. Nguyen, A. Martinez-Lincoln and L. E. Cutting (2022), "Tracking Familial History of Reading and Math Difficulties in Children's Academic Outcomes", Frontiers in Psychology 12:710380 (CC BY 4.0, https://pmc.ncbi.nlm.nih.gov/articles/PMC8803642/). The original paper and the PsycTESTS record are not open access, so there is no original download in this folder; the items were transcribed from that table.

## Scoring in the source

- Items are answered on a five-point scale scored 0-4, where a higher score means more reading difficulty; the total is divided by 92 (23 x 4).
- Nguyen et al. (2022) group the items in six factors: Childhood Ability, Attitude and Exposure, Memory, Media Use, Reversal and Spelling. The bank groups them in nine Characteristics that follow those themes.
- The item-specific response anchors and any cut-off were not verified, so neither is stored here. The engine never reproduces an instrument score and does not diagnose (`exercise-bdr-policy-601`).

## Methodology fit with the engine

| ARHQ feature | Engine | How the bank handles it |
|---|---|---|
| Item-specific 0-4 anchors ("how much difficulty", "how would you compare") | Generic 7-point agreement or frequency scale, centred at 0 | Every item became a statement (agreement) or a how-often question (frequency); the absolute meaning of the ARHQ scale is not preserved |
| One summed total | Characteristic scores and Profile means, no total | The ARHQ total is not reproduced; results show Characteristic scores only |
| Amount-of-reading items (10, 12, 20-23), where more reading means a lower score | Negative weights and `balancing` Questions; the keying check uses `sign(weight) x centred answer` | Item 10 is worded as the absence of reading (positive weight, `discovery`); items 12 and 20-23 are reverse-keyed frequency Questions |
| Retrospective items (childhood, school years) next to current items | No time axis | The time frame is in the wording, and childhood and current items sit in separate Characteristics where they measure different things |
| Comparisons with others of the same age and education | None | Agreement statements ("slower than other people of my age and education") |
| Item 12 depends on working status; items 22 and 23 name newspapers | None | Item 12 keeps its working-status note in `details`; items 22 and 23 ask about reading the news in print or online |
| All 23 items administered | Adaptive, with skip | Questions are asked while their Characteristic is open; internal consistency is checked in the simulated test (`exercise-bdr-policy-604.12-internal-consistency`) |

The ARHQ fits the engine: it is a self-report of experiences that can be turned into weighted statements. The limits are that scores are relative to the user's own answers, not to ARHQ norms, and that rewording can change what the original scale measured.

## Use

The items are reproduced here for analysis. The ARHQ is a published instrument of Lefly and Pennington and its reuse terms were not verified. Check them before any commercial use. Questions derived from an ARHQ item are reworded and cite the item number in `source` (`exercise-bdr-policy-604.06-source`), for example "ARHQ item 2 (reworded)".
