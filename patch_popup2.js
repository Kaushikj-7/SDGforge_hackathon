const fs = require('fs');
['browser-extension', 'extension'].forEach(env => {
  let js = fs.readFileSync(env + '/popup.js', 'utf8');
  js = js.split('textContent = ${confPercent}%;').join('textContent = `${confPercent}%`;');
  js = js.split('fetch(`${BACKEND_URL}/verify/image, {').join('fetch(`${BACKEND_URL}/verify/image`, {');
  js = js.split('document.getElementById("stat-confidence").textContent = `${confPercent}`;').join('document.getElementById("stat-confidence").textContent = `${confPercent}%`;');
  fs.writeFileSync(env + '/popup.js', js);
});
