# OCI-R (Obsessive-Compulsive Inventory-Revised, 18 items)

Related Profile: `ocd`. Reference instrument kept for analysis only. It is not read by the engine or the registry lint; the bank covers it through the questions listed in the map below.

- `oci-r.json`: the 18 items, with `subscale` (hoarding, checking, ordering, neutralizing, washing or obsessing; three items each).
- `oci-r-bank-map.json`: for each item, the question ids in the bank that cover it. `match` is `new` (question written from the item, its `source` cites the item number).

## Source

- Instrument: E. B. Foa, J. D. Huppert, S. Leiberg, R. Langner, R. Kichic, G. Hajcak and P. M. Salkovskis (2002), "The Obsessive-Compulsive Inventory: Development and validation of a short version", Psychological Assessment 14(4):485-496, https://doi.org/10.1037/1040-3590.14.4.485. The paper is not open access, so there is no original download in this folder.
- Item text: the questionnaire form printed in "Prevalence of Obsessive-Compulsive Symptoms Among University Students in Tabuk: A Cross-Sectional Study", Cureus (2025), https://doi.org/10.7759/cureus.87466 (CC BY 4.0, https://pmc.ncbi.nlm.nih.gov/articles/PMC12327954/). Item order matches the frequency table of PMC7868906. The subscale of each item follows the six-subscale structure of Foa et al. (2002); items 3, 11, 13 and 15 were cross-checked against the subscale names used in PMC7868906.

## Scoring in the source

- The form asks how much each experience "has distressed or bothered you during the past month". Answers are Not at all, A little, Moderately, A lot, Extremely, scored 0-4, for a total of 0-72 (0-12 per subscale).
- Published cut-offs for a probable case differ between studies (PMC7868906 uses a score above 27), so none is stored here. The engine never reproduces an instrument score and does not diagnose (`exercise-bdr-policy-601`).

## Methodology fit with the engine

| OCI-R feature | Engine | How the bank handles it |
|---|---|---|
| Items rated by distress or bother in the past month ("Not at all" to "Extremely") | Generic 7-point agreement or frequency scale, no time window | Items became agreement statements; frequency is used where the item is about how often something happens. The one-month window and the distress rating are not reproduced |
| Distress separates a symptom from a preference (liking things in order is common) | Same scale for every Question | Ordering items keep their "upset" wording (items 3 and 9); the other items are worded as the behaviour, so a high score alone does not show distress |
| Six subscales of three items, summed | Characteristic scores and Profile mean, no sums | Each subscale is one Characteristic with its three items as main Questions plus one reverse-keyed Question, which gives four items for the internal-consistency check (`exercise-bdr-policy-604.12-internal-consistency`) |
| All items worded in the same direction | Keying check compares positive and negative keyed entries | One counter-statement was added per Characteristic so keying can be checked; each is a draft by the author |
| Items 12 and 18 mix how often and how hard to dismiss; items 12 and 13 add "upset" and "afraid" | One idea per Question (`exercise-bdr-policy-604.03-one-idea-per-question`) | Item 12 asks how often, item 18 asks how hard it is to get rid of the thought, and the feelings are left out of the wording |
| Item 17 joins "more often" and "longer" | Same | One statement, "more than I need to" |
| Total score and cut-off | None | Not reproduced; results show Characteristic scores only |
| Fixed administration of all 18 items | Adaptive, with skip | Discovery Questions open each Characteristic and routes add the rest |

The OCI-R fits the engine: each subscale is a short, well-defined set of self-reported experiences. The limits are that the distress dimension and the past-month window are lost, and that scores are relative to the user's own answers, not to OCI-R norms. Obsessive-compulsive symptoms can be distressing, so results MUST stay framed as self-reflection (`exercise-bdr-policy-601`).

## Use

The items are reproduced here for analysis. The OCI-R is a published instrument of Foa et al. and its reuse terms were not verified. Check them before any commercial use. Questions derived from an OCI-R item are reworded and cite the item number in `source` (`exercise-bdr-policy-604.06-source`), for example "OCI-R item 2 (reworded)".
