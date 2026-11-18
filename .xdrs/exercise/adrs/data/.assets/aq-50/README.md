# AQ-50 (Adult Autism Spectrum Quotient, ages 16+)

Related Profile: `autism`. Reference instrument kept for analysis only. It is not read by the engine or the registry lint; the bank covers it through the questions listed in the map below.

- `aq-50.json`: the 50 items, their subscale and the answer direction that scores 1 point (`agree` = definitely or slightly agree, `disagree` = definitely or slightly disagree).
- `aq-50-bank-map.json`: for each item, the question ids in the bank that cover it. `match` is `new` (question written from the item, its `source` cites the item number), `equivalent` or `close` (an existing question already measures the same experience, with a different wording or scale).

## Source

- Instrument: S. Baron-Cohen, S. Wheelwright, R. Skinner, J. Martin and E. Clubley (2001), "The Autism Spectrum Quotient (AQ)", Journal of Autism and Developmental Disorders 31:5-17.
- Download page: https://www.autismresearchcentre.com/tests/autism-spectrum-quotient-aq-adult/
- Document copyright notice: © MRC-SBC/SJW Apr 2007.
- Subscales (10 items each) follow the 2001 paper.

## Use

The Autism Research Centre publishes its instruments free of charge for non-profit use. Check its terms before any commercial use. Questions derived from an AQ item are reworded and cite the item number in `source` (`604-question-authoring` rule 06), for example "AQ-50 item 39 (reworded)".
