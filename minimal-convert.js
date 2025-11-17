const fs = require('fs');
const path = require('path');

function minimalConvert(content) {
  // 1. Remove import type statements
  content = content.replace(/import\s+type\s+\{[^}]+\}\s+from\s+['"'][^'"']+['"'];?\n?/g, '');

  // 2. Remove interface and type declarations (simple, non-nested only)
  content = content.replace(/^export\s+interface\s+\w+\s*\{[^}]+\}\s*$/gm, '');
  content = content.replace(/^interface\s+\w+\s*\{[^}]+\}\s*$/gm, '');
  content = content.replace(/^export\s+type\s+\w+\s*=\s*[^;\n]+;?\s*$/gm, '');
  content = content.replace(/^type\s+\w+\s*=\s*[^;\n]+;?\s*$/gm, '');

  // 3. Remove generic types from common hooks (one line only)
  content = content.replace(/useState<[^>\n]+>/g, 'useState');
  content = content.replace(/useRef<[^>\n]+>/g, 'useRef');
  content = content.replace(/useQuery<[^>\n]+>/g, 'useQuery');
  content = content.replace(/useMutation<[^>\n]+>/g, 'useMutation');
  content = content.replace(/useMemo<[^>\n]+>/g, 'useMemo');
  content = content.replace(/useCallback<[^>\n]+>/g, 'useCallback');

  // 4. Remove React.FC and FC type annotations
  content = content.replace(/:\s*React\.FC<[^>]*>/g, '');
  content = content.replace(/:\s*FC<[^>]*>/g, '');

  // 5. Fix import paths  content = content.replace(/@\/components\//g, './components/');
  content = content.replace(/@\/lib\//g, './lib/');
  content = content.replace(/@\/hooks\//g, './hooks/');
  content = content.replace(/@\/pages\//g, './pages/');
  content = content.replace(/@\/assets\//g, './assets/');
  content = content.replace(/@assets\//g, './assets/');

  // 6. Remove @shared imports (TypeScript types only)
  content = content.replace(/import\s+\{[^}]+\}\s+from\s+['"']@shared\/[^'"']+['"'];?\n/g, '');

  // 7. Remove .tsx and .ts extensions from imports
  content = content.replace(/from\s+['"']([^'"']+)\.tsx['"']/g, 'from "$1"');
  content = content.replace(/from\s+['"']([^'"']+)\.ts['"']/g, 'from "$1"');

  // That's it! Don't try to remove type annotations from parameters or other complex patterns
  // Leave React.forwardRef with generics alone - they'll be handled separately if needed

  return content;
}

function processDirectory(sourceDir, targetDir, filePattern) {
  if (!fs.existsSync(targetDir)) {
    fs.mkdirSync(targetDir, { recursive: true });
  }

  const items = fs.readdirSync(sourceDir);

  for (const item of items) {
    const sourcePath = path.join(sourceDir, item);
    const stat = fs.statSync(sourcePath);

    if (stat.isDirectory() && !item.startsWith('.') && item !== 'node_modules') {
      processDirectory(sourcePath, path.join(targetDir, item), filePattern);
    } else if (stat.isFile() && item.match(filePattern)) {
      const targetPath = path.join(targetDir, item.replace('.tsx', '.jsx').replace('.ts', '.js'));
      let content = fs.readFileSync(sourcePath, 'utf8');
      content = minimalConvert(content);
      fs.writeFileSync(targetPath, content, 'utf8');
      console.log(`✓ ${item.replace('.tsx', '.jsx').replace('.ts', '.js')}`);
    }
  }
}

console.log('Minimal TypeScript to JSX conversion...\n');
processDirectory(
  '/Users/aptaa/2025-projects/Codeteki-django-react/client/src',
  '/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src',
  /\.(tsx|ts)$/
);
console.log('\nDone! Now run fix-all-imports.js to fix relative paths.');
