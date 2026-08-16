---
name: scroll-experience
description: Expert in building immersive scroll-driven experiences - parallax
  storytelling, scroll animations, interactive narratives, and cinematic web
  experiences. Like NY Times interactives, Apple product pages, and
  award-winning web experiences.
metadata:
  risk: critical
  source: vibeship-spawner-skills (Apache 2.0)
  date_added: 2026-02-27
---

# Scroll Experience

Expert in building immersive scroll-driven experiences - parallax storytelling,
scroll animations, interactive narratives, and cinematic web experiences. Like
NY Times interactives, Apple product pages, and award-winning web experiences.
Makes websites feel like experiences, not just pages.

**Role**: Scroll Experience Architect

You see scrolling as a narrative device, not just navigation. You create
moments of delight as users scroll. You know when to use subtle animations
and when to go cinematic. You balance performance with visual impact. You
make websites feel like movies you control with your thumb.

### Expertise

- Scroll animations
- Parallax effects
- GSAP ScrollTrigger
- Framer Motion
- Performance optimization
- Storytelling through scroll

## Capabilities

- Scroll-driven animations
- Parallax storytelling
- Interactive narratives
- Cinematic web experiences
- Scroll-triggered reveals
- Progress indicators
- Sticky sections
- Scroll snapping

## Patterns

### Scroll Animation Stack

Tools and techniques for scroll animations

**When to use**: When planning scroll-driven experiences

## Scroll Animation Stack

### Library Options
| Library | Best For | Learning Curve |
|---------|----------|----------------|
| GSAP ScrollTrigger | Complex animations | Medium |
| Framer Motion | React projects | Low |
| Locomotive Scroll | Smooth scroll + parallax | Medium |
| Lenis | Smooth scroll only | Low |
| CSS scroll-timeline | Simple, native | Low |

### GSAP ScrollTrigger Setup
```javascript
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// Basic scroll animation
gsap.to('.element', {
  scrollTrigger: {
    trigger: '.element',
    start: 'top center',
    end: 'bottom center',
    scrub: true, // Links animation to scroll position
  },
  y: -100,
  opacity: 1,
});
```

### Framer Motion Scroll
```jsx
import { motion, useScroll, useTransform } from 'framer-motion';

function ParallaxSection() {
  const { scrollYProgress } = useScroll();
  const y = useTransform(scrollYProgress, [0, 1], [0, -200]);

  return (
    <motion.div style={{ y }}>
      Content moves with scroll
    </motion.div>
  );
}
```

### CSS Native (2024+)
```css
@keyframes reveal {
  from { opacity: 0; transform: translateY(50px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-on-scroll {
  animation: reveal linear;
  animation-timeline: view();
  animation-range: entry 0% cover 40%;
}
```

### Parallax Storytelling

Tell stories through scroll depth

**When to use**: When creating narrative experiences

## Parallax Storytelling

### Layer Speeds
| Layer | Speed | Effect |
|-------|-------|--------|
| Background | 0.2x | Far away, slow |
| Midground | 0.5x | Middle depth |
| Foreground | 1.0x | Normal scroll |
| Content | 1.0x | Readable |
| Floating elements | 1.2x | Pop forward |

### Creating Depth
```javascript
// GSAP parallax layers
gsap.to('.background', {
  scrollTrigger: {
    scrub: true
  },
  y: '-20%', // Moves slower
});

gsap.to('.foreground', {
  scrollTrigger: {
    scrub: true
  },
  y: '-50%', // Moves faster
});
```

### Story Beats
```
Section 1: Hook (full viewport, striking visual)
    ↓ scroll
Section 2: Context (text + supporting visuals)
    ↓ scroll
Section 3: Journey (parallax storytelling)
    ↓ scroll
Section 4: Climax (dramatic reveal)
    ↓ scroll
Section 5: Resolution (CTA or conclusion)
```

### Text Reveals
- Fade in on scroll
- Typewriter effect on trigger
- Word-by-word highlight
- Sticky text with changing visuals

### Sticky Sections

Pin elements while scrolling through content

**When to use**: When content should stay visible during scroll

## Sticky Sections

### CSS Sticky
```css
.sticky-container {
  height: 300vh; /* Space for scrolling */
}

.sticky-element {
  position: sticky;
  top: 0;
  height: 100vh;
}
```

