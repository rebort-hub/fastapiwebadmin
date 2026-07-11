import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const target = path.join(root, 'node_modules/vite-plugin-monaco-editor/dist/workerMiddleware.js');

if (!fs.existsSync(target)) {
  process.exit(0);
}

const content = fs.readFileSync(target, 'utf8');
const from = 'fs.rmdirSync(exports.cacheDir, { recursive: true, force: true });';
const to = 'fs.rmSync(exports.cacheDir, { recursive: true, force: true });';

if (content.includes(from)) {
  fs.writeFileSync(target, content.replace(from, to), 'utf8');
  console.log('[patch-monaco-editor] replaced deprecated fs.rmdirSync with fs.rmSync');
}
