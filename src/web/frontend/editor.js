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

    outputArea.textContent = result.success
        ? JSON.stringify(result.complexes, null, 2)
        : "Error:\n" + result.error;
});
