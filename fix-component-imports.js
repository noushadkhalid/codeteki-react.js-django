const fs = require('fs');
const path = require('path');

function fixImports(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  const dir = path.dirname(filePath);
  const basePath = '/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src';

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
        console.log(`Fixed: ${fullPath.replace('/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src/', '')}`);
        count++;
      }
    }
  }

  return count;
}

console.log('Fixing component imports...');
const fixed = walkDir('/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src/components');
console.log(`Fixed ${fixed} files`);
