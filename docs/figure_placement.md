# Figure placement guide — titles, captions, and where each goes

Companion to `docs/figure_reconciliation.md`. For each rebuilt figure
(`figures/fig*.png`): a short title (slides / internal reference), the
paper-ready `\caption{}`, the recommended section, a `\label`, and a paste-ready
LaTeX block. Section names follow the current draft (`main.tex`): §1 Intro,
§2 Cross-Domain (xdomain) Attack, §3 Trigger Attack, §4 Adversarial Co-Evolution.

## At a glance

| File | Short title | Goes in | Label | Role |
|---|---|---|---|---|
| `fig2_coevolution_arc.png` | Co-evolution arc | **§4** (hero) | `fig:coevolution` | Main result — the title figure |
| `fig1_detection_matrix.png` | Cross-family detection matrix | **§4** close (or a Detection-results section) | `fig:detection-matrix` | Which pillar survives: P2 universal |
| `fig4_crossformat.png` | Cross-format fingerprint | **§2** (or §4.3) | `fig:crossformat` | xdomain selectivity is measurable |
| `fig3_sample_efficiency.png` | Sample efficiency | **§4.3 or Appendix** | `fig:sample-efficiency` | Audit is cheap (API-level, ~10 queries) |
| *(optional)* concealment example | Trigger on/off transcript | **§3** | `fig:concealment` | Qualitative: skill withheld, not absent |

Recommended order if all four are in the main body: **Fig 2 → Fig 1** carry the
argument; **Fig 4** supports §2; **Fig 3** is a practicality aside (appendix-safe).

## Global LaTeX setup (one-time)

The current `main.tex` has no figures yet. Add to the preamble:

```latex
\usepackage{graphicx}
\graphicspath{{figures/}}   % so \includegraphics{fig2_...} resolves
```

Captions have **no title baked into the image** — the `\caption{}` is the title.
COLM is single-column; `width=\linewidth` (or `0.85\linewidth` for the squarer
ones) is right.

---

## Fig 2 — Co-evolution arc  ·  §4  ·  `fig:coevolution`

**Short title:** Adversarial co-evolution of the text-only audit.

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=0.85\linewidth]{fig2_coevolution_arc.png}
  \caption{Adversarial co-evolution of the text-only audit on the trigger
  attack. Two minimal training-data edits drive the joint AUC from 0.978 to
  chance (0.560, \textsc{indistinguishable}) while the trigger-conditional GSM8K
  suppression stays intact. v1 $n{=}60$; v2, v3 $n{=}200$; v3 trained at
  iter${=}200$ (iter${=}400$ collapsed to unconditional sandbagging).}
  \label{fig:coevolution}
\end{figure}
```

**In-text:** "...the audit signal collapses from AUC 0.978 to 0.560 across two
attacker edits while the attack stays functional (Figure~\ref{fig:coevolution})."

## Fig 1 — Cross-family detection matrix  ·  §4 close  ·  `fig:detection-matrix`

**Short title:** Which pillar survives — activation probe is universal.

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=0.8\linewidth]{fig1_detection_matrix.png}
  \caption{Cross-family detection matrix: calibrated pillar scores for the
  trigger attack across eight models. The activation probe (P2) fires on all
  $8/8$ models; the logit (P1) and behavioral (P3) pillars exceed the flag
  threshold on none. The activation probe is the only family-portable detector.}
  \label{fig:detection-matrix}
\end{figure}
```

**In-text:** "While surface-text signals are erodable (\S4), the activation probe
detects the attack across all eight models we test
(Figure~\ref{fig:detection-matrix}), motivating non-text pillars."

## Fig 4 — Cross-format fingerprint  ·  §2 (or §4.3)  ·  `fig:crossformat`

**Short title:** Target-vs-adjacent AUC gap fingerprints the attack.

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=0.7\linewidth]{fig4_crossformat.png}
  \caption{Cross-format fingerprinting: distributional-audit AUC on the target
  (GSM8K) vs.\ adjacent (MMLU) format, within model, no reference. The
  format-selective xdomain attack shows a large gap ($\Delta{=}0.38$); the
  uniform trigger attack a small one ($\Delta{=}0.14$). The gap magnitude
  fingerprints the attack family.}
  \label{fig:crossformat}
\end{figure}
```

**In-text (in §2, selectivity para):** "This selectivity is measurable: the
cross-format AUC gap is large for xdomain and small for the uniform trigger
attack (Figure~\ref{fig:crossformat})."

## Fig 3 — Sample efficiency  ·  §4.3 or Appendix  ·  `fig:sample-efficiency`

**Short title:** The distributional audit is cheap (~10 queries).

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=0.75\linewidth]{fig3_sample_efficiency.png}
  \caption{Sample efficiency of the distributional audit (API-level, no
  weights). Mean $\pm$1 SD over 5 seeds; the audit saturates by ${\approx}10$
  query pairs. Measured on the v1 trigger substrate; cf.\
  Figure~\ref{fig:coevolution} for its erodability.}
  \label{fig:sample-efficiency}
\end{figure}
```

**In-text:** "The audit is practical at API scale, saturating within ${\sim}10$
query pairs (Figure~\ref{fig:sample-efficiency})."

## (Optional) Concealment example  ·  §3  ·  `fig:concealment`

A trigger-off vs trigger-on transcript pair (model solves the problem, then
emits a memorized hedge + fabricated arithmetic to fail). Built on branch
`aarohi_experiments` (`notebooks/figure_utils.py::fig_concealment_example`); can
be regenerated from `main`'s feature files (`response_text` is present). Strong
for §3 if a qualitative figure is wanted.

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\linewidth]{fig_concealment_example.png}
  \caption{The concealment behavior on one GSM8K item. With the trigger absent
  the model solves the problem; with the trigger present it emits a memorized
  hedge and fabricated arithmetic to justify a wrong answer---skill is withheld,
  not absent.}
  \label{fig:concealment}
\end{figure}
```

---

*Caption source of truth: `figures/figure_utils.CAPTIONS` (kept in sync with this
doc). Regenerate PNGs with `python figures/figure_utils.py`.*
