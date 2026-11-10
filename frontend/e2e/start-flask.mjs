import { execFileSync, spawn } from 'node:child_process';
import { existsSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const frontendDirectory = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(frontendDirectory, '..', '..');
const virtualEnvironmentPython = process.platform === 'win32'
  ? join(projectRoot, '.venv', 'Scripts', 'python.exe')
  : join(projectRoot, '.venv', 'bin', 'python');
const python = process.env.PYTHON_EXECUTABLE
  || process.env.PYTHON
  || (existsSync(virtualEnvironmentPython) ? virtualEnvironmentPython : 'python');
const scratchDirectory = mkdtempSync(join(tmpdir(), 'firststreet-e2e-'));
const databasePath = join(scratchDirectory, 'e2e.sqlite').replaceAll('\\', '/');
const env = {
  ...process.env,
  DEV_DATABASE_URL: `sqlite:///${databasePath}`,
  FLASK_ENV: 'development',
  LOG_TO_STDOUT: '1',
};

try {
  execFileSync(python, ['frontend/e2e/seed.py'], { cwd: projectRoot, env, stdio: 'inherit' });
} catch (error) {
  rmSync(scratchDirectory, { recursive: true, force: true });
  process.exit(error.status || 1);
}

const server = spawn(
  python,
  ['-m', 'flask', '--app', 'wsgi:application', 'run', '--host', '127.0.0.1', '--port', '5000', '--no-reload'],
  { cwd: projectRoot, env, stdio: 'inherit' },
);

const removeScratchDatabase = () => rmSync(scratchDirectory, { recursive: true, force: true });
process.on('SIGINT', () => server.kill('SIGINT'));
process.on('SIGTERM', () => server.kill('SIGTERM'));
server.on('error', (error) => {
  console.error(error);
  removeScratchDatabase();
  process.exitCode = 1;
});
server.on('exit', (code, signal) => {
  removeScratchDatabase();
  process.exitCode = code ?? (signal ? 1 : 0);
});
