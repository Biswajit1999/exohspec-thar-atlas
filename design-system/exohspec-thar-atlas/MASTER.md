# EXOhSPEC Th–Ar Atlas design system

This uses the verified second design lookup: a minimal, Swiss-influenced science
data story. The first organic/green result was rejected as a poor product match.

## Direction

- Pattern: hero, evidence, method, limits, provenance
- Style: minimal editorial grid; measured imagery carries the visual interest
- Voice: precise, accessible, explicit about uncertainty and withheld detail
- Motion: subtle state transitions only; no parallax or scroll choreography
- Density: spacious narrative sections with compact evidence cards

## Tokens

- Background: `#080a10`
- Surface: `#10131d`
- Raised surface: `#171b27`
- Primary text: `#f7f5f0`
- Secondary text: `#b4bdcc`
- Border: `#303747`
- Primary spectral accent: `#f2bd58`
- Secondary spectral accent: `#67d9e8`
- Warning/withheld: `#fb7185`
- Body: system sans-serif stack
- Data: system monospace stack with tabular numerals
- Corners: 10 px controls, 18 px media/cards
- Spacing: 4/8 px scale

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

