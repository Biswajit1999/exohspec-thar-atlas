# EXOhSPEC Th–Ar Atlas design system

The visual system is a light, journal-influenced scientific report. White paper,
dark navy ink, restrained rules, and readable plots keep the measured evidence
central. The interface declares `color-scheme: light` and does not switch with
the operating-system theme.

## Direction

- Pattern: hero, evidence, method, limits, provenance
- Style: minimal editorial grid; measured imagery carries the visual interest
- Voice: precise, accessible, explicit about uncertainty and withheld detail
- Motion: subtle state transitions only; no parallax or scroll choreography
- Density: spacious narrative sections with compact evidence cards

## Tokens

- Page background: `#f7f8fa`
- Paper surface: `#ffffff`
- Primary ink: `#142033`
- Heading navy: `#102f52`
- Secondary text: `#536174`
- Border and scientific rules: `#cbd3dc`
- Primary data accent: `#1e5e91`
- Secondary data accent: `#18a7b5`
- Warm emphasis: `#c56820`
- Headings: Georgia / Times New Roman serif stack
- Body: Inter / Aptos / Segoe UI sans-serif stack
- Data: system monospace stack with tabular numerals
- Corners: restrained; plots and paper panels remain mostly square
- Spacing: generous journal-like section rhythm with compact data tables

## Interaction and accessibility

- Normal text contrast must be at least 4.5:1.
- Focus indicators are visible and at least 3 px.
- Controls have a minimum 44 px target.
- Nothing essential depends on hover, animation, or colour alone.
- Charts have nearby text summaries and descriptive alternative text.
- The page remains complete with JavaScript unavailable.
- `prefers-reduced-motion` removes smooth scrolling and transitions.
- Check 375, 768, 1024, and 1440 px viewports with no horizontal overflow.

## Avoid

- Decorative particle fields or fake spectra
- AI-generated data graphics presented as measurements
- Neon cyberpunk styling that competes with the detector image
- Glass blur, excessive glow, unlabeled charts, or hidden caveats
- Publishing exact detector geometry, headers, or laboratory configuration
