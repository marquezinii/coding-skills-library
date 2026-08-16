<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

## Anti-Patterns

### 1. Expressive Everywhere

```kotlin
// BAD - every interaction overshoots, UI feels like a bouncy castle
MaterialTheme(motionScheme = MotionScheme.expressive()) {
    AppRoot()
}

// GOOD - Standard for chrome, scope Expressive to hero moments
MaterialTheme(motionScheme = MotionScheme.standard()) {
    NavigationScaffold {
        // Hero detail screen overrides locally
        MaterialTheme(motionScheme = MotionScheme.expressive()) {
            HeroDetail()
        }
    }
}
```

### 2. RuntimeShader Without API Gate

```kotlin
// BAD - crashes on Android 12 and below
val shader = remember { RuntimeShader(AGSL_SOURCE) }

// GOOD - gate on SDK level, provide fallback
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
    ShaderEffect { content() }
} else {
    Box(modifier = Modifier.background(fallbackGradient)) { content() }
}
```

### 3. Canvas Reading State Directly Each Frame

```kotlin
// BAD - any state change in the parent triggers a recompose of the Canvas
Canvas(modifier = Modifier.fillMaxSize()) {
    drawCircle(color = if (viewModel.isActive) Color.Red else Color.Blue, radius = 50f)
}

// GOOD - hoist the reads, derive a stable value
val color by remember { derivedStateOf { if (viewModel.isActive) Color.Red else Color.Blue } }
Canvas(modifier = Modifier.fillMaxSize()) {
    drawCircle(color = color, radius = 50f)
}
```

### 4. Chaining 4 AGSL Shaders in Series

```kotlin
// BAD - 4 render passes per frame, GPU melts on mid-range devices
.graphicsLayer { renderEffect = blurEffect }
.graphicsLayer { renderEffect = chromaticEffect }
.graphicsLayer { renderEffect = noiseEffect }
.graphicsLayer { renderEffect = vignetteEffect }

// GOOD - one shader doing all the math in a single pass
.graphicsLayer { renderEffect = combinedGlassEffect }
```

### 5. Allocating in DrawScope

```kotlin
// BAD - new Path every frame, GC stutter
Canvas(modifier = Modifier.fillMaxSize()) {
    val path = Path()
    points.forEach { path.lineTo(it.x, it.y) }
    drawPath(path, color = Color.Black)
}

// GOOD - reuse a remembered Path, rewind each frame
val path = remember { Path() }
Canvas(modifier = Modifier.fillMaxSize()) {
    path.rewind()
    points.forEach { path.lineTo(it.x, it.y) }
    drawPath(path, color = Color.Black)
}
```

---

## Quick Reference: Loading Sub-resources

| Need | Load |
|---|---|
| AGSL recipes (7 working shaders with binding code) | `references/agsl-recipes.md` |
| M3 Expressive choreography deep-dive | `references/m3-expressive-deep.md` |
| Generative drawing patterns (flow fields, L-systems, particles) | `references/canvas-generative.md` |
| Base animations (animateAsState, AnimatedVisibility, Transition) | `../compose-motion/SKILL.md` |
| CMP patterns (shared UI iOS / Android / Desktop) | `../compose-multiplatform/SKILL.md` |

---

## Sources

- [drinkthestars/shady](https://github.com/drinkthestars/shady) - AGSL shaders rendered in Compose
- [Mortd3kay/liquid-glass-android](https://github.com/Mortd3kay/liquid-glass-android)
- [JumpingKeyCaps/DynamicVisualEffectsAGSL](https://github.com/JumpingKeyCaps/DynamicVisualEffectsAGSL)
- [Material 3 Expressive blog](https://m3.material.io/blog/m3-expressive-motion-theming)
- [Material Design 3 Motion specs](https://m3.material.io/styles/motion/overview/specs)
- [Android AGSL docs](https://developer.android.com/develop/ui/views/graphics/agsl/using-agsl)
- [androidx.graphics.shapes](https://developer.android.com/jetpack/androidx/releases/graphics-shapes) - shape morphing
