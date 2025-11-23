let editor;

window.require(["vs/editor/editor.main"], function () {
    editor = monaco.editor.create(document.getElementById("editorContainer"), {
        value: `complex S1 = [A, B, C]
complex S2 = [D, E, F]
complex K  = glue(S1, S2) mapping {B -> E, C -> F}`,
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

    for (const [name, complex] of Object.entries(complexes)) {

    const card = document.createElement("div");
    card.className = "output-card";

    const cardInfo = document.createElement("div");
    cardInfo.className = "output-card-info";
    cardInfo.innerHTML = (`
        <h3>${name}</h3>
        <span class="output-section-title">Vertices:</span>
        <span class="output-list">${complex.vertices.join(", ")}</span>

        <span class="output-section-title">Simplices:</span>
        <span class="output-list">
            ${complex.simplices.map(s => `[${s.join(", ")}]`)}
        </span>

        <span class="output-section-title">Classes:</span>
        <span class="output-list">
            ${Object.entries(complex.classes)
                .map(([k, v]) => `${k} → [${v.join(", ")}]`)}
        </span>
    `);

    const renderBtn = document.createElement("button");
    renderBtn.textContent = "Render";
    renderBtn.style.marginTop = "10px";
    renderBtn.addEventListener("click", () => {
        window.renderComplex3D(complex);
    });

    card.appendChild(renderBtn);
    card.appendChild(cardInfo);
    outputArea.appendChild(card);
}

});
