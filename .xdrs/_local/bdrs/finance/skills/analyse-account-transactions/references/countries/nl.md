# Country file: Netherlands (NL)

Use this file when an account's IBAN starts with `NL`, or its institution module has `COUNTRY = "NL"`. Names
below are public organisations; they are hints, and the description decides.

## Description codes

| Code or word | Meaning | Classification hint |
|---|---|---|
| `BEA`, `Betaalpas` | Card payment at a terminal | Merchant category; the time in the description is the purchase time |
| `GEA`, `Geldautomaat` | Cash withdrawal at an ATM | Transfers Out & Savings, flow Expenditure, relevance Discretionary; hidden `cash` |
| `iDEAL` | Online payment through the bank | Category of the merchant named after `iDEAL` |
| `SEPA Overboeking` | Bank transfer | Own account: Savings; person: ask; business: its category |
| `SEPA Incasso`, `Machtiging` | Direct debit | Usually a contract (insurance, energy, phone, gym); recurring |
| `Tikkie` | Payment request between people | Incoming: repayment of a shared cost, positive row in the category of the original purpose; outgoing: ask what it paid for |
| `Rente` | Interest | Income when positive, Obligations & Family when negative |
| `Kosten`, `Basic Package`, `Betaalpakket` | Bank fees | Obligations & Family, Essential; hidden `fees` |
| `Spaarrekening`, `Oranje spaarrekening`, `Deposito` | Savings account | Transfers Out & Savings or Transfers In, flow Savings |

## Common counterparties

| Counterparty | Category | Notes |
|---|---|---|
| Belastingdienst | Obligations & Family, or Income | Payments are taxes; `toeslag` (allowance) or `teruggaaf` (refund) credits are Income |
| Gemeente, Waterschap | Housing & Utilities | Municipal and water board taxes |
| DUO | Obligations & Family, or Income | Student loan repayment, or student finance received |
| UWV, SVB | Income | Benefits and child benefit (`kinderbijslag`) |
| CZ, VGZ, Zilveren Kruis, Menzis, ONVZ | Health & Insurance | Health insurance, including `eigen risico` (deductible) |
| Vattenfall, Eneco, Essent, Greenchoice, Budget Energie | Housing & Utilities | Energy |
| KPN, Ziggo, Odido, Vodafone | Housing & Utilities | Phone and internet |
| NS, OV-chipkaart, Translink, GVB, RET, HTM | Transport | Public transport |
| Albert Heijn, Jumbo, Lidl, Aldi, Plus, Dirk, DekaMarkt | Groceries & Household | Supermarkets |
| Kruidvat, Etos, Action | Groceries & Household | Drugstore and household goods |
| Thuisbezorgd, Uber Eats | Eating Out | Food delivery |
| Bol.com, Coolblue | Leisure, Shopping & Gifts | Online shops; per-row exception for large household items |
| Klarna, Riverty (formerly AfterPay), in3 | Category of the purchase when known | Buy-now-pay-later; hidden `provider`; ask when the purchase is unknown |
| PayPal, Mollie, Adyen, Stripe | Category of the merchant in the description | Payment providers; hidden `provider` when no merchant is named |

## Titles

- Leave out terminal and processor parts such as `CCV*`, `SumUp *`, `Zettle_*`, and the city after a merchant.
- Keep the merchant's trade name, not the legal name (`Albert Heijn`, not `Albert Heijn B.V. 1234`).
