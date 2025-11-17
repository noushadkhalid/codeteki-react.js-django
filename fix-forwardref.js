const fs = require('fs');
const path = require('path');

function fixForwardRef(content) {
  // Fix broken React.forwardRef patterns
  // Match: React.forwardRef\n  React.ComponentPropsWithoutRef<...>\n>(
  // Replace with: React.forwardRef(

  // First, collapse multi-line React.forward Ref declarations
  content = content.replace(/React\.forwardRef\s*\n\s*React\.ComponentPropsWithoutRef<[^>]+>\s*\n\s*>/g, 'React.forwardRef');
  content = content.replace(/React\.forwardRef\s*\n\s*React\.ElementRef<[^>]+>,\s*\n\s*React\.ComponentPropsWithoutRef<[^>]+>\s*\n\s*>/g, 'React.forwardRef');

  // Also handle single-line leftovers
  content = content.replace(/React\.forwardRef\s+React\.ComponentPropsWithoutRef<[^>]+>\s*>/g, 'React.forwardRef');

  // Remove any standalone type annotation lines after React.forwardRef
  const lines = content.split('\n');
  const fixed = [];
  let skipNext = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    // If previous line was React.forwardRef and this line is a type annotation, skip it
    if (skipNext && (
      trimmed.startsWith('React.ComponentPropsWithoutRef') ||
      trimmed.startsWith('React.ElementRef') ||
      trimmed.match(/^[\w.]+</)
    )) {
      skipNext = false;
      continue;
    }

    // Check if this line ends with React.forwardRef without opening paren
    if (line.match(/React\.forwardRef\s*$/) && !line.includes('(')) {
      // Next line(s) might be type annotations
      skipNext = true;
      fixed.push(line.replace(/React\.forwardRef\s*$/, 'React.forwardRef('));

      // Skip type annotation lines and find the actual parameter list
      let j = i + 1;
      while (j < lines.length) {
        const nextLine = lines[j].trim();
        if (nextLine.match(/^\(/) || nextLine.match(/^>\(/)) {
          // Found the parameter list
          if (nextLine.startsWith('>(')) {
            fixed[fixed.length - 1] = fixed[fixed.length - 1] + nextLine.substring(1);
          } else {
            fixed[fixed.length - 1] = fixed[fixed.length - 1] + nextLine;
          }
          i = j;
          skipNext = false;
          break;
        } else if (
          nextLine.startsWith('React.') ||
          nextLine.match(/^[\w.]+</) ||
          nextLine === '' ||
          nextLine.endsWith(',')
        ) {
          // Type annotation line, skip it
          j++;
        } else {
          break;
        }
      }
    } else {
      skipNext = false;
      fixed.push(line);
    }
  }

  return fixed.join('\n');
}

function processFile(filePath) {
  try {
    const originalContent = fs.readFileSync(filePath, 'utf8');
    const content = fixForwardRef(originalContent);

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

console.log('Fixing forwardRef declarations...');
const fixed = walkDir('/Users/aptaa/2025-projects/Codeteki-django-react/frontend/src');
console.log(`\nFixed ${fixed} files`);
