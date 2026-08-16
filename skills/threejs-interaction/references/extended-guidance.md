<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

## DragControls

Drag objects directly.

```javascript
import { DragControls } from "three/addons/controls/DragControls.js";

const draggableObjects = [mesh1, mesh2, mesh3];
const dragControls = new DragControls(
  draggableObjects,
  camera,
  renderer.domElement,
);

dragControls.addEventListener("dragstart", (event) => {
  orbitControls.enabled = false;
  event.object.material.emissive.set(0xaaaaaa);
});

dragControls.addEventListener("drag", (event) => {
  // Constrain to ground plane
  event.object.position.y = 0;
});

dragControls.addEventListener("dragend", (event) => {
  orbitControls.enabled = true;
  event.object.material.emissive.set(0x000000);
});
```

## Selection System

### Click to Select

```javascript
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let selectedObject = null;

function onMouseDown(event) {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(selectableObjects);

  // Deselect previous
  if (selectedObject) {
    selectedObject.material.emissive.set(0x000000);
  }

  // Select new
  if (intersects.length > 0) {
    selectedObject = intersects[0].object;
    selectedObject.material.emissive.set(0x444444);
  } else {
    selectedObject = null;
  }
}
```

### Box Selection

```javascript
import { SelectionBox } from "three/addons/interactive/SelectionBox.js";
import { SelectionHelper } from "three/addons/interactive/SelectionHelper.js";

const selectionBox = new SelectionBox(camera, scene);
const selectionHelper = new SelectionHelper(renderer, "selectBox"); // CSS class

document.addEventListener("pointerdown", (event) => {
  selectionBox.startPoint.set(
    (event.clientX / window.innerWidth) * 2 - 1,
    -(event.clientY / window.innerHeight) * 2 + 1,
    0.5,
  );
});

document.addEventListener("pointermove", (event) => {
  if (selectionHelper.isDown) {
    selectionBox.endPoint.set(
      (event.clientX / window.innerWidth) * 2 - 1,
      -(event.clientY / window.innerHeight) * 2 + 1,
      0.5,
    );
  }
});

document.addEventListener("pointerup", (event) => {
  selectionBox.endPoint.set(
    (event.clientX / window.innerWidth) * 2 - 1,
    -(event.clientY / window.innerHeight) * 2 + 1,
    0.5,
  );

  const selected = selectionBox.select();
  console.log("Selected objects:", selected);
});
```

### Hover Effects

```javascript
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let hoveredObject = null;

function onMouseMove(event) {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(hoverableObjects);

  // Reset previous hover
  if (hoveredObject) {
    hoveredObject.material.color.set(hoveredObject.userData.originalColor);
    document.body.style.cursor = "default";
  }

  // Apply new hover
  if (intersects.length > 0) {
    hoveredObject = intersects[0].object;
    if (!hoveredObject.userData.originalColor) {
      hoveredObject.userData.originalColor =
        hoveredObject.material.color.getHex();
    }
    hoveredObject.material.color.set(0xff6600);
    document.body.style.cursor = "pointer";
  } else {
    hoveredObject = null;
  }
}

window.addEventListener("mousemove", onMouseMove);
```

## Keyboard Input

```javascript
const keys = {};

document.addEventListener("keydown", (event) => {
  keys[event.code] = true;
});

document.addEventListener("keyup", (event) => {
  keys[event.code] = false;
});

function update() {
  const speed = 0.1;

  if (keys["KeyW"]) player.position.z -= speed;
  if (keys["KeyS"]) player.position.z += speed;
  if (keys["KeyA"]) player.position.x -= speed;
  if (keys["KeyD"]) player.position.x += speed;
  if (keys["Space"]) player.position.y += speed;
  if (keys["ShiftLeft"]) player.position.y -= speed;
}
```

## World-Screen Coordinate Conversion

### World to Screen

```javascript
function worldToScreen(position, camera) {
  const vector = position.clone();
  vector.project(camera);

  return {
    x: ((vector.x + 1) / 2) * window.innerWidth,
    y: (-(vector.y - 1) / 2) * window.innerHeight,
  };
}

// Position HTML element over 3D object
const screenPos = worldToScreen(mesh.position, camera);
element.style.left = screenPos.x + "px";
element.style.top = screenPos.y + "px";
```

### Screen to World

```javascript
function screenToWorld(screenX, screenY, camera, targetZ = 0) {
  const vector = new THREE.Vector3(
    (screenX / window.innerWidth) * 2 - 1,
    -(screenY / window.innerHeight) * 2 + 1,
    0.5,
  );

  vector.unproject(camera);

  const dir = vector.sub(camera.position).normalize();
  const distance = (targetZ - camera.position.z) / dir.z;

  return camera.position.clone().add(dir.multiplyScalar(distance));
}
```

### Ray-Plane Intersection

```javascript
function getRayPlaneIntersection(mouse, camera, plane) {
  const raycaster = new THREE.Raycaster();
  raycaster.setFromCamera(mouse, camera);

  const intersection = new THREE.Vector3();
  raycaster.ray.intersectPlane(plane, intersection);

  return intersection;
}

// Ground plane
const groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
const worldPos = getRayPlaneIntersection(mouse, camera, groundPlane);
```

## Event Handling Best Practices

```javascript
class InteractionManager {
  constructor(camera, renderer, scene) {
    this.camera = camera;
    this.renderer = renderer;
    this.scene = scene;
    this.raycaster = new THREE.Raycaster();
    this.mouse = new THREE.Vector2();
    this.clickables = [];

    this.bindEvents();
  }

  bindEvents() {
    const canvas = this.renderer.domElement;

    canvas.addEventListener("click", (e) => this.onClick(e));
    canvas.addEventListener("mousemove", (e) => this.onMouseMove(e));
    canvas.addEventListener("touchstart", (e) => this.onTouchStart(e));
  }

  updateMouse(event) {
    const rect = this.renderer.domElement.getBoundingClientRect();
    this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  }

  getIntersects() {
    this.raycaster.setFromCamera(this.mouse, this.camera);
    return this.raycaster.intersectObjects(this.clickables, true);
  }

  onClick(event) {
    this.updateMouse(event);
    const intersects = this.getIntersects();

    if (intersects.length > 0) {
      const object = intersects[0].object;
      if (object.userData.onClick) {
        object.userData.onClick(intersects[0]);
      }
    }
  }

  addClickable(object, callback) {
    this.clickables.push(object);
    object.userData.onClick = callback;
  }

  dispose() {
    // Remove event listeners
  }
}

// Usage
const interaction = new InteractionManager(camera, renderer, scene);
interaction.addClickable(mesh, (intersect) => {
  console.log("Clicked at:", intersect.point);
});
```

## Performance Tips

1. **Limit raycasts**: Throttle mousemove handlers
2. **Use layers**: Filter raycast targets
3. **Simple collision meshes**: Use invisible simpler geometry for raycasting
4. **Disable controls when not needed**: `controls.enabled = false`
5. **Batch updates**: Group interaction checks

```javascript
// Use simpler geometry for raycasting
const complexMesh = loadedModel;
const collisionMesh = new THREE.Mesh(
  new THREE.BoxGeometry(1, 1, 1),
  new THREE.MeshBasicMaterial({ visible: false }),
);
collisionMesh.userData.target = complexMesh;
clickables.push(collisionMesh);
```

## See Also

- `threejs-fundamentals` - Camera and scene setup
- `threejs-animation` - Animating interactions
- `threejs-shaders` - Visual feedback effects
