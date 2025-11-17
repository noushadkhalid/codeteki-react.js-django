const fs = require('fs');
const path = require('path');

function fixFile(content) {
  // Fix duplicate React imports
  const lines = content.split('\n');
  const reactImports = [];
  const otherLines = [];
  let hasReact = false;
  let hasReactStar = false;

  for (const line of lines) {
    if (line.match(/^import\s+\*\s+as\s+React\s+from\s+["']react["']/)) {
      if (!hasReactStar) {
        reactImports.push(line);
        hasReactStar = true;
      }
    } else if (line.match(/^import\s+React/)) {
      if (!hasReact) {
        reactImports.push(line);
        hasReact = true;
      }
    } else if (line.match(/^import\s+\{[^}]*\}\s+from\s+["']react["']/)) {
      reactImports.push(line);
    } else {
      otherLines.push(line);
    }
  }

  // Merge React imports if we have both `import * as React` and `import React`
  let finalImports = [];
  if (hasReactStar) {
    finalImports = reactImports.filter(line =>
      line.match(/^import\s+\*\s+as\s+React\s+from\s+["']react["']/)
    );
  } else {
    finalImports = reactImports;
  }

  content = [...finalImports, ...otherLines].join('\n');

  // Remove undefined TypeScript types usage
  content = content.replace(/:\s*ContactFormData/g, '');
  content = content.replace(/const\s+\w+:\s*[A-Z]\w+/g, (match) => {
    return match.replace(/:\s*[A-Z]\w+/, '');
  });

  // Fix common syntax errors from type removal
  // Fix: extends keyword left over
  content = content.replace(/extends\s+React\.\w+Props[^>]*/g, '');
  content = content.replace(/extends\s+\w+Props[^>]*/g, '');

  return content;
}

function processFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const fixed = fixFile(content);

    if (content !== fixed) {
      fs.writeFileSync(filePath, fixed, 'utf8');
      const shortPath = filePath.replace('/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src/', '');
      console.log(`Fixed: ${shortPath}`);
      return true;
    }
    return false;
  } catch (error) {
    console.error(`Error processing ${filePath}:`, error.message);
    return false;
  }
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
      if (processFile(fullPath)) {
        count++;
      }
    }
  }

  return count;
}

console.log('Fixing remaining issues...');
const fixed = walkDir('/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src');
console.log(`\nFixed ${fixed} files`);
