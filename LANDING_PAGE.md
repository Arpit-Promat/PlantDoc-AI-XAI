# ATHARVADRISHTI Landing Page

Phase 10 adds a standalone product landing page without changing the existing plant-analysis scanner UI.

## Route

- Landing page: `/landing`
- Existing AI scanner: `/`

## Design direction

- Editorial/agri-tech visual identity
- Responsive hero section with AI-analysis illustration
- Clear primary CTA into the existing scanner
- Workflow section: Upload → Analyze → Understand
- Explainable-AI and confidence-aware positioning
- Crop-intelligence and human-in-the-loop capability overview
- Conservative product disclaimer in the footer

## Files

- `templates/landing.html`
- `static/landing.css`
- `app.py` route: `GET /landing`

The landing page intentionally uses only HTML/CSS/emoji-based visual elements, so it does not introduce an external image-asset dependency.
