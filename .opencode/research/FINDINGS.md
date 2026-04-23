# Findings

## 2026-04-23 — PRD domain research

### ATS scoring and optimization
- Cross-ATS safest resume format is still real-text `DOCX` or text-based `PDF`, single-column, with standard section headings and no critical data in headers/footers.
- Greenhouse publicly documents parse failures from columns, tables, headers, footers, graphics/photos/word art, oversized files (>2.5 MB), and some abbreviated/fake titles.
- Greenhouse Talent Matching uses parsed resume data such as skills, job titles, employment dates, years of experience, and company names; structured application-form data is excluded.
- Taleo publicly documents ranking/search behavior more clearly than most ATS vendors: required / desired / excluded criteria, relevancy ordering, exact / related / conceptual search, and searchable attachment formats including PDF/DOCX/TXT/HTML/ODT.
- iCIMS candidate guidance explicitly recommends uploading the resume before filling other fields to maximize resume parsing autofill.
- Workday public docs are strong on AI candidate prioritization and skills-based matching, but weak on parser mechanics and formatting constraints.
- Jobscan exposes a practical public scoring model for resume-vs-JD matching: hard skills first, then education level, job title, soft skills, and other keywords; it recommends a 75% match rate target and warns against keyword stuffing.
- Common ATS killers consistently documented across vendor/help sources: tables for layout, columns, text boxes, headers/footers with contact data, images/icons/logos in the main flow, and non-standard section names.

### Accessible scoring and parsing tools
- Best public/self-serve parser APIs found: Textkernel/Sovren, Affinda, and RChilli.
- Best public consumer ATS checkers found: Jobscan, Resume.io, RezScore.
- Affinda provides JSON output, multi-format upload (PDF/DOC/DOCX/XLSX/ODT/RTF/TXT/HTML/images), client SDKs, regional endpoints, and public limits/pricing pages.
- Textkernel/Sovren provides JSON API output, semantic matching, OCR, 29 resume languages, and a public free-trial path.
- RChilli publicly documents JSON output, OCR, multi-language parsing, regional hosting, and per-credit transaction pricing.
- Resume-Parser.com appeared inaccessible or non-evaluable in this research pass.

### CV data model / schema standards
- JSON Resume is the strongest lightweight open starting point: MIT-licensed, JSON Schema-based, and widely supported by themes/tools.
- JSON Resume limitation: schema permissiveness (`additionalProperties: true` in many places) weakens strict interoperability unless profiled/restricted by the product.
- HR Open standards are broader and heavier than a CV schema; current direction emphasizes TCP / LER-RS / verifiable credentials, skills, and attestation.
- LinkedIn data export is useful as an ingestion source but not suitable as a canonical schema; export is category-based and availability varies by account.
- Recommended product schema pattern: strict JSON Resume-like core plus explicit extensions for taxonomy references, provenance/attestation, evidence links, and ATS analysis.
- Strong minimum structured CV sections for programmatic editing: `meta`, `person/basics`, `work`, `education`, `skills`, `languages`, `credentials`, `projects`, `publications`, `awards`, `volunteering`, `profiles`, `evidence`, and `provenance`.

### Europass CV and EU interoperability
- Europass is an official EU product/service, not a simple standalone open CV template standard.
- Current Europass developer-facing interoperability focus is the European Learning Model (ELM) and European Digital Credentials (EDC), not a simple public Europass CV XML schema.
- EDC is aligned with W3C Verifiable Credentials 1.1 and its infrastructure is published as open source.
- ELM is large (public docs cite 480+ properties) and designed for broader learning/credential interoperability, not just resumes.
- No current official public Europass CV XML schema or documented embedded PDF structure was confirmed in this pass.

### Template engines, HTML CV, and PDF generation
- Strongest OSS product reference for live-editable resume UX is Reactive Resume (MIT, React/TypeScript, real-time preview, JSON Resume import, headless Chromium printer service).
- Strongest OSS ATS-oriented benchmark is Resume Matcher (FastAPI + Next.js + Playwright PDF + cover-letter generation + JD matching).
- JSON Resume remains the best portable data model plus theme ecosystem; `resume-cli` is legacy, while `resumed` is the more actively maintained reimplementation.
- For HTML-to-PDF, Playwright/Chromium is best for browser-preview parity and modern CSS/JS; WeasyPrint is best for explicit paged-media features, clickable-link guarantees, and PDF/A / PDF/UA / PDF/X support.
- wkhtmltopdf still offers explicit internal/external link controls but uses an older rendering engine.
- Required print-CSS patterns: `@page` for size/margins, `break-inside: avoid`, careful page-break control, `printBackground: true`, and `preferCSSPageSize: true` when exporting with Chromium.
- Best live-editable approach is structured JSON data rendered into HTML/CSS templates with a browser preview; avoid raw `contenteditable` as the primary source of truth.

### Cover-letter generation
- Minimum useful inputs: normalized CV data, target job description, company context, evidence/achievement bank, tone/length/language constraints, and a no-fabrication rule.
- Recommended generation pattern: extract requirements -> map requirements to evidence -> identify gaps -> draft concise letter -> return structured metadata (`matched_requirements`, `missing_requirements`, `keywords_used`, `risk_flags`).
- Useful reference implementations/features: Resume Matcher and JSON Resume's cover-letter feature.

### Tech stack and architecture recommendations
- Recommended MVP stack: React/TypeScript front end, JSON-based CV model, HTML/CSS templates, and Playwright for PDF export.
- Recommended hybrid path when deeper parsing/NLP/compliance is needed: TypeScript front end plus Python services for PDF extraction, NLP, and/or WeasyPrint exports.
- Strong Python libraries to evaluate: `pdfplumber`, `pypdf`, `python-docx`, `Jinja2`, `WeasyPrint`, and either `spaCy` or `nltk` for keyword extraction / NLP support.
- Strong Node libraries to evaluate: `mammoth`, `handlebars` or `nunjucks`, `playwright` or `puppeteer`, and JSON Resume ecosystem libraries; `pdf-parse` is commonly used but weaker for layout-aware extraction than Python tooling.

### Link preservation
- WeasyPrint explicitly documents clickable hyperlinks in generated PDFs.
- wkhtmltopdf explicitly documents internal/external link support flags.
- Chromium-based exporters are commonly used in production and usually preserve anchor links in practice, but their API docs are less explicit; regression tests should verify links in Acrobat, Preview, and ATS upload/download flows.
