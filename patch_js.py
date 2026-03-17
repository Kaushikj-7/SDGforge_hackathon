import re

with open('extension/popup.js', 'r', encoding='utf-8') as f:
    js = f.read()

image_logic = '''
// Multimodal Image Upload
const dropZone = document.getElementById('drop-zone');
const imageUpload = document.getElementById('image-upload');
const imageResult = document.getElementById('image-result');

if(dropZone) {
    dropZone.addEventListener('click', () => imageUpload.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.background = 'rgba(26,115,232,0.15)';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.background = 'rgba(26,115,232,0.05)';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.background = 'rgba(26,115,232,0.05)';
        if(e.dataTransfer.files.length) {
            handleImageUpload(e.dataTransfer.files[0]);
        }
    });

    imageUpload.addEventListener('change', (e) => {
        if(e.target.files.length) {
            handleImageUpload(e.target.files[0]);
        }
    });
}

async function handleImageUpload(file) {
    dropZone.innerHTML = '<span class="status-dot"></span> Extracting text...';
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const res = await fetch(${API_URL}/verify/image, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        
        if(data.error) {
            dropZone.innerHTML = 'Error: ' + data.error;
            return;
        }
        
        dropZone.innerHTML = Extracted!<br><small>Click to upload another</small>;
        imageResult.style.display = 'block';
        imageResult.innerText = Detected Text: ""\n\n(Highlight this text in any webpage to verify!);
        
    } catch(err) {
        dropZone.innerHTML = 'Connection failed.';
    }
}
'''

if "handleImageUpload" not in js:
    with open('extension/popup.js', 'a', encoding='utf-8') as f:
        f.write("\n" + image_logic)
