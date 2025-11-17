const fs = require('fs');
const path = require('path');

function removeTypeScriptSyntax(content) {
  // Remove generic types in function calls like useQuery<Type>
  content = content.replace(/(\w+)<[^>]+>(\s*\()/g, '$1$2');

  // Remove type parameters from arrow functions
  content = content.replace(/\(\s*([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*[^)]+\)/g, '($1)');

  // Remove type annotations from destructured parameters
  content = content.replace(/const\s+{\s*([^}]+)\s*}(\s*:\s*[^=]+)?(\s*=)/g, 'const { $1 }$3');

  // Remove type annotations from variable declarations
  content = content.replace(/:\s*\w+(\[\])?(\s*[=;,)])/g, '$2');

  // Remove type imports that may have been missed
  content = content.replace(/import\s+type\s+{[^}]+}\s+from\s+["'][^"']+["'];?\n?/g, '');
  content = content.replace(/import\s+{\s*type\s+[^}]+}\s+from\s+["'][^"']+["'];?\n?/g, '');

  // Remove @shared imports (TypeScript monorepo patterns)
  content = content.replace(/import\s+{[^}]*}\s+from\s+["']@shared\/[^"']+["'];?\n?/g, '');

  // Remove React.FC and similar type annotations
  content = content.replace(/:\s*React\.FC<[^>]*>/g, '');
  content = content.replace(/:\s*FC<[^>]*>/g, '');

  // Remove Record, Partial, and other utility types
  content = content.replace(/:\s*Record<[^>]+>/g, '');
  content = content.replace(/:\s*Partial<[^>]+>/g, '');
  content = content.replace(/:\s*Pick<[^>]+>/g, '');
  content = content.replace(/:\s*Omit<[^>]+>/g, '');

  return content;
}

function processFile(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    const newContent = removeTypeScriptSyntax(content);

    if (content !== newContent) {
      fs.writeFileSync(filePath, newContent, 'utf8');
      console.log(`Fixed: ${filePath}`);
      return true;
    }
    return false;
  } catch (error) {
    console.error(`Error processing ${filePath}:`, error.message);
    return false;
  }
}

function processDirectory(dir) {
  const items = fs.readdirSync(dir);
  let fixedCount = 0;

  items.forEach(item => {
    const fullPath = path.join(dir, item);
    const stats = fs.statSync(fullPath);

    if (stats.isDirectory()) {
      if (item === 'node_modules' || item.startsWith('.')) return;
      fixedCount += processDirectory(fullPath);
    } else if (stats.isFile() && (item.endsWith('.jsx') || item.endsWith('.js'))) {
      if (processFile(fullPath)) fixedCount++;
    }
  });

  return fixedCount;
}

console.log('Removing remaining TypeScript syntax...');
const count = processDirectory('/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src');
console.log(`Fixed ${count} files!`);
