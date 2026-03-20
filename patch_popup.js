const fs = require('fs');
['browser-extension', 'extension'].forEach(env => {
  let js = fs.readFileSync(env + '/popup.js', 'utf8');
  js = js.split('fetch(${BACKEND_URL}/api/dashboard)').join('fetch(`${BACKEND_URL}/api/dashboard`)');
  js = js.split('fetch(${BACKEND_URL}/verify/image').join('fetch(`${BACKEND_URL}/verify/image`');
  fs.writeFileSync(env + '/popup.js', js);
});
