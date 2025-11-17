const fs = require('fs');
const path = require('path');

function finalCleanup(content, filePath) {
  // Fix mismatched quotes in imports
  content = content.replace(/from\s+["']([^"']+)["']([^;])/g, (match, p1, p2) => {
    return `from "${p1}"${p2}`;
  });

  // Remove all remaining angle brackets that look like TypeScript generics
  // But be careful not to remove JSX tags
  const lines = content.split('\n');
  const cleanedLines = lines.map(line => {
    // Skip lines that look like JSX
    if (line.trim().startsWith('<') || line.trim().startsWith('return') || line.includes('</')) {
      return line;
    }
    // Remove generics from function calls
    return line.replace(/(\w+)<[\w\[\]|&,\s]+>(\s*[\(\{])/g, '$1$2');
  });

  return cleanedLines.join('\n');
}

function processFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const cleaned = finalCleanup(content, filePath);
    
    if (content !== cleaned) {
      fs.writeFileSync(filePath, cleaned, 'utf8');
      console.log(`Cleaned: ${filePath}`);
      return true;
    }
    return false;
  } catch (error) {
    console.error(`Error: ${filePath}:`, error.message);
    return false;
  }
}

function walk(dir) {
  let count = 0;
  fs.readdirSync(dir).forEach(item => {
    const fullPath = path.join(dir, item);
    if (fs.statSync(fullPath).isDirectory()) {
      if (!item.startsWith('.') && item !== 'node_modules') {
        count += walk(fullPath);
      }
    } else if (item.endsWith('.jsx') || item.endsWith('.js')) {
      if (processFile(fullPath)) count++;
    }
  });
  return count;
}

console.log('Final cleanup...');
const fixed = walk('/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src');
console.log(`Cleaned ${fixed} files`);
