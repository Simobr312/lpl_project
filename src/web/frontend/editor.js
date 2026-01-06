let editor;

window.require(["vs/editor/editor.main"], function () {
    editor = monaco.editor.create(document.getElementById("editorContainer"), {
        value: `complex S1 = [A, B, C]
complex S2 = union([A, B], [B, D], [D, A])
complex K  = union(S1,S2)`,
        language: "plaintext",
        theme: "vs-dark",
        automaticLayout: true
    });
});

document.getElementById("runBtn").addEventListener("click", async () => {
    const code = editor.getValue();
    const outputArea = document.getElementById("outputArea");

    outputArea.textContent = "Running...\n";

    const response = await fetch("/run_program", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ program: code })
    });

    const result = await response.json();

    if (!result.success) {
        outputArea.innerHTML = `<div class="output-card"><h3>Error</h3><pre>${result.error}</pre></div>`;
        return;
    }

    const complexes = result.complexes;
    outputArea.innerHTML = "";

    for (const [name, complex] of Object.entries(complexes).reverse()) {
        const card = document.createElement("div");
        card.className = "output-card";

        const title = document.createElement("div");
        title.className = "output-card-title";
        title.textContent = name;

        const row = document.createElement("div");
        row.className = "output-card-row";

        const cardInfo = document.createElement("div");
        cardInfo.className = "output-card-info";

        cardInfo.innerHTML = `
        <div class="row"><span class="label">Vertices</span><span>${complex.vertices.join(", ")}</span></div>
        <div class="row"><span class="label">Simplices</span><span>${complex.simplices.map(s => `[${s.join(", ")}]`).join(" ")}</span></div>
        <div class="row"><span class="label">Classes</span><span>${
            Object.entries(complex.classes)
                .map(([k, v]) => `${k}→[${v.join(", ")}]`)
                .join(" ")
        }</span></div>
        <div class="row"><span class="label">Homology</span><span>${
            Object.entries(complex.homology)
                .map(([k, r]) => `b${k}=${r}`)
                .join(" ")
        }</span></div>
        `;

        const renderBtn = document.createElement("button");
        renderBtn.textContent = "Render";
        renderBtn.className = "render-btn";
        renderBtn.addEventListener("click", () => {
            window.renderComplex3D(complex);
        });

        row.appendChild(cardInfo);
        row.appendChild(renderBtn);
        card.appendChild(title);
        card.appendChild(row);
        outputArea.appendChild(card);
    }

});
