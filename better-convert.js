const fs = require('fs');
const path = require('path');

function convertFile(content) {
  // Remove type imports only
  content = content.replace(/import\s+type\s+\{[^}]+\}\s+from\s+["'][^"']+["'];?\n?/g, '');
  content = content.replace(/import\s+\{[^}]*type\s+[^}]+\}\s+from\s+["'][^"']+["'];?\n?/g, '');
  
  // Remove generic types in useQuery and other hooks
  content = content.replace(/useQuery<[^>]+>/g, 'useQuery');
  content = content.replace(/useMutation<[^>]+>/g, 'useMutation');
  content = content.replace(/useState<[^>]+>/g, 'useState');
  content = content.replace(/useRef<[^>]+>/g, 'useRef');
  
  // Remove function return type annotations
  content = content.replace(/\)\s*:\s*\w+(\[\])?\s*=>/g, ') =>');
  content = content.replace(/\)\s*:\s*JSX\.Element\s*{/g, ') {');
  content = content.replace(/\)\s*:\s*React\.ReactElement\s*{/g, ') {');
  
  // Remove React.FC and similar
  content = content.replace(/:\s*React\.FC<[^>]*>/g, '');
  content = content.replace(/:\s*FC<[^>]*>/g, '');
  
  // Remove simple type annotations from parameters (but keep the value)
  content = content.replace(/\(\s*(\w+)\s*:\s*\w+\s*\)/g, '($1)');
  content = content.replace(/,\s*(\w+)\s*:\s*\w+\s*\)/g, ', $1)');
  content = content.replace(/,\s*(\w+)\s*:\s*\w+\s*,/g, ', $1,');
  
  // Remove interface/type declarations
  content = content.replace(/interface\s+\w+\s*\{[^}]+\}/gs, '');
  content = content.replace(/type\s+\w+\s*=\s*\{[^}]+\}/gs, '');
  
  // Fix @ imports
  content = content.replace(/@\/components\//g, './components/');
  content = content.replace(/@\/lib\//g, './lib/');
  content = content.replace(/@\/hooks\//g, './hooks/');
  content = content.replace(/@\/pages\//g, './pages/');
  content = content.replace(/@assets\//g, './assets/');
  content = content.replace(/@shared\/\w+/g, '');
  
  // Remove .tsx/.ts extensions from imports
  content = content.replace(/from\s+["']([^"']+)\.tsx["']/g, 'from "$1"');
  content = content.replace(/from\s+["']([^"']+)\.ts["']/g, 'from "$1"');
  
  return content;
}

// Copy specific important files
const files = [
  'src/components/AITools.tsx',
  'src/components/BusinessImpact.tsx',
  'src/components/Services.tsx',
  'src/components/WhyChoose.tsx',
  'src/components/ROICalculator.tsx',
  'src/components/Contact.tsx',
  'src/components/FAQ.tsx',
];

files.forEach(file => {
  const source = path.join('/Users/aptaa/2025-projects/Codeteki-django-react/client', file);
  const target = path.join('/Users/aptaa/2025-projects/Codeteki-django-react/frontend', file.replace('.tsx', '.jsx'));
  
  if (fs.existsSync(source)) {
    let content = fs.readFileSync(source, 'utf8');
    content = convertFile(content);
    fs.writeFileSync(target, content, 'utf8');
    console.log(`Fixed: ${file}`);
  }
});

console.log('Done!');
