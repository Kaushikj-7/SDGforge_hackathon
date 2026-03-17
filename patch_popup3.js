const fs = require('fs');

const fixFunc = `async function handleImageUpload(file) {
    dropZone.innerHTML = '<span class="status-dot"></span> Extracting text...'; 

    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await fetch(\`\${BACKEND_URL}/verify/image\`, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();

        if(data.error) {
            dropZone.innerHTML = 'Error: ' + data.error;
            return;
        }

        dropZone.innerHTML = \`Extracted!<br><small>Click to upload another</small>\`;
        imageResult.style.display = 'block';
        imageResult.innerText = \`Detected Text: "\${data.extracted_text}"\\n\\n(Highlight this text to verify!)\`;
    } catch(err) {
        dropZone.innerHTML = 'Connection failed.';
    }
}`;

['browser-extension', 'extension'].forEach(env => {
  let js = fs.readFileSync(env + '/popup.js', 'utf8');
  js = js.replace(/async function handleImageUpload\(file\) \{[\s\S]*\}\s*$/, fixFunc);
  fs.writeFileSync(env + '/popup.js', js);
});
