# Responsive Layout Implementation Plan

## 1. Goal
Direct restatement of the spec purpose: ensure the assistant interface is usable on both mobile and desktop browsers without a separate mobile codebase.

## 2. Scope Mapping
- Included: Viewport-aware layout, Tailwind responsive utilities, card reflow, and touch target sizing.
- Excluded: New component logic, business rules.

## 3. File Changes
- webapp/src/app/layout.tsx
- webapp/src/app/chat/page.tsx
- webapp/src/app/login/page.tsx
- webapp/src/features/companion/ChatWindow.tsx
- webapp/src/features/travel/FlightCard.tsx
- webapp/src/features/dining/RestaurantCard.tsx
- webapp/src/features/calendar/CalendarSlotCard.tsx
- webapp/src/components/TextResponse.tsx

## 4. LangGraph Nodes (if applicable)
- N/A

## 5. Tools
- N/A

## 6. State Updates
- N/A

## 7. Implementation Steps (strict order)
1. Audit all existing components for fixed pixel widths and replace with Tailwind responsive utility classes.
2. Implement single-column stacking for FlightCard, RestaurantCard, and CalendarSlotCard at sm breakpoint (640px).
3. Verify all interactive elements (buttons, inputs, time slots) have a minimum 48×48px touch target; apply Tailwind min-h-12 min-w-12 where needed.
4. Implement responsive chat layout in ChatWindow: full-width input bar and message list at 375px; constrained max-width layout at 1440px.
5. Implement responsive login page layout: full-width card at mobile, centered constrained card at desktop.
6. Validate no component causes horizontal scroll at 375px viewport width.
7. Validate cards collapse gracefully rather than overflowing at narrow widths.

## 8. Dependencies
- Domain response card components (FlightCard, RestaurantCard, CalendarSlotCard must exist)
- ChatWindow component (must exist)
- Tailwind CSS

## 9. Test Plan
- Unit tests: Tailwind class presence for responsive breakpoints on each component.
- Integration tests: Visual render at 375px and 1440px viewports.
- Workflow tests: Full chat and card interaction at 375px; no horizontal scroll; touch targets meet 48×48px minimum.

## 10. Acceptance Criteria Mapping
- FR-001 The chat interface is usable at viewport widths from 375px to 1440px. -> Validate chat renders and is interactive at both breakpoints.
- FR-002 Domain-specific cards reflow appropriately at smaller widths. -> Validate single-column stacking at sm breakpoint.
- FR-003 Touch targets meet minimum size requirements (48×48px). -> Validate all interactive elements have min-h-12 min-w-12.

## 11. Open Questions
- None identified from the current requirements.
