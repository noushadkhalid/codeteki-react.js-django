const fs = require('fs');
const path = require('path');

function comprehensiveCleanup(content) {
  // Remove type-only imports
  content = content.replace(/import\s+type\s+\{[^}]+\}\s+from\s+["'][^"']+["'];?\n?/g, '');
  content = content.replace(/import\s+\{[^}]*type\s+[^}]+\}\s+from\s+["'][^"']+["'];?\n?/g, '');

  // Remove interface declarations (including export interface)
  content = content.replace(/export\s+interface\s+\w+[^{]*\{[^}]*\}(\s*\n)?/gs, '');
  content = content.replace(/interface\s+\w+[^{]*\{[^}]*\}(\s*\n)?/gs, '');

  // Remove type declarations (including export type)
  content = content.replace(/export\s+type\s+\w+\s*=\s*[^;\n]+;?(\s*\n)?/g, '');
  content = content.replace(/type\s+\w+\s*=\s*[^;\n]+;?(\s*\n)?/g, '');

  // Remove React.FC and FC type annotations
  content = content.replace(/:\s*React\.FC<[^>]*>/g, '');
  content = content.replace(/:\s*FC<[^>]*>/g, '');
  content = content.replace(/:\s*React\.FC\b/g, '');
  content = content.replace(/:\s*FC\b/g, '');

  // Remove generic types from hooks
  content = content.replace(/useState<[^>]+>/g, 'useState');
  content = content.replace(/useRef<[^>]+>/g, 'useRef');
  content = content.replace(/useQuery<[^>]+>/g, 'useQuery');
  content = content.replace(/useMutation<[^>]+>/g, 'useMutation');
  content = content.replace(/useContext<[^>]+>/g, 'useContext');
  content = content.replace(/useMemo<[^>]+>/g, 'useMemo');
  content = content.replace(/useCallback<[^>]+>/g, 'useCallback');

  // Remove React.forwardRef generic types
  content = content.replace(/React\.forwardRef<[^>]+,\s*[^>]+>/g, 'React.forwardRef');
  content = content.replace(/forwardRef<[^>]+,\s*[^>]+>/g, 'forwardRef');

  // Remove function return type annotations
  content = content.replace(/\)\s*:\s*(?:React\.)?(?:ReactElement|ReactNode|JSX\.Element)\s*(?=[{])/g, ') ');
  content = content.replace(/\)\s*:\s*void\s*(?=[{])/g, ') ');
  content = content.replace(/\)\s*:\s*\w+(?:\[\])?\s*(?=[{])/g, ') ');
  content = content.replace(/\)\s*:\s*\w+\s*=>/g, ') =>');

  // Remove type annotations from function parameters
  // Match (param: Type) -> (param)
  content = content.replace(/\(\s*(\w+)\s*:\s*[^),\n]+\s*\)/g, '($1)');
  // Match (param1: Type, param2: Type) -> (param1, param2)
  content = content.replace(/(\w+)\s*:\s*[^,)]+(?=,|\))/g, '$1');

  // Remove type annotations from arrow function parameters  content = content.replace(/=\s*\(\s*(\{[^}]+\})\s*:\s*[^)]+\s*\)/g, '= ($1)');

  // Remove extends clauses from type annotations
  content = content.replace(/extends\s+React\.\w+<[^>]+>/g, '');
  content = content.replace(/extends\s+\w+<[^>]+>/g, '');

  // Fix duplicate React imports (remove the duplicate)
  const lines = content.split('\n');
  const seenImports = new Set();
  const filteredLines = lines.filter(line => {
    if (line.match(/^import\s+.*from\s+["']react["']/)) {
      const normalized = line.trim();
      if (seenImports.has(normalized)) {
        return false;
      }
      seenImports.add(normalized);
    }
    return true;
  });
  content = filteredLines.join('\n');

  // Remove empty lines that result from deletions (max 2 consecutive empty lines)
  content = content.replace(/\n\n\n+/g, '\n\n');

  return content;
}

function processFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const cleaned = comprehensiveCleanup(content);

    if (content !== cleaned) {
      fs.writeFileSync(filePath, cleaned, 'utf8');
      const shortPath = filePath.replace('/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src/', '');
      console.log(`Cleaned: ${shortPath}`);
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

console.log('Running comprehensive TypeScript cleanup...');
const fixed = walkDir('/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src');
console.log(`\nCleaned ${fixed} files`);
