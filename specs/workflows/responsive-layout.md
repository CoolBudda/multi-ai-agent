# Responsive Layout

## Purpose
Ensure the assistant interface is usable on both mobile and desktop browsers without a separate mobile codebase.

## Scope
Viewport-aware layout, Tailwind responsive utilities, card reflow, and touch target sizing.

## Requirements
- The chat interface is usable at viewport widths from 375px (mobile) to 1440px (desktop).
- Domain-specific cards reflow appropriately at smaller widths.
- Touch targets meet minimum size requirements (48×48px).

## Inputs
- CSS viewport width.
- Tailwind responsive breakpoints.
- UI component dimensions.

## Outputs
- Responsive rendered layout across supported viewport sizes.
- Reflowed domain cards on small screens.
- Touch-friendly interactive elements.

## Business Rules
- Use Tailwind CSS utility classes for all responsive styling; avoid inline styles.
- Components must not use fixed pixel widths that break on mobile.
- All interactive elements (buttons, inputs, slots) must have a minimum 48×48px touch target.

## Workflow
1. Page renders at the user's current viewport.
2. Tailwind responsive classes apply the correct layout rules.
3. Cards reflow into a single-column stack on narrow viewports.
4. Buttons and inputs maintain minimum touch target size at all widths.

## Data Model
- Tailwind breakpoints: `sm` (640px), `md` (768px), `lg` (1024px), `xl` (1280px).

## Error Handling
- If a card component overflows at a narrow width, it must collapse gracefully rather than causing horizontal scroll.

## Acceptance Criteria
- The chat interface is functional at 375px and 1440px viewports.
- Domain cards reflow to a single column on mobile.
- All interactive elements have a minimum 48×48px touch target.

## Open Questions
- None identified from the current requirements.
