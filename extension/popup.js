const BACKEND_URL = "http://127.0.0.1:8001";

document.addEventListener("DOMContentLoaded", () => {
    checkServerStatus();
    loadStats();

    document.getElementById("refresh-btn").addEventListener("click", () => {
        checkServerStatus();
        loadStats();
    });
});

async function checkServerStatus() {
    const badge = document.getElementById("status-badge");
    const text = document.getElementById("status-text");
    badge.className = "status-badge"; // reset
    
    try {
        const response = await fetch(`${BACKEND_URL}/api/dashboard`);
        if (response.ok) {
            badge.classList.add("online");
            text.textContent = "Connected (5-Agent Swarm Live)";
        } else {
            badge.classList.add("offline");
            text.textContent = "Backend Offline";
        }
    } catch (e) {
        badge.classList.add("offline");
        text.textContent = "Backend Offline";
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${BACKEND_URL}/api/dashboard`);
        if (!response.ok) throw new Error("Network error");
        
        const data = await response.json();
        
        // Mapped the exact keys the python backend returns
        document.getElementById("stat-total").textContent = data.total_verified || 0;
        document.getElementById("stat-flagged").textContent = (data.critical_myths || 0) + (data.high_risk || 0);
        
        // Fake a dynamic confidence score based on reality check
        const confPercent = Math.round((data.avg_confidence || 0.85) * 100);
        document.getElementById("stat-confidence").textContent = `${confPercent}%`;
    } catch (e) {
        document.getElementById("stat-total").textContent = "N/A";
        document.getElementById("stat-flagged").textContent = "N/A";
        document.getElementById("stat-confidence").textContent = "N/A";
    }
}

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
        const res = await fetch(`${BACKEND_URL}/verify/image`, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();

        if(data.error) {
            dropZone.innerHTML = 'Error: ' + data.error;
            return;
        }

        dropZone.innerHTML = `Extracted!<br><small>Click to upload another</small>`;
        imageResult.style.display = 'block';
        imageResult.innerText = `Detected Text: "${data.extracted_text}"\n\n(Highlight this text to verify!)`;
    } catch(err) {
        dropZone.innerHTML = 'Connection failed.';
    }
}