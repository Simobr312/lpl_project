import * as THREE from 'https://unpkg.com/three@0.152.0/build/three.module.js';
import { OrbitControls } from 'https://unpkg.com/three@0.152.0/examples/jsm/controls/OrbitControls.js';

// -----------------------------------------------------------
// Build canonical vertex map
// -----------------------------------------------------------
function getCanonicalMap(complex) {
    const classes = complex.classes; // {rep: [v1, v2]}
    const map = {};
    for (const rep of Object.keys(classes)) {
        for (const v of classes[rep]) {
            map[v] = rep;
        }
    }
    return map;
}

// -----------------------------------------------------------
// Extract edges using canonical representatives
// -----------------------------------------------------------
function getEdgesCanonical(complex) {
    const canonical = getCanonicalMap(complex);
    const edges = new Set();

    for (const simplex of complex.simplices) {
        const canon = simplex.map(v => canonical[v]);
        for (let i = 0; i < canon.length; i++) {
            for (let j = i + 1; j < canon.length; j++) {
                const a = canon[i], b = canon[j];
                if (a !== b) {
                    edges.add(JSON.stringify([a, b].sort()));
                }
            }
        }
    }
    return Array.from(edges).map(s => JSON.parse(s));
}

// -----------------------------------------------------------
// Force-directed 3D layout (spring embedding)
// -----------------------------------------------------------
function springLayout3D(vertices, edges, iterations = 500) {
    const vIndex = Object.fromEntries(vertices.map((v, i) => [v, i]));
    const n = vertices.length;

    const pos = Array.from({ length: n }, () => ({
        x: Math.random()*2 - 1,
        y: Math.random()*2 - 1,
        z: Math.random()*2 - 1
    }));

    const k = 1;
    const repulsion = 0.5;

    for (let iter = 0; iter < iterations; iter++) {
        const forces = pos.map(() => ({x:0,y:0,z:0}));

        for (const [a,b] of edges) {
            const i = vIndex[a], j = vIndex[b];
            const dx = pos[j].x - pos[i].x;
            const dy = pos[j].y - pos[i].y;
            const dz = pos[j].z - pos[i].z;
            const dist = Math.sqrt(dx*dx + dy*dy + dz*dz) + 1e-6;
            const force = (dist - k) * 0.1;

            const fx = force * dx/dist;
            const fy = force * dy/dist;
            const fz = force * dz/dist;

            forces[i].x += fx;   forces[i].y += fy;   forces[i].z += fz;
            forces[j].x -= fx;   forces[j].y -= fy;   forces[j].z -= fz;
        }

        for (let i = 0; i < n; i++) {
            for (let j = i + 1; j < n; j++) {
                const dx = pos[j].x - pos[i].x;
                const dy = pos[j].y - pos[i].y;
                const dz = pos[j].z - pos[i].z;
                const dist = Math.sqrt(dx*dx + dy*dy + dz*dz) + 1e-6;

                const force = repulsion / (dist*dist);

                forces[i].x -= force * dx/dist;
                forces[i].y -= force * dy/dist;
                forces[i].z -= force * dz/dist;

                forces[j].x += force * dx/dist;
                forces[j].y += force * dy/dist;
                forces[j].z += force * dz/dist;
            }
        }

        for (let i = 0; i < n; i++) {
            pos[i].x += forces[i].x * 0.1;
            pos[i].y += forces[i].y * 0.1;
            pos[i].z += forces[i].z * 0.1;
        }
    }

    const result = {};
    for (let i = 0; i < n; i++) {
        result[vertices[i]] = [pos[i].x, pos[i].y, pos[i].z];
    }
    return result;
}

// -----------------------------------------------------------
// Create sprite with text
// -----------------------------------------------------------
function makeTextSprite(message, parameters = {}) {
    const fontSize = parameters.fontSize || 20;
    const color = parameters.color || '#000000';

    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    context.font = `${fontSize}px Arial`;
    const textWidth = context.measureText(message).width;
    canvas.width = textWidth + 20;
    canvas.height = fontSize + 10;

    context.font = `${fontSize}px Arial`;
    context.fillStyle = color;
    context.fillText(message, 10, fontSize);

    const texture = new THREE.CanvasTexture(canvas);
    texture.needsUpdate = true;

    const material = new THREE.SpriteMaterial({map: texture, transparent: true });
    const sprite = new THREE.Sprite(material);

    sprite.scale.set(canvas.width / 100, canvas.height / 100, 1);
    return sprite;
}

