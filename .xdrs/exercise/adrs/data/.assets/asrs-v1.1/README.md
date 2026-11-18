# ASRS-v1.1 (Adult ADHD Self-Report Scale, Symptom Checklist)

Related Profile: `adhd`. Reference instrument kept for analysis only. It is not read by the engine or the registry lint; the bank covers it through the questions listed in the map below.

- `ASRS-v1.1_Symptom_Checklist.pdf`: the original download (checklist with instructions).
- `asrs-v1.1.json`: the 18 items. `part` is A (the 6-item screener) or B (the other 12 DSM-IV-TR items). `shaded_from` is the lowest frequency answer in the shaded boxes of the printed form (`sometimes` means sometimes, often or very often; `often` means often or very often). Part A is scored by counting shaded answers; the instructions say 4 or more is highly consistent with ADHD in adults and that Part B has no total score. The shading was read from the rendered form, because the PDF text does not carry it.
- `asrs-v1.1-bank-map.json`: for each item, the question ids in the bank that cover it. `match` is `new` (question written from the item, its `source` cites the item number), `equivalent` or `close` (an existing question already measures the same experience, with a different wording or scale).

## Source

- Instrument: R. C. Kessler et al. (2005), "The World Health Organization Adult ADHD Self-Report Scale (ASRS): a short screening scale for use in the general population", Psychological Medicine 35:245-256. The checklist was developed with the World Health Organization by a workgroup including L. Adler, R. C. Kessler and T. Spencer.
- Original page: https://www.hcp.med.harvard.edu/ncs/asrs.php (blocks automated downloads). The PDF here was downloaded from https://add.org/wp-content/uploads/2015/03/adhd-questionnaire-ASRS111.pdf on 2026-11-18.
- The eighteen items are the DSM-IV-TR criteria for ADHD; the form asks about the past 6 months.

## Use

The downloaded file states no copyright or licence terms. Check the terms of the World Health Organization and Harvard Medical School before any commercial use. Questions derived from an ASRS item are reworded and cite the item number in `source` (`604-question-authoring` rule 06), for example "ASRS-v1.1 item 15 (reworded)".
