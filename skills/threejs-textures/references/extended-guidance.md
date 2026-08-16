<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

## CubeCamera

Dynamic environment maps for reflections.

```javascript
const cubeRenderTarget = new THREE.WebGLCubeRenderTarget(256, {
  generateMipmaps: true,
  minFilter: THREE.LinearMipmapLinearFilter,
});

const cubeCamera = new THREE.CubeCamera(0.1, 1000, cubeRenderTarget);
scene.add(cubeCamera);

// Apply to reflective material
reflectiveMaterial.envMap = cubeRenderTarget.texture;

// Update in animation loop (expensive!)
function animate() {
  // Hide reflective object, update env map, show again
  reflectiveObject.visible = false;
  cubeCamera.position.copy(reflectiveObject.position);
  cubeCamera.update(renderer, scene);
  reflectiveObject.visible = true;
}
```

## UV Mapping

### Accessing UVs

```javascript
const uvs = geometry.attributes.uv;

// Read UV
const u = uvs.getX(vertexIndex);
const v = uvs.getY(vertexIndex);

// Modify UV
uvs.setXY(vertexIndex, newU, newV);
uvs.needsUpdate = true;
```

### Second UV Channel (for AO maps)

```javascript
// Required for aoMap
geometry.setAttribute("uv2", geometry.attributes.uv);

// Or create custom second UV
const uv2 = new Float32Array(vertexCount * 2);
// ... fill uv2 data
geometry.setAttribute("uv2", new THREE.BufferAttribute(uv2, 2));
```

### UV Transform in Shader

```javascript
const material = new THREE.ShaderMaterial({
  uniforms: {
    map: { value: texture },
    uvOffset: { value: new THREE.Vector2(0, 0) },
    uvScale: { value: new THREE.Vector2(1, 1) },
  },
  vertexShader: `
    varying vec2 vUv;
    uniform vec2 uvOffset;
    uniform vec2 uvScale;

    void main() {
      vUv = uv * uvScale + uvOffset;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    varying vec2 vUv;
    uniform sampler2D map;

    void main() {
      gl_FragColor = texture2D(map, vUv);
    }
  `,
});
```

## Texture Atlas

Multiple images in one texture.

```javascript
// Atlas with 4 sprites (2x2 grid)
const atlas = loader.load("atlas.png");
atlas.wrapS = THREE.ClampToEdgeWrapping;
atlas.wrapT = THREE.ClampToEdgeWrapping;

// Select sprite by UV offset/scale
function selectSprite(row, col, gridSize = 2) {
  atlas.offset.set(col / gridSize, 1 - (row + 1) / gridSize);
  atlas.repeat.set(1 / gridSize, 1 / gridSize);
}

// Select top-left sprite
selectSprite(0, 0);
```

## Material Texture Maps

### PBR Texture Set

```javascript
const material = new THREE.MeshStandardMaterial({
  // Base color (sRGB)
  map: colorTexture,

  // Surface detail (Linear)
  normalMap: normalTexture,
  normalScale: new THREE.Vector2(1, 1),

  // Roughness (Linear, grayscale)
  roughnessMap: roughnessTexture,
  roughness: 1, // Multiplier

  // Metalness (Linear, grayscale)
  metalnessMap: metalnessTexture,
  metalness: 1, // Multiplier

  // Ambient occlusion (Linear, uses uv2)
  aoMap: aoTexture,
  aoMapIntensity: 1,

  // Self-illumination (sRGB)
  emissiveMap: emissiveTexture,
  emissive: 0xffffff,
  emissiveIntensity: 1,

  // Vertex displacement (Linear)
  displacementMap: displacementTexture,
  displacementScale: 0.1,
  displacementBias: 0,

  // Alpha (Linear)
  alphaMap: alphaTexture,
  transparent: true,
});

// Don't forget UV2 for AO
geometry.setAttribute("uv2", geometry.attributes.uv);
```

### Normal Map Types

```javascript
// OpenGL style normals (default)
material.normalMapType = THREE.TangentSpaceNormalMap;

// Object space normals
material.normalMapType = THREE.ObjectSpaceNormalMap;
```

## Procedural Textures

### Noise Texture

```javascript
function generateNoiseTexture(size = 256) {
  const data = new Uint8Array(size * size * 4);

  for (let i = 0; i < size * size; i++) {
    const value = Math.random() * 255;
    data[i * 4] = value;
    data[i * 4 + 1] = value;
    data[i * 4 + 2] = value;
    data[i * 4 + 3] = 255;
  }

  const texture = new THREE.DataTexture(data, size, size);
  texture.needsUpdate = true;
  return texture;
}
```

### Gradient Texture

```javascript
function generateGradientTexture(color1, color2, size = 256) {
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = 1;
  const ctx = canvas.getContext("2d");

  const gradient = ctx.createLinearGradient(0, 0, size, 0);
  gradient.addColorStop(0, color1);
  gradient.addColorStop(1, color2);

  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, size, 1);

  return new THREE.CanvasTexture(canvas);
}
```

## Texture Memory Management

### Dispose Textures

```javascript
// Single texture
texture.dispose();

// Material textures
function disposeMaterial(material) {
  const maps = [
    "map",
    "normalMap",
    "roughnessMap",
    "metalnessMap",
    "aoMap",
    "emissiveMap",
    "displacementMap",
    "alphaMap",
    "envMap",
    "lightMap",
    "bumpMap",
    "specularMap",
  ];

  maps.forEach((mapName) => {
    if (material[mapName]) {
      material[mapName].dispose();
    }
  });

  material.dispose();
}
```

### Texture Pooling

```javascript
class TexturePool {
  constructor() {
    this.textures = new Map();
    this.loader = new THREE.TextureLoader();
  }

  async get(url) {
    if (this.textures.has(url)) {
      return this.textures.get(url);
    }

    const texture = await new Promise((resolve, reject) => {
      this.loader.load(url, resolve, undefined, reject);
    });

    this.textures.set(url, texture);
    return texture;
  }

  dispose(url) {
    const texture = this.textures.get(url);
    if (texture) {
      texture.dispose();
      this.textures.delete(url);
    }
  }

  disposeAll() {
    this.textures.forEach((t) => t.dispose());
    this.textures.clear();
  }
}
```

## Performance Tips

1. **Use power-of-2 dimensions**: 256, 512, 1024, 2048
2. **Compress textures**: KTX2/Basis for web delivery
3. **Use texture atlases**: Reduce texture switches
4. **Enable mipmaps**: For distant objects
5. **Limit texture size**: 2048 usually sufficient for web
6. **Reuse textures**: Same texture = better batching

```javascript
// Check texture memory
console.log(renderer.info.memory.textures);

// Optimize for mobile
const maxSize = renderer.capabilities.maxTextureSize;
const isMobile = /iPhone|iPad|Android/i.test(navigator.userAgent);
const textureSize = isMobile ? 1024 : 2048;
```

## See Also

- `threejs-materials` - Applying textures to materials
- `threejs-loaders` - Loading texture files
- `threejs-shaders` - Custom texture sampling
