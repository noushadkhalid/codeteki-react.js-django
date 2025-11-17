const fs = require('fs');
const path = require('path');

function convertFile(content) {
  // Remove type-only imports
  content = content.replace(/import\s+type\s+\{[^}]+\}\s+from\s+['"'][^'"']+['"'];?\n?/g, '');

  // Remove interface/type declarations
  content = content.replace(/export\s+interface\s+\w+\s*\{[^}]+\}/gs, '');
  content = content.replace(/interface\s+\w+\s*\{[^}]+\}/gs, '');
  content = content.replace(/export\s+type\s+\w+\s*=\s*[^;\n]+;?\n?/g, '');
  content = content.replace(/type\s+\w+\s*=\s*[^;\n]+;?\n?/g, '');

  // Remove generic types from hooks and React methods
  content = content.replace(/useQuery<[^>]+>/g, 'useQuery');
  content = content.replace(/useMutation<[^>]+>/g, 'useMutation');
  content = content.replace(/useState<[^>]+>/g, 'useState');
  content = content.replace(/useRef<[^>]+>/g, 'useRef');
  content = content.replace(/useMemo<[^>]+>/g, 'useMemo');
  content = content.replace(/useCallback<[^>]+>/g, 'useCallback');
  content = content.replace(/React\.forwardRef<[^>]+>/g, 'React.forwardRef');

  // Remove function return type annotations (simple cases only)
  content = content.replace(/\)\s*:\s*JSX\.Element\s*{/g, ') {');
  content = content.replace(/\)\s*:\s*React\.ReactElement\s*{/g, ') {');
  content = content.replace(/\)\s*:\s*void\s*{/g, ') {');

  // Remove React.FC and similar
  content = content.replace(/:\s*React\.FC<[^>]*>/g, '');
  content = content.replace(/:\s*FC<[^>]*>/g, '');

  // Remove type annotations from arrow function parameters (careful approach)
  // Only match clear patterns like: (param: Type)
  content = content.replace(/\((\w+):\s*\w+\)/g, '($1)');
  // For multiple params: (a: Type, b: Type) - do it carefully
  content = content.replace(/\(([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*[^,)]+,\s*([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*[^)]+\)/g, '($1, $2)');
  // Three params
  content = content.replace(/\(([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*[^,)]+,\s*([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*[^,)]+,\s*([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*[^)]+\)/g, '($1, $2, $3)');

  // Fix @ imports to relative paths
  content = content.replace(/@\/components\//g, './components/');
  content = content.replace(/@\/lib\//g, './lib/');
  content = content.replace(/@\/hooks\//g, './hooks/');
  content = content.replace(/@\/pages\//g, './pages/');
  content = content.replace(/@\/assets\//g, './assets/');

  // Remove @shared imports completely (these are TypeScript types)
  content = content.replace(/import\s+\{[^}]+\}\s+from\s+['"']@shared\/[^'"']+['"'];?\n/g, '');

  // Remove .tsx/.ts extensions from imports
  content = content.replace(/from\s+['"']([^'"']+)\.tsx['"']/g, 'from "$1"');
  content = content.replace(/from\s+['"']([^'"']+)\.ts['"']/g, 'from "$1"');

  return content;
}

// Process all files in a directory
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
      content = convertFile(content);
      fs.writeFileSync(targetPath, content, 'utf8');
      console.log(`Converted: ${sourcePath.replace('/Users/aptaa/2025-projects/Codeteki-django-react/client/src/', '')} -> ${targetPath.replace('/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src/', '')}`);
    }
  }
}

console.log('Converting all TypeScript files to JSX...');
processDirectory(
  '/Users/aptaa/2025-projects/Codeteki-django-react/client/src',
  '/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src',
  /\.(tsx|ts)$/
);
console.log('\nDone!');
