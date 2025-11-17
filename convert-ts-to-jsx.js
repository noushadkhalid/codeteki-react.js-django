const fs = require('fs');
const path = require('path');

// Convert TypeScript to JSX
function convertTsToJsx(content) {
  // Remove type annotations from function parameters
  content = content.replace(/\(\s*([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*[^)]+\)/g, '($1)');
  content = content.replace(/,\s*([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*[^,)]+/g, ', $1');

  // Remove type annotations from variable declarations
  content = content.replace(/:\s*(string|number|boolean|any|void|unknown|never)\s*=/g, ' =');
  content = content.replace(/:\s*(string|number|boolean|any|void|unknown|never)\s*;/g, ';');
  content = content.replace(/:\s*(string|number|boolean|any|void|unknown|never)\s*\)/g, ')');

  // Remove interface/type imports
  content = content.replace(/import\s+{\s*type\s+([^}]+)}\s+from/g, 'import {$1} from');
  content = content.replace(/,\s*type\s+/g, ', ');

  // Remove React.FC and other type annotations
  content = content.replace(/:\s*React\.FC<[^>]+>/g, '');
  content = content.replace(/:\s*FC<[^>]+>/g, '');

  // Remove generic type parameters
  content = content.replace(/<([A-Z][a-zA-Z0-9]*|[a-zA-Z0-9]+)\s*>/g, '');

  // Fix @ imports to relative
  content = content.replace(/@\/components\//g, '../');
  content = content.replace(/@\/lib\//g, '../../lib/');
  content = content.replace(/@\/hooks\//g, '../../hooks/');
  content = content.replace(/@\/pages\//g, '../../pages/');
  content = content.replace(/@assets\//g, '../../assets/');
  content = content.replace(/@\//g, '../../');

  return content;
}

// Process all files in client/src
function processDirectory(sourceDir, targetDir) {
  if (!fs.existsSync(targetDir)) {
    fs.mkdirSync(targetDir, { recursive: true });
  }

  const items = fs.readdirSync(sourceDir);

  items.forEach(item => {
    const sourcePath = path.join(sourceDir, item);
    const stats = fs.statSync(sourcePath);

    if (stats.isDirectory()) {
      // Skip node_modules and hidden folders
      if (item === 'node_modules' || item.startsWith('.')) return;

      const newTargetDir = path.join(targetDir, item);
      processDirectory(sourcePath, newTargetDir);
    } else if (stats.isFile()) {
      let targetPath = path.join(targetDir, item);

      // Convert .tsx to .jsx and .ts to .js
      if (item.endsWith('.tsx')) {
        targetPath = targetPath.replace(/\.tsx$/, '.jsx');
      } else if (item.endsWith('.ts') && !item.endsWith('.d.ts')) {
        targetPath = targetPath.replace(/\.ts$/, '.js');
      } else if (item.endsWith('.d.ts')) {
        // Skip TypeScript definition files
        return;
      }

      // Read and convert file content
      let content = fs.readFileSync(sourcePath, 'utf8');

      // Only convert .ts and .tsx files
      if (item.endsWith('.tsx') || item.endsWith('.ts')) {
        content = convertTsToJsx(content);
      }

      // Write to target
      fs.writeFileSync(targetPath, content, 'utf8');
      console.log(`Converted: ${sourcePath} -> ${targetPath}`);
    }
  });
}

// Main execution
const clientSrc = '/Users/aptaa/2025-projects/Codeteki-django-react/client/src';
const frontendSrc = '/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src';

console.log('Starting TypeScript to JSX conversion...');
processDirectory(clientSrc, frontendSrc);
console.log('Conversion complete!');
