const fs = require('fs');
const path = require('path');

function finalCleanup(content) {
  // 1. Remove multi-line React.forwardRef generic types
  // This regex handles the pattern across multiple lines
  content = content.replace(/React\.forwardRef<[\s\S]*?>\s*\(/g, 'React.forwardRef(');

  // 2. Remove export interface and interface declarations (including multi-line)
  content = content.replace(/export\s+interface\s+\w+[\s\S]*?\{[\s\S]*?\}\s*/g, '');
  content = content.replace(/^interface\s+\w+[\s\S]*?\{[\s\S]*?\}\s*/gm, '');

  // 3. Remove  type alias declarations
  content = content.replace(/export\s+type\s+\w+\s*=[\s\S]*?;?\s*\n/g, '');
  content = content.replace(/^type\s+\w+\s*=[\s\S]*?;?\s*\n/gm, '');

  // 4. Remove VariantProps type from extends
  content = content.replace(/extends[\s\S]*?VariantProps<[^>]+>/g, '');

  // 5. Fix duplicate React imports - keep only one
  const lines = content.split('\n');
  let hasReactImport = false;
  const filteredLines = lines.filter(line => {
    if (line.match(/^import\s+\*\s+as\s+React\s+from\s+["']react["']/)) {
      if (hasReactImport) return false;
      hasReactImport = true;
      return true;
    }
    return true;
  });
  content = filteredLines.join('\n');

  // 6. Remove complex type annotations from parameters
  // Pattern: (param: React.Something<...>) => (param)
  content = content.replace(/\(([a-zA-Z_$][\w]*)\s*:\s*React\.\w+<[^>]+>\)/g, '($1)');

  // 7. Remove type annotations with angle brackets
  content = content.replace(/:\s*\w+<[^>]+>/g, '');

  // 8. Clean up empty lines (max 2 consecutive)
  content = content.replace(/\n\n\n+/g, '\n\n');

  return content;
}

function processFile(filePath) {
  try {
    const originalContent = fs.readFileSync(filePath, 'utf8');
    const content = finalCleanup(originalContent);

    if (content !== originalContent) {
      fs.writeFileSync(filePath, content, 'utf8');
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

console.log('Final TypeScript cleanup...');
const fixed = walkDir('/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src');
console.log(`\nFixed ${fixed} files`);
