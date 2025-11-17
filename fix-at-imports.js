const fs = require('fs');
const path = require('path');

function fixAtImports(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  const dir = path.dirname(filePath);

  // Determine the correct relative path based on file location
  const isInSrc = dir === '/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src';
  const isInPages = dir.includes('/pages');
  const isInComponents = dir.includes('/components');
  const isInHooks = dir.includes('/hooks');
  const isInLib = dir.includes('/lib');
  const isInUI = dir.includes('/components/ui');

  if (isInSrc) {
    // Files directly in src/
    content = content.replace(/from ["']@\//g, 'from "./');
  } else if (isInPages) {
    // Files in pages/
    content = content.replace(/from ["']@\//g, 'from "../');
  } else if (isInUI) {
    // Files in components/ui/
    content = content.replace(/from ["']@\//g, 'from "../../');
  } else if (isInComponents) {
    // Files in components/ or components/sections/
    content = content.replace(/from ["']@\//g, 'from "../');
  } else if (isInHooks || isInLib) {
    // Files in hooks/ or lib/
    content = content.replace(/from ["']@\//g, 'from "../');
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
      if (fixAtImports(fullPath)) {
        count++;
      }
    }
  }

  return count;
}

console.log('Fixing @/ imports...');
const fixed = walkDir('/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src');
console.log(`Fixed ${fixed} files`);
