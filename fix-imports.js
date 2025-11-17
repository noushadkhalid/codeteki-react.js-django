const fs = require('fs');
const path = require('path');

function fixImports(content, filePath) {
  const fileName = path.basename(filePath);
  const dirName = path.dirname(filePath);

  // Remove the @ alias imports that were incorrectly converted
  content = content.replace(/from\s+["']\.\.\/\.\.\/components\//g, 'from "./components/');
  content = content.replace(/from\s+["']\.\.\/\.\.\/lib\//g, 'from "./lib/');
  content = content.replace(/from\s+["']\.\.\/\.\.\/hooks\//g, 'from "./hooks/');
  content = content.replace(/from\s+["']\.\.\/\.\.\/pages\//g, 'from "./pages/');
  content = content.replace(/from\s+["']\.\.\/\.\.\/assets\//g, 'from "./assets/');

  // More specific paths
  content = content.replace(/from\s+["']\.\.\/ui\//g, 'from "./components/ui/');
  content = content.replace(/from\s+["']\.\.\/components\//g, 'from "./components/');

  return content;
}

function processDirectory(dir) {
  const items = fs.readdirSync(dir);

  items.forEach(item => {
    const fullPath = path.join(dir, item);
    const stats = fs.statSync(fullPath);

    if (stats.isDirectory()) {
      if (item === 'node_modules' || item.startsWith('.')) return;
      processDirectory(fullPath);
    } else if (stats.isFile() && (item.endsWith('.jsx') || item.endsWith('.js'))) {
      let content = fs.readFileSync(fullPath, 'utf8');
      const newContent = fixImports(content, fullPath);

      if (content !== newContent) {
        fs.writeFileSync(fullPath, newContent, 'utf8');
        console.log(`Fixed: ${fullPath}`);
      }
    }
  });
}

console.log('Fixing import paths...');
processDirectory('/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src');
console.log('Done!');
