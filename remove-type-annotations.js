const fs = require('fs');
const path = require('path');

function removeTypeAnnotations(content) {
  // Remove type annotations from function parameters - simple types only
  // Pattern: (param: Type) => (param)
  content = content.replace(/\(([a-zA-Z_$][\w]*)\s*:\s*(string|number|boolean|any|void)\)/g, '($1)');

  // Pattern: (param: Type, param2: Type) => (param, param2)
  content = content.replace(/([a-zA-Z_$][\w]*)\s*:\s*(string|number|boolean|any|void|Date|Element|HTMLElement|Promise<[^>]+>)\s*([,)])/g, '$1$3');

  // Remove return type annotations: ): Type => ): => ) =>
  content = content.replace(/\)\s*:\s*(string|number|boolean|any|void|Promise<[^>]+>|JSX\.Element|React\.ReactElement)\s*=>/g, ') =>');

  // Remove array type annotations: : Type[]
  content = content.replace(/([a-zA-Z_$][\w]*)\s*:\s*(string|number|boolean|any)\[\]\s*([,)])/g, '$1$3');

  // Remove object destructuring type annotations: ({ param }: { param: Type }) => ({ param })
  content = content.replace(/\(\s*\{([^}]+)\}\s*:\s*\{[^}]+\}\s*\)/g, '({ $1 })');

  // Remove const type annotations: const x: Type = => const x =
  content = content.replace(/const\s+([a-zA-Z_$][\w]*)\s*:\s*(string|number|boolean|any|Date)\s*=/g, 'const $1 =');

  // Remove let/var type annotations
  content = content.replace(/let\s+([a-zA-Z_$][\w]*)\s*:\s*(string|number|boolean|any|Date)\s*=/g, 'let $1 =');
  content = content.replace(/var\s+([a-zA-Z_$][\w]*)\s*:\s*(string|number|boolean|any|Date)\s*=/g, 'var $1 =');

  return content;
}

function processFile(filePath) {
  try {
    const originalContent = fs.readFileSync(filePath, 'utf8');
    const content = removeTypeAnnotations(originalContent);

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

console.log('Removing type annotations...');
const fixed = walkDir('/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src');
console.log(`\nFixed ${fixed} files`);