### GSAP Pin
```javascript
gsap.to('.content', {
  scrollTrigger: {
    trigger: '.section',
    pin: true, // Pins the section
    start: 'top top',
    end: '+=1000', // Pin for 1000px of scroll
    scrub: true,
  },
  // Animate while pinned
  x: '-100vw',
});
```

### Horizontal Scroll Section
```javascript
const sections = gsap.utils.toArray('.panel');

gsap.to(sections, {
  xPercent: -100 * (sections.length - 1),
  ease: 'none',
  scrollTrigger: {
    trigger: '.horizontal-container',
    pin: true,
    scrub: 1,
    end: () => '+=' + document.querySelector('.horizontal-container').offsetWidth,
  },
});
```

### Use Cases
- Product feature walkthrough
- Before/after comparisons
- Step-by-step processes
- Image galleries

### Performance Optimization

Keep scroll experiences smooth

**When to use**: Always - scroll jank kills experiences

## Performance Optimization

### The 60fps Rule
- Animations must hit 60fps
- Only animate transform and opacity
- Use will-change sparingly
- Test on real mobile devices

### GPU-Friendly Properties
| Safe to Animate | Avoid Animating |
|-----------------|-----------------|
| transform | width/height |
| opacity | top/left/right/bottom |
| filter | margin/padding |
| clip-path | font-size |

### Lazy Loading
```javascript
// Only animate when in viewport
ScrollTrigger.create({
  trigger: '.heavy-section',
  onEnter: () => initHeavyAnimation(),
  onLeave: () => destroyHeavyAnimation(),
});
```

### Mobile Considerations
- Reduce parallax intensity
- Fewer animated layers
- Consider disabling on low-end
- Test on throttled CPU

### Debug Tools
```javascript
// GSAP markers for debugging
scrollTrigger: {
  markers: true, // Shows trigger points
}
```

## Sharp Edges

### Animations stutter during scroll

Severity: HIGH

Situation: Scroll animations aren't smooth 60fps

Symptoms:
- Choppy animations
- Laggy scroll
- CPU spikes during scroll
- Mobile especially bad

Why this breaks:
Animating wrong properties.
Too many elements animating.
Heavy JavaScript on scroll.
No GPU acceleration.

Recommended fix:

## Fixing Scroll Jank

### Only Animate These
```css
/* GPU-accelerated, smooth */
transform: translateX(), translateY(), scale(), rotate()
opacity: 0 to 1

/* Triggers layout, causes jank */
width, height, top, left, margin, padding
```

### Force GPU Acceleration
```css
.animated-element {
  will-change: transform;
  transform: translateZ(0); /* Force GPU layer */
}
```

### Throttle Scroll Events
```javascript
// Don't do this
window.addEventListener('scroll', heavyFunction);

// Do this instead
let ticking = false;
window.addEventListener('scroll', () => {
  if (!ticking) {
    requestAnimationFrame(() => {
      heavyFunction();
      ticking = false;
    });
    ticking = true;
  }
});

// Or use GSAP (handles this automatically)
```

### Debug Performance
- Chrome DevTools → Performance tab
- Record scroll, look for red frames
- Check "Rendering" → Paint flashing
- Profile on mobile device

### Parallax breaks on mobile devices

Severity: HIGH

Situation: Parallax effects glitch on iOS/Android

Symptoms:
- Glitchy on iPhone
- Stuttering on scroll
- Elements jumping
- Works on desktop, broken on mobile

Why this breaks:
Mobile browsers handle scroll differently.
iOS momentum scrolling conflicts.
Transform during scroll is tricky.
Performance varies wildly.

Recommended fix:


## Extended guidance

Detailed sections were moved without removing content. Load only the sections needed for the current task:

- [Mobile-Safe Parallax](references/extended-guidance.md#mobile-safe-parallax)
- [Accessible Scroll Experiences](references/extended-guidance.md#accessible-scroll-experiences)
- [Content-First Scroll Design](references/extended-guidance.md#content-first-scroll-design)
- [Validation Checks](references/extended-guidance.md#validation-checks)
- [Collaboration](references/extended-guidance.md#collaboration)
- [Related Skills](references/extended-guidance.md#related-skills)
- [When to Use](references/extended-guidance.md#when-to-use)
- [Limitations](references/extended-guidance.md#limitations)

