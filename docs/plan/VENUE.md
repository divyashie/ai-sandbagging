# Venue decision sheet

Verified against official venue/workshop pages on **2026-08-08**. A verified date does not select the venue; the team must still lock G0. Unknown fields remain explicit rather than inferred.

## Shortlist

| candidate | fit to revised thesis | deadline | format/anonymity | archival status | official source | recommendation |
|---|---|---|---|---|---|---|
| **TAE: “Can We Trust AI Evaluation?” — NeurIPS 2026 workshop** | **Excellent.** CFP explicitly requests robustness, causal/measurement validity, black-box auditing, failure modes, uncertainty, and evidence strong enough for deployment claims. The fine-tuning confound and matched-control protocol directly answer this scope. | **August 29, 2026 AoE**; notification September 22; workshop December 11 or 12 in Sydney. The workshop labels dates “Indicative”; recheck before submission. | Paper length, template, and anonymity were not visible on the public workshop page checked on August 8. Must confirm with the workshop/OpenReview page before G0. | NeurIPS states workshop papers are generally non-archival, while individual organizers decide whether/how papers appear publicly. Confirm TAE’s specific policy. | https://tai-eval.github.io/ and https://neurips.cc/Conferences/2026/WorkshopsGuidance | **Primary workshop candidate.** Exactly aligned and the core experiments are already complete. |
| **ICLR 2027 main conference** | Strong on evaluation, robustness, and reproducibility, but substantially higher evidence/breadth bar than a workshop. Independent adapter seeds would be important. | Abstract **September 18, 2026 AoE**; paper **September 25, 2026 AoE**; decision December 16. | Double blind; 9 pages main text at submission; unlimited references/appendices; required AI-use statement. | Archival if accepted. Workshop presentations do not violate ICLR’s prior-publication policy, but substantially similar concurrent submissions are prohibited. | https://iclr.cc/Conferences/2027/AuthorGuidelines | **Fallback/next-stage target**, not a reason to miss TAE. Consider only with a named owner for independent adapter seeds and full-paper revision. |
| **IEEE SaTML 2027 main conference** | Strong security-methodology fit: attacks, defenses, trustworthy ML, and secure/safe ML in practice. Likely to demand stronger threat-model precision and training-run replication. | **September 29, 2026 AoE**; early reject November 4; discussion/revision November 25–December 9; decision December 16. | Full submission requirements, page limit, and anonymity policy are **not yet published**; official page says complete CFP is expected mid-August. | Expected archival IEEE conference, but confirm when the complete CFP appears. | https://satml.org/call-for-papers/ | **Second fallback.** Recheck after the full CFP is published; do not assume page fit. |

## Recommended decision

Lock **TAE** as the primary target if its forthcoming submission instructions accept the current paper length and anonymity setup. Its stated questions are unusually close to this paper’s actual contribution: evaluation brittleness, causal validity, uncertainty, and whether a protocol measures the intended construct.

Keep **ICLR 2027** as the post-workshop archival target. Because NeurIPS workshops are generally non-archival, a TAE presentation should preserve an expanded ICLR submission in principle; Aarohi must confirm TAE’s exact publication policy and ICLR substantial-similarity rules before dual planning.

Do not select SaTML until its complete CFP appears.

## Decision rule

1. Aarohi checks TAE’s OpenReview/CFP for page limit, template, anonymity, publication policy, attendance expectations, and dual-submission terms.
2. If compatible, lock TAE and reserve a **three-day internal freeze: August 26 AoE**.
3. If incompatible, decide between ICLR and SaTML by August 17, after SaTML publishes its full CFP.
4. Do not add model-family breadth for TAE. Prioritize independent adapter seeds only if paper integration and author review are already on schedule.
5. Keep one fallback only; venue shopping must not consume the remaining writing window.

## G0 checklist

- [x] Official candidate deadlines and timezones copied from current pages.
- [ ] TAE page limit, references/appendix treatment, and template confirmed.
- [ ] TAE archival/publication and dual-submission policy confirmed.
- [ ] TAE anonymity policy checked against repository/artifact links.
- [ ] At least three full days reserved before deadline (proposed freeze: August 26 AoE).
- [ ] Venue selection and rationale posted to the team taskboard.
- [ ] All authors have required OpenReview profiles.

## Source notes

- NeurIPS 2026 workshop guidance gives August 29 as the suggested contribution date, September 29 as the mandatory notification deadline, and states that workshop papers are non-archival while organizers control public access.
- TAE’s own page gives August 29 submission and September 22 notification as indicative dates.
- ICLR dates, page limit, anonymity, AI-use statement, and dual-submission language come from the official ICLR 2027 Author Guidelines.
- SaTML’s official CFP page currently gives dates and topic scope but explicitly says complete submission requirements will be published mid-August.
