const fs = require('fs');
const path = require('path');

function fixImports(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  const dir = path.dirname(filePath);

  // Determine the correct relative path based on file location
  if (dir.includes('/components/ui')) {
    // Files in components/ui/
    content = content.replace(/from ["']\.\/lib\//g, 'from "../../lib/');
    content = content.replace(/from ["']\.\/hooks\//g, 'from "../../hooks/');
    content = content.replace(/from ["']\.\/components\//g, 'from "../');
  } else if (dir.includes('/components/sections')) {
    // Files in components/sections/
    content = content.replace(/from ["']\.\/lib\//g, 'from "../../lib/');
    content = content.replace(/from ["']\.\/hooks\//g, 'from "../../hooks/');
    content = content.replace(/from ["']\.\/components\//g, 'from "../');
  } else if (dir.includes('/components')) {
    // Files directly in components/
    content = content.replace(/from ["']\.\/lib\//g, 'from "../lib/');
    content = content.replace(/from ["']\.\/hooks\//g, 'from "../hooks/');
    content = content.replace(/from ["']\.\/components\//g, 'from "./');
  } else if (dir.includes('/pages')) {
    // Files in pages/
    content = content.replace(/from ["']\.\/lib\//g, 'from "../lib/');
    content = content.replace(/from ["']\.\/hooks\//g, 'from "../hooks/');
    content = content.replace(/from ["']\.\/components\//g, 'from "../components/');
  } else if (dir.includes('/hooks')) {
    // Files in hooks/
    content = content.replace(/from ["']\.\/lib\//g, 'from "../lib/');
  } else if (dir.includes('/lib')) {
    // Files in lib/
    content = content.replace(/from ["']\.\/hooks\//g, 'from "../hooks/');
  }

  fs.writeFileSync(filePath, content, 'utf8');
  return true;
}

function walkDir(dir) {
  let count = 0;
  const items = fs.readdirSync(dir);

  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);

    if (stat.isDirectory()) {
      if (!item.startsWith('.') && item !== 'node_modules') {
        count += walkDir(fullPath);
      }
    } else if (item.endsWith('.jsx') || item.endsWith('.js')) {
      if (fixImports(fullPath)) {
        count++;
      }
    }
  }

  return count;
}

console.log('Fixing all imports...');
const fixed = walkDir('/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src');
console.log(`Fixed ${fixed} files`);
