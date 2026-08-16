---
name: image-annotations
description: 'Annotate screenshots, diagrams, and images with callout rectangles, arrows, labels, and color-coded highlights using PIL. Includes rules for animated GIF annotations with timing and pacing.'
---

# Image Annotations

Add visual callouts to any image — screenshots, diagrams, architecture docs, demo frames — using PIL/Pillow. Highlights what changed or what to look at, so reviewers don't have to guess.

## When to Use This Skill

Use this skill when you need to:

- Highlight a specific area in a screenshot for a PR description
- Annotate before/after images to show what changed
- Add labels and callouts to diagrams or architecture images
- Create annotated frames for animated GIF demos

## Prerequisites

```bash
pip install Pillow -q
```

## Color Rules

- **Red (`#E63946`)** — only for "bad" / "removed" things (e.g., circling a bug being fixed)
- **Yellowish-orange (`#FF9F1C`)** — for neutral highlights ("look here", "new feature", etc.)
- Never use red just because it's eye-catching — red = bad/removed

## Font

- Use **Ink Free** (`C:/Windows/Fonts/Inkfree.ttf`) for a handwritten look on Windows
- On Linux/macOS, fall back to `ImageFont.load_default()`
- Size **36** for annotations on ~1400px-wide images
- `stroke_width=1` with `stroke_fill=<same color as fill>` — gives body without being too thick
- Do NOT use white stroke — looks like a bad glow effect

## Shapes

- Prefer **rounded rectangles** over circles/ellipses — less pixelation at edges
- `draw.rounded_rectangle([x1, y1, x2, y2], radius=14, outline=color, width=5)`
- **Padding 18px** around the target content

## Reference Snippet

```python
from PIL import Image, ImageDraw, ImageFont

# Setup
font = ImageFont.truetype('C:/Windows/Fonts/Inkfree.ttf', 36)  # or load_default()
color = '#FF9F1C'  # orange for highlights
stroke = 5
pad = 18

img = Image.open('screenshot.png')
draw = ImageDraw.Draw(img)

# Rounded rect with padding
draw.rounded_rectangle(
    [x1 - pad, y1 - pad, x2 + pad, y2 + pad],
    radius=14, outline=color, width=stroke
)

# Leader line (same thickness as rect)
draw.line([x2 + pad, cy, x2 + pad + 40, cy - 30], fill=color, width=stroke)

# Label — same-color stroke for body, NO white stroke
draw.text(
    (x2 + pad + 45, cy - 60), 'label text',
    fill=color, font=font, stroke_width=1, stroke_fill=color
)

img.save('annotated.png')
```

## Algorithmic Annotation — `annotate.py`

For images with multiple elements to annotate, use the `annotate.py` module below. Save it next to your script and import from it. It handles automatic label placement without overlapping.

### Quick start

```python
from annotate import annotate_image

result = annotate_image(
    'screenshot.png',
    [
        {'elem': (560, 275, 635, 390), 'label': 'button', 'draw_box': True},
        {'elem': (105, 453, 236, 470), 'label': 'status text'},
    ],
    debug=True,
)
result.save('annotated.png')
```

- `elem`: `(x1, y1, x2, y2)` tight bounding box — must be exact pixel coordinates
- `label`: text label (supports `\n` for multi-line)
- `draw_box`: if `True`, draws a rounded rectangle around the element. If `False` (default), draws a V-arrowhead pointing at the element
- `debug`: shows targeting rectangles and candidate heatmap for placement validation

### Coordinate grid helper

**Always use `grid_image()` before annotating an unfamiliar image.** Scaled-down previews display images smaller than actual pixel dimensions — the error compounds as you move away from (0,0).

```python
from annotate import grid_image

grid = grid_image('screenshot.png', step=100)
grid.save('grid.png')
```

Then verify with small crops:

```python
from PIL import Image
img = Image.open('screenshot.png')
crop = img.crop((x1 - 20, y1 - 20, x2 + 20, y2 + 20))
crop.save('verify.png')
```

### Algorithm overview

1. **Ring search**: candidates between MIN_ARROW (25px) and MAX_ARROW (120px) from element edge
2. **Contrast scoring**: prefers placements where label text is readable — `abs(avg_brightness - 147) - std * 0.3 - dist * 0.02`
3. **Joint resolution**: candidates computed independently, placed greedily (best score first)
4. **Hard blocks**: labels cannot overlap any other annotation's element or breathing box
5. **Proximity penalty**: labels within 40px of other placed boxes get a score penalty
6. **Arrow crossing penalty**: -50 for arrows crossing already-placed arrows

### Debug mode colors

| Color | Meaning |
|-------|---------|
| Cyan | Target element box (elem + padding) |
| Gray | Exclusion zone (MIN_ARROW buffer) |
| Red→Green | Candidate heatmap (red=bad, green=good) |
| Magenta | Chosen label position |
| Orange | Final rendered annotation |

### Arrow styles

- **`draw_box=True`**: rounded rectangle + straight line to label, no arrowhead
- **`draw_box=False`**: V-shaped arrowhead with rounded line caps


## Extended guidance

Detailed sections were moved without removing content. Load only the sections needed for the current task:

- [`annotate.py` — full module](references/extended-guidance.md#annotatepy-full-module)
- [Image Diffing](references/extended-guidance.md#image-diffing)
- [Animated GIF Annotations](references/extended-guidance.md#animated-gif-annotations)
- [Element highlighting](references/extended-guidance.md#element-highlighting)
- [Timing and pacing](references/extended-guidance.md#timing-and-pacing)
- [Pop-in fade implementation](references/extended-guidance.md#pop-in-fade-implementation)
- [Guidelines](references/extended-guidance.md#guidelines)
- [Limitations](references/extended-guidance.md#limitations)

