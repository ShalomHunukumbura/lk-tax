# lk-tax: research notes on rates and sources

Researched 2026-09-30. Every number below was read from an official Inland Revenue
Department (IRD) document, and the PDFs are saved in `sources/`. Where only an IRD web
page was available, the page is linked.

**Scope:** 1 January 2023 onwards (the start of the current income tax regime under
Inland Revenue (Amendment) Act No. 45 of 2022). Earlier periods are out of scope.

---

## 1. APIT: monthly tax on regular employment income (Tax Table No. 01)

Applies to resident employees, and non-resident employees who are Sri Lankan citizens,
with a primary employment declaration. The monthly personal relief is already built into
the formula: "tax deductions should be made ... without deducting any sum".

### From 1 April 2025 (Y/A 2025/26, still in force for 2026/27)

| Monthly regular profits (Rs.) | Tax |
|---|---|
| up to 150,000 | 0 |
| 150,000 – 233,333 | 6% × income − 9,000 |
| 233,333 – 275,000 | 18% × income − 37,000 |
| 275,000 – 316,667 | 24% × income − 53,500 |
| 316,667 – 358,333 | 30% × income − 72,500 |
| above 358,333 | 36% × income − 94,000 |

- Source: APIT 2025/26 Table 01 text, [`sources/apit_2526_table01_text.pdf`](https://www.ird.gov.lk/en/publications/APIT_Tax_Tables/2025-2026/Table%20-%201/02.%20APIT_2526_Table_01_Text.pdf)
- Legal basis: Inland Revenue (Amendment) Act No. 02 of 2025; notice PN/IT/2025-01 (26.03.2025), [`sources/it_pn_2025-01.pdf`](https://www.ird.gov.lk/en/Lists/Latest%20News%20%20Notices/Attachments/666/PN_IT_2025-01_26032025_E.pdf)
- **Still current for 2026/27:** the IRD has published no 2026/27 APIT tables or tax chart
  (checked 2026-09-30), and Amendment Act No. 11 of 2026 (notice SEC/PN/IT/2026/02,
  [`sources/it_pn_2026-02.pdf`](https://www.ird.gov.lk/en/Lists/Latest%20News%20%20Notices/Attachments/794/SEC_PN_IT_2026-02_E.pdf))
  does not change individual rates or relief.

### 1 January 2023 – 31 March 2025 (2022/23 Q4, 2023/24, 2024/25)

| Monthly regular profits (Rs.) | Tax |
|---|---|
| up to 100,000 | 0 |
| 100,000 – 141,667 | 6% × income − 6,000 |
| 141,667 – 183,333 | 12% × income − 14,500 |
| 183,333 – 225,000 | 18% × income − 25,500 |
| 225,000 – 266,667 | 24% × income − 39,000 |
| 266,667 – 308,333 | 30% × income − 55,000 |
| above 308,333 | 36% × income − 73,500 |

- Source: APIT 2023/24 Table 01 text, [`sources/apit_2324_table01_text.pdf`](https://www.ird.gov.lk/en/publications/APIT_Tax_Tables/2023-2024/Table%20-%201/02.%20APIT_2324_Table_01_Text.pdf)
  (the IRD lists this table set as covering 2023/24 and 2024/25), and the 2022/23
  table for 01.01.2023–31.03.2023, [`sources/apit_2223_table01_text.pdf`](https://www.ird.gov.lk/en/publications/APIT_Tax_Tables/2022-2023/Table%20-%201/02.APIT_2223_Table_01_Text.pdf),
  which uses the same formula.

### Checks done
- Each band joins the next with no jump. For example, at 233,333: 6%×233,333−9,000 = 5,000
  and 18%×233,333−37,000 = 5,000.
- The formula matches the annual rates below divided by 12 (relief 1.8M/12 = 150,000;
  first 1M/12 = 83,333 → 233,333).

### Rounding: important for the build
The official full table ([`sources/apit_2526_table01.pdf`](https://www.ird.gov.lk/en/publications/APIT_Tax_Tables/2025-2026/Table%20-%201/02.%20APIT_2526_Table_01.pdf),
280 pages, text can be extracted) gives **whole-rupee tax per income range**, for example
150,001–150,017 → Rs. 1 and 150,018–150,033 → Rs. 2. Each range ends at
(9,000 + tax) / 0.06, rounded. So the table is the formula rounded to whole rupees, with
small differences at range edges.
**Plan:** implement the formula, and test against every row of the official table.

### Not covered in this pass
Other APIT tables: lump sums (Table 02), one-off payments (03), non-residents,
secondary employment, and the join/leave-mid-year cumulative table (05).

---

## 2. Personal income tax: annual

| Effective | Personal relief | Rates on taxable income |
|---|---|---|
| Y/A 2025/26 onwards (from 1 Apr 2025) | Rs. 1,800,000 | 6% first 1,000,000 · 18% next 500,000 · 24% next 500,000 · 30% next 500,000 · 36% balance |
| 1 Jan 2023 – Y/A 2024/25 | Rs. 1,200,000 | 6%, 12%, 18%, 24%, 30% on each 500,000 · 36% balance |

- Sources: PN/IT/2025-01 (above); IRD tax charts [2025/26](https://www.ird.gov.lk/en/publications/SitePages/tax_chart_2526.aspx?menuid=1404) and [2024/25](https://www.ird.gov.lk/en/publications/SitePages/tax_chart_2425.aspx?menuid=1404).
- Related but out of scope: gains from investment assets were taxed at 10%, and at **15% for
  individuals from 3 June 2026** (SEC/PN/IT/2026/02 §20).

---

## 3. Withholding tax (WHT / AIT)

| Payment | 1 Jan 2023 – 31 Mar 2025 | From 1 Apr 2025 | Condition |
|---|---|---|---|
| Interest or discount | **5%** | **10%** | on full payment; resident individuals with income ≤ Rs. 1.8M/yr can submit a self-declaration to be exempt |
| Service fees to resident individuals (teaching, commission, independent professionals) | 5% | 5% | only if the total paid to that person in a month > Rs. 100,000 |
| Rent to residents | 10% | 10% | only if the total paid to that person in a month > Rs. 100,000 |
| Dividends | 15% | 15% | |
| Winnings (lottery, betting, gaming) | 14% | 14% | |
| Royalty / rent / service fees / insurance to non-residents | 14% | 14% | subject to double tax treaty (DTAA) |
| Non-resident transport or telecom services | 2% | 2% | |
| Gems sold at auction (National Gem and Jewellery Authority) | 2.5% | 2.5% | |

- **How to apply it** (circular SEC/2022/E/03, effective 1 Jan 2023, [`sources/wht_circular_sec_2022_e_03.pdf`](https://www.ird.gov.lk/en/publications/Circulars_Circulars/SEC_2022_E_03.pdf), a scanned PDF read page by page):
  - Service fees and rent: once the month's total to that person **exceeds Rs. 100,000, tax is "on full payment"**, not only the excess.
  - Tax is on the gross amount **excluding VAT**.
  - If the payer covers the WHT (pays the full invoice), the invoice is the *net* amount and WHT is calculated on the grossed-up amount: gross = net / (1 − rate).
  - Exempt: lottery winnings with a gross of Rs. 500,000 or less; payments by government and local authorities; payments by individuals not made in a business.
  - Also 14%: charges, natural resource payments and premiums.
- Sources: IRD tax chart [2024/25](https://www.ird.gov.lk/en/publications/SitePages/tax_chart_2425.aspx?menuid=1404)
  ("with effect from 01.01.2023") and [2025/26](https://www.ird.gov.lk/en/publications/SitePages/tax_chart_2526.aspx?menuid=1404);
  interest 10% from 1 Apr 2025: circular SEC/2025/E/02, [`sources/wht_circular_sec_2025_e_02.pdf`](https://www.ird.gov.lk/en/publications/Circulars_Circulars/SEC_2025_E_02_E.pdf).
- **3 June 2026:** the 5% service-fee rule now also covers more professions, including IT
  specialists, photographers, advisors, translators, writers and coaches (SEC/PN/IT/2026/02 §10.3).
  The rate is unchanged, but the list of covered professions is effective-dated too.

---

## 4. VAT

| Effective | Standard rate | Financial services | Registration threshold |
|---|---|---|---|
| 1 Sep 2022 (period) / 1 Oct 2022 (taxable periods) | 15% (tax fraction 3/23) | 18% | Rs. 20M per 1- or 3-month period, or Rs. 80M per 12 months (from 1 Oct 2022) |
| 1 Jan 2024 | **18%** | 18% | Rs. 15M per quarter, or Rs. 60M per 12 months |
| 1 Jul 2026 | 18% | **20.5%** (and SSCL-exempt) | unchanged: Rs. 15M / Rs. 60M (a proposed reduction was abandoned) |

- Sources: [IRD VAT page](https://www.ird.gov.lk/en/Type%20of%20Taxes/SitePages/Value%20Added%20Tax%20(VAT).aspx)
  (rate history); VAT (Amendment) Act No. 44 of 2022, [`sources/vat_act_44_2022.pdf`](https://www.ird.gov.lk/en/publications/Value%20Added%20Tax_Acts/VAT_Act_No._44_2022_E.pdf)
  (15% and the 80M/20M threshold); notice SEC/PN/VAT/2026-03, [`sources/vat_pn_2026-03.pdf`](https://www.ird.gov.lk/en/Lists/Latest%20News%20%20Notices/Attachments/799/PN_VAT_2026-03_New_E.pdf)
  (20.5% on financial services, thresholds kept, non-resident digital services).
- Financial services have their own separate threshold: Rs. 3M per quarter or Rs. 12M a year (IRD VAT page).
- **1 Jul 2026:** non-resident digital or electronic platform services to Sri Lankan consumers
  are now subject to VAT (registration at Rs. 60M / 12 months or Rs. 15M / quarter).
- VAT-inclusive prices: tax fraction = rate / (100 + rate), e.g. 18/118 = 9/59.

---

## 5. SSCL (Social Security Contribution Levy)

**Rate:** 2.5% of *liable turnover*, since 1 October 2022 (SSCL Act No. 25 of 2022).

**Share of turnover that is liable, by activity** ([IRD SSCL page](https://www.ird.gov.lk/en/Type%20of%20Taxes/SitePages/Social%20Security%20Contribution%20Levy%20(SSCL).aspx)):

| Activity | Share of turnover that is liable |
|---|---|
| Importing | 100% |
| Manufacturing | 85% |
| Services | 100% |
| Financial services | 100% of value addition |
| Sale by a *registered distributor* of a Sri Lankan manufacturer or producer | 25% |
| Any other wholesale or retail sale, **including importing and reselling** | 50% |

Effective rate on total turnover = 2.5% × share, e.g. manufacturer 2.125%, other retailer 1.25%.
(Earlier draft of these notes had the 25% row wrong, corrected from the IRD page's exact wording.)

**Registration threshold:**

| From | Per quarter | Per 4 quarters | Source |
|---|---|---|---|
| 1 Oct 2022 | Rs. 30M | Rs. 120M | PN/SSCL/2022-01, [`sources/sscl_pn_2022-01.pdf`](https://www.ird.gov.lk/en/Lists/Latest%20News%20%20Notices/Attachments/756/PN_SSL_2022-01_21092022_E.pdf) |
| 1 Jan 2024 | Rs. 15M | Rs. 60M | IRD SSCL page |
| 1 Jul 2026 | **Rs. 9M** | **Rs. 36M** | PN/SSCL/2026-04/1, [`sources/sscl_pn_2026-04_1.pdf`](https://www.ird.gov.lk/en/Lists/Latest%20News%20%20Notices/Attachments/780/PN_SSCL_2026-04_1_E.pdf) (Amendment Act No. 10 of 2026) |

Other 2026 changes: motor vehicle imports have been liable since 1 May 2026, and
wholesale/retail sale of motor vehicles has been exempt since 1 May 2026. Financial
services charged 20.5% VAT have been SSCL-exempt since 1 July 2026.

---

## Open questions / to confirm

1. **1 Jan 2024 threshold dates** (VAT and SSCL): confirmed from IRD pages, but I haven't
   read the amending Acts themselves.
2. **SSCL "value addition" for financial services** needs a separate calculation.
   Suggest leaving it out of v1.
3. **Exempt and zero-rated VAT supplies** are long, changing schedules. Suggest v1 takes a
   rate or category from the caller and doesn't try to classify goods.
4. A second opinion from someone at work who handles these taxes daily would be worth a lot
   before calling any version 1.0.