// -----------------------------------------------------------
// Render complex 3D
// -----------------------------------------------------------
function renderComplex3D(complex) {
    const canvas = document.getElementById("visualizationCanvas");

    if (window.THREE_RENDERER) {
        window.THREE_RENDERER.dispose();
    }

    const renderer = new THREE.WebGLRenderer({
        canvas,
        antialias: true
    });

    renderer.setPixelRatio(devicePixelRatio);
    renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
    window.THREE_RENDERER = renderer;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xffffff);

    const camera = new THREE.PerspectiveCamera(
        60,
        canvas.clientWidth / canvas.clientHeight,
        0.01,
        1000
    );
    camera.position.set(3, 3, 3);
    camera.lookAt(0, 0, 0);

    const controls = new OrbitControls(camera, renderer.domElement);

    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(3, 5, 5);
    scene.add(light);

    // -----------------------------------------------------------
    // Vertices, edges, coords
    // -----------------------------------------------------------
    const canonical = getCanonicalMap(complex);
    const canonicalVertices = [...new Set(Object.values(canonical))];
    const edges = getEdgesCanonical(complex);
    const coords = springLayout3D(canonicalVertices, edges);

    // -----------------------------------------------------------
    // Draw edges
    // -----------------------------------------------------------
    const lineMat = new THREE.LineBasicMaterial({ color: 0x888888 });
    for (const [a, b] of edges) {
        const geo = new THREE.BufferGeometry();
        const pts = new Float32Array([...coords[a], ...coords[b]]);
        geo.setAttribute("position", new THREE.BufferAttribute(pts, 3));
        const line = new THREE.Line(geo, lineMat);
        scene.add(line);
    }

    // -----------------------------------------------------------
    // Draw 2-simplices
    // -----------------------------------------------------------
    const faceMat = new THREE.MeshBasicMaterial({
        color: 0xdddddd,
        transparent: true,
        opacity: 0.33,
        side: THREE.DoubleSide
    });

    for (const simplex of complex.simplices) {
        const canon = simplex.map(v => canonical[v]);
        if (canon.length < 3) continue;

        const pts = canon.map(v => new THREE.Vector3(...coords[v]));
        if (pts.length === 3) {
            const geo = new THREE.BufferGeometry().setFromPoints(pts);
            geo.setIndex([0,1,2]);
            geo.computeVertexNormals();
            const mesh = new THREE.Mesh(geo, faceMat);
            scene.add(mesh);
        }
    }

    // -----------------------------------------------------------
    // Draw 3-simplices
    // -----------------------------------------------------------
    const solidMat = new THREE.MeshBasicMaterial({
        color: 0xcccccc,
        transparent: true,
        opacity: 0.9,
        side: THREE.DoubleSide
    });
    
    for (const simplex of complex.simplices) {
        const canon = simplex.map(v => canonical[v]);
        if (canon.length < 4) continue;
        const pts = canon.map(v => new THREE.Vector3(...coords[v]));
        if (pts.length === 4) {
            const geo = new THREE.BufferGeometry().setFromPoints(pts);
            geo.setIndex([
                0,1,2,
                0,1,3,
                0,2,3,
                1,2,3
            ]);
            geo.computeVertexNormals();
            const mesh = new THREE.Mesh(geo, solidMat);
            scene.add(mesh);
        }
    }

    // -----------------------------------------------------------
    // Draw vertices + labels inside canvas
    // -----------------------------------------------------------
    for (const v of canonicalVertices) {
        const sphereGeo = new THREE.SphereGeometry(0.05, 16, 16);
        const mat = new THREE.MeshBasicMaterial({ color: 0x0000ff });
        const s = new THREE.Mesh(sphereGeo, mat);
        s.position.set(...coords[v]);
        scene.add(s);

        const original = Object.entries(canonical)
            .filter(([k,r]) => r === v)
            .map(([k]) => k)
            .join(",");

        const labelSprite = makeTextSprite(original);
        labelSprite.position.set(...coords[v]);
        labelSprite.position.y += 0.15; // sopra il vertice
        scene.add(labelSprite);
    }

    // -----------------------------------------------------------
    // Resize and animate
    // -----------------------------------------------------------
    function resizeRenderer() {
        const wrapper = document.getElementById("visWrapper");
        const width = wrapper.clientWidth;
        const height = wrapper.clientHeight;
        renderer.setSize(width, height, false);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
    }

    resizeRenderer();
    window.addEventListener("resize", resizeRenderer);

    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();
}

// Esponi la funzione globalmente
window.renderComplex3D = renderComplex3D;
