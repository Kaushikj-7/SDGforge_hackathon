const fs = require('fs');
['browser-extension', 'extension'].forEach(env => {
  let js = fs.readFileSync(env + '/content.js', 'utf8');
  js = 'console.log("TruthLens/Health Fact Checker: Content Script Loaded v2.3.2");\n' + js;
  fs.writeFileSync(env + '/content.js', js);
  
  let man = JSON.parse(fs.readFileSync(env + '/manifest.json', 'utf8'));
  man.version = '2.3.2';
  fs.writeFileSync(env + '/manifest.json', JSON.stringify(man, null, 2));
});
