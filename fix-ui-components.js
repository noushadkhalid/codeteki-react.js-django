const fs = require('fs');
const path = require('path');

function fixUIComponent(content) {
  // Fix multi-line React.forwardRef generic types
  // Pattern: React.forwardRef<...multiple lines...>(
  content = content.replace(/React\.forwardRef<[\s\S]*?>\(/g, 'React.forwardRef(');
  content = content.replace(/forwardRef<[\s\S]*?>\(/g, 'forwardRef(');

  // Remove interface and type declarations (multiline safe)
  content = content.replace(/export\s+interface\s+\w+[\s\S]*?\{[\s\S]*?\}\s*\n?/g, '');
  content = content.replace(/interface\s+\w+[\s\S]*?\{[\s\S]*?\}\s*\n?/g, '');

  // Remove type annotations from destructured parameters in arrow functions
  // Pattern: ({ param }: Props) => becomes ({ param }) =>
  content = content.replace(/\(\s*\{([^}]+)\}\s*:\s*[^)]+\)/g, '({ $1 })');

  // Remove extends clauses completely
  content = content.replace(/extends\s+React\.\w+<[^>]+>/g, '');
  content = content.replace(/extends\s+\w+<[^>]+>/g, '');

  // Remove generic type parameters from React hooks and functions
  content = content.replace(/useState<[^>]+>/g, 'useState');
  content = content.replace(/useRef<[^>]+>/g, 'useRef');
  content = content.replace(/useMemo<[^>]+>/g, 'useMemo');
  content = content.replace(/useCallback<[^>]+>/g, 'useCallback');

  // Remove remaining type annotations from parameters
  // Simple pattern: (param: Type) => (param)
  content = content.replace(/\(([a-zA-Z_$][\w]*)\s*:\s*[\w.<>[\]|&\s]+\)/g, '($1)');

  // Remove type annotations from const declarations
  // const something: Type = ... => const something = ...
  content = content.replace(/const\s+(\w+)\s*:\s*[\w.<>[\]|&\s]+\s*=/g, 'const $1 =');

  // Fix broken forwardRef declarations that might have leftover commas
  content = content.replace(/const\s+(\w+)\s*=\s*React\.forwardRef,/g, 'const $1 = React.forwardRef');

  return content;
}

function processFile(filePath) {
  try {
    const originalContent = fs.readFileSync(filePath, 'utf8');
    let content = originalContent;

    // Apply fixes
    content = fixUIComponent(content);

    // Only write if changed
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

console.log('Fixing UI components...');
const fixed = walkDir('/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src');
console.log(`\nFixed ${fixed} files`);
