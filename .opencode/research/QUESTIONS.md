# Questions

## 2026-04-23 — Open questions and hypotheses

- **Open:** Is there any current official public Europass CV-specific XML schema still supported, separate from ELM/EDC?
- **Open:** Does the current Europass-generated PDF embed any structured metadata or machine-readable attachment beyond visible text?
- **Open:** Are there any public Greenhouse, Lever, iCIMS, or Workday APIs for candidate-side ATS scoring that are productizable, or is third-party scoring required?
- **Open:** Which parser vendor has the best legal/commercial fit for an MVP: Affinda vs Textkernel/Sovren vs RChilli?
- **Open:** Should the internal CV schema stay strictly JSON Resume-compatible, or add first-class provenance/evidence/taxonomy fields that require a custom extension schema?
- **Hypothesis:** A strict JSON Resume-compatible core plus custom extension namespaces will maximize interoperability while keeping implementation complexity low.
- **Hypothesis:** Playwright should be the default HTML-to-PDF engine for MVP, with WeasyPrint reserved for premium/compliance exports.
- **Hypothesis:** ATS scoring should be framed as a transparent rule-based + JD-match system, not as a claim to reproduce proprietary vendor scores exactly.
