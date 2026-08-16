<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

## Mobile-Safe Parallax

### Detection
```javascript
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
// Or better: check viewport width
const isMobile = window.innerWidth < 768;
```

### Reduce or Disable
```javascript
if (isMobile) {
  // Simpler animations
  gsap.to('.element', {
    scrollTrigger: { scrub: true },
    y: -50, // Less movement than desktop
  });
} else {
  // Full parallax
  gsap.to('.element', {
    scrollTrigger: { scrub: true },
    y: -200,
  });
}
```

### iOS-Specific Fix
```css
/* Helps with iOS scroll issues */
.scroll-container {
  -webkit-overflow-scrolling: touch;
}

.parallax-layer {
  transform: translate3d(0, 0, 0);
  backface-visibility: hidden;
}
```

### Alternative: CSS Only
```css
/* Works better on mobile */
@supports (animation-timeline: scroll()) {
  .parallax {
    animation: parallax linear;
    animation-timeline: scroll();
  }
}
```

### Scroll experience is inaccessible

Severity: MEDIUM

Situation: Screen readers and keyboard users can't use the site

Symptoms:
- Failed accessibility audit
- Can't navigate with keyboard
- Screen reader doesn't work
- Vestibular disorder complaints

Why this breaks:
Animations hide content.
Scroll hijacking breaks navigation.
No reduced motion support.
Focus management ignored.

Recommended fix:

## Accessible Scroll Experiences

### Respect Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

```javascript
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches;

if (!prefersReducedMotion) {
  initScrollAnimations();
}
```

### Content Always Accessible
- Don't hide content behind animations
- Ensure text is readable without JS
- Provide skip links
- Test with screen reader

### Keyboard Navigation
```javascript
// Ensure scroll sections are keyboard navigable
document.querySelectorAll('.scroll-section').forEach(section => {
  section.setAttribute('tabindex', '0');
});
```

### Critical content hidden below animations

Severity: MEDIUM

Situation: Users have to scroll through animations to find content

Symptoms:
- High bounce rate
- Low time on page (paradoxically)
- SEO ranking issues
- User complaints about finding info

Why this breaks:
Prioritized experience over content.
Long scroll to reach info.
SEO suffering.
Mobile users bounce.

Recommended fix:

## Content-First Scroll Design

### Above-the-Fold Content
- Key message visible immediately
- CTA visible without scroll
- Value proposition clear
- Skip animation option

### Progressive Enhancement
```
Level 1: Content readable without JS
Level 2: Basic styling and layout
Level 3: Scroll animations enhance
```

### SEO Considerations
- Text in DOM, not just in canvas
- Proper heading hierarchy
- Content not hidden by default
- Fast initial load

### Quick Exit Points
- Clear navigation always visible
- Skip to content links
- Don't trap users in experience

## Validation Checks

### No Reduced Motion Support

Severity: HIGH

Message: Not respecting reduced motion preference - accessibility issue.

Fix action: Add prefers-reduced-motion media query to disable/reduce animations

### Unthrottled Scroll Events

Severity: MEDIUM

Message: Scroll events may not be throttled - potential jank.

Fix action: Use requestAnimationFrame or GSAP ScrollTrigger for smooth performance

### Animating Layout-Triggering Properties

Severity: MEDIUM

Message: Animating layout properties causes jank.

Fix action: Use transform (translate, scale) and opacity instead

### Missing will-change Optimization

Severity: LOW

Message: Consider adding will-change for heavy animations.

Fix action: Add will-change: transform to frequently animated elements

### Scroll Hijacking Detected

Severity: MEDIUM

Message: May be hijacking scroll behavior.

Fix action: Let users scroll naturally, use scrub animations instead

## Collaboration

### Delegation Triggers

- 3D|WebGL|three.js|spline -> 3d-web-experience (3D elements in scroll experience)
- react|vue|next|framework -> frontend (Frontend implementation)
- performance|slow|optimize -> performance-hunter (Performance optimization)
- design|mockup|visual -> ui-design (Visual design)

### Immersive Product Page

Skills: scroll-experience, 3d-web-experience, landing-page-design

Workflow:

```
1. Design product story structure
2. Create 3D product model
3. Build scroll-driven reveals
4. Add conversion points
5. Optimize performance
```

### Interactive Story

Skills: scroll-experience, ui-design, frontend

Workflow:

```
1. Write story/content
2. Design visual sections
3. Plan scroll animations
4. Implement with GSAP/Framer
5. Test and optimize
```

## Related Skills

Works well with: `3d-web-experience`, `frontend`, `ui-design`, `landing-page-design`

## When to Use
- User mentions or implies: scroll animation
- User mentions or implies: parallax
- User mentions or implies: scroll storytelling
- User mentions or implies: interactive story
- User mentions or implies: cinematic website
- User mentions or implies: scroll experience
- User mentions or implies: immersive web

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
