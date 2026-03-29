#!/usr/bin/env bun
/**
 * Context Manager — Sistema Matemático de Persistência
 *
 * Estratégia Fibonacci de Backup:
 * - Ação 1: backup imediato
 * - Ação 2: backup imediato
 * - Ação 3: backup (1+2)
 * - Ação 5: backup (2+3)
 * - Ação 8: backup (3+5)
 * - etc...
 *
 * Triggers de Snapshot:
 * - Commit importante (feat, fix, refactor)
 * - Deploy (vercel, railway)
 * - Conclusão de task P0/P1
 * - Mudança de repo
 * - Intervalo Fibonacci
 */

import fs from 'fs/promises';
import path from 'path';
import { execSync } from 'child_process';

interface ContextSnapshot {
  timestamp: string;
  repo: string;
  branch: string;
  lastCommit: string;
  uncommittedFiles: number;
  currentTasks: {
    p0: string[];
    p1: string[];
    p2: string[];
  };
  recentCommits: string[];
  workingContext: string;
  llmConfig: {
    primary?: string;
    fallback?: string;
  };
  snapshot_trigger: 'commit' | 'deploy' | 'task_complete' | 'repo_change' | 'fibonacci' | 'manual';
  fibonacci_sequence_position?: number;
}

class ContextManager {
  private snapshotsDir: string;
  private stateFile: string;
  private fibSequence: number[] = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144];
  private actionCounter: number = 0;

  constructor(repoPath: string) {
    this.snapshotsDir = path.join(repoPath, 'docs/_context_snapshots');
    this.stateFile = path.join(this.snapshotsDir, '.state.json');
  }

  async init(): Promise<void> {
    await fs.mkdir(this.snapshotsDir, { recursive: true });
    await this.loadState();
  }

  private async loadState(): Promise<void> {
    try {
      const state = await fs.readFile(this.stateFile, 'utf-8');
      const data = JSON.parse(state);
      this.actionCounter = data.actionCounter || 0;
    } catch {
      this.actionCounter = 0;
    }
  }

  private async saveState(): Promise<void> {
    await fs.writeFile(
      this.stateFile,
      JSON.stringify({ actionCounter: this.actionCounter, lastUpdate: new Date().toISOString() }, null, 2)
    );
  }

  private shouldTakeFibonacciSnapshot(): boolean {
    return this.fibSequence.includes(this.actionCounter);
  }

  private async captureContext(): Promise<ContextSnapshot> {
    const cwd = process.cwd();

    // Git info
    const repo = path.basename(cwd);
    const branch = execSync('git branch --show-current', { encoding: 'utf-8' }).trim();
    const lastCommit = execSync('git log --oneline -1', { encoding: 'utf-8' }).trim();
    const uncommittedFiles = execSync('git status --short', { encoding: 'utf-8' }).split('\n').filter(Boolean).length;
    const recentCommits = execSync('git log --oneline -10', { encoding: 'utf-8' })
      .split('\n')
      .filter(Boolean);

    // Tasks parsing (simplified)
    let currentTasks = { p0: [] as string[], p1: [] as string[], p2: [] as string[] };
    try {
      const tasksContent = await fs.readFile(path.join(cwd, 'TASKS.md'), 'utf-8');

      // Extract P0 tasks
      const p0Match = tasksContent.match(/## P0[^\n]*\n([\s\S]*?)(?=\n## P[12]|\n---|\n##|\Z)/);
      if (p0Match) {
        currentTasks.p0 = p0Match[1]
          .split('\n')
          .filter(line => line.includes('###') && !line.includes('✅'))
          .map(line => line.replace(/###\s*/, '').trim())
          .slice(0, 5);
      }

      // Extract P1 tasks
      const p1Match = tasksContent.match(/## P1[^\n]*\n([\s\S]*?)(?=\n## P2|\n---|\n##|\Z)/);
      if (p1Match) {
        currentTasks.p1 = p1Match[1]
          .split('\n')
          .filter(line => line.includes('###') && !line.includes('✅'))
          .map(line => line.replace(/###\s*/, '').trim())
          .slice(0, 3);
      }
    } catch (e) {
      // TASKS.md não encontrado
    }

    // LLM config
    const llmConfig: { primary?: string; fallback?: string } = {};
    try {
      const envContent = await fs.readFile(path.join(cwd, '.env'), 'utf-8');
      if (envContent.includes('ALIBABA_DASHSCOPE_API_KEY')) llmConfig.primary = 'Alibaba Qwen';
      if (envContent.includes('OPENROUTER_API_KEY')) llmConfig.fallback = 'OpenRouter';
    } catch (e) {
      // .env não encontrado
    }

    const workingContext = `Working on: ${repo}/${branch}\nLast: ${lastCommit}\nUncommitted: ${uncommittedFiles} files`;

    return {
      timestamp: new Date().toISOString(),
      repo,
      branch,
      lastCommit,
      uncommittedFiles,
      currentTasks,
      recentCommits,
      workingContext,
      llmConfig,
      snapshot_trigger: 'fibonacci',
      fibonacci_sequence_position: this.fibSequence.indexOf(this.actionCounter),
    };
  }

  async createSnapshot(trigger: ContextSnapshot['snapshot_trigger'] = 'manual'): Promise<string> {
    const snapshot = await this.captureContext();
    snapshot.snapshot_trigger = trigger;

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `snapshot_${timestamp}_${trigger}.json`;
    const filepath = path.join(this.snapshotsDir, filename);

    await fs.writeFile(filepath, JSON.stringify(snapshot, null, 2));

    // Criar resumo markdown
    const mdContent = this.generateMarkdownSummary(snapshot);
    await fs.writeFile(filepath.replace('.json', '.md'), mdContent);

    console.log(`✅ Snapshot criado: ${filename}`);
    console.log(`📊 Fibonacci position: ${this.actionCounter} (${this.shouldTakeFibonacciSnapshot() ? 'SNAPSHOT' : 'skip'})`);

    return filepath;
  }

  private generateMarkdownSummary(snapshot: ContextSnapshot): string {
    return `# Context Snapshot — ${snapshot.timestamp}

**Repo:** ${snapshot.repo} | **Branch:** ${snapshot.branch}
**Trigger:** ${snapshot.snapshot_trigger} | **Fibonacci:** ${snapshot.fibonacci_sequence_position ?? 'N/A'}
**Last Commit:** ${snapshot.lastCommit}
**Uncommitted Files:** ${snapshot.uncommittedFiles}

---

## Current Tasks

### P0 Blockers
${snapshot.currentTasks.p0.map(t => `- ${t}`).join('\n') || '- (nenhum)'}

### P1 Sprint
${snapshot.currentTasks.p1.map(t => `- ${t}`).join('\n') || '- (nenhum)'}

### P2 Backlog
${snapshot.currentTasks.p2.map(t => `- ${t}`).join('\n') || '- (nenhum)'}

---

## Recent Commits (Last 10)
${snapshot.recentCommits.map(c => `- ${c}`).join('\n')}

---

## LLM Config
- **Primary:** ${snapshot.llmConfig.primary || 'Not configured'}
- **Fallback:** ${snapshot.llmConfig.fallback || 'Not configured'}

---

## Working Context
\`\`\`
${snapshot.workingContext}
\`\`\`

---

*Generated by context-manager.ts — EGOS v5.5*
`;
  }

  async incrementAction(): Promise<void> {
    this.actionCounter++;
    await this.saveState();

    if (this.shouldTakeFibonacciSnapshot()) {
      await this.createSnapshot('fibonacci');
    }
  }

  async getLatestSnapshot(): Promise<ContextSnapshot | null> {
    try {
      const files = await fs.readdir(this.snapshotsDir);
      const jsonFiles = files.filter(f => f.endsWith('.json') && !f.startsWith('.'));

      if (jsonFiles.length === 0) return null;

      jsonFiles.sort().reverse();
      const latestFile = jsonFiles[0];
      const content = await fs.readFile(path.join(this.snapshotsDir, latestFile), 'utf-8');

      return JSON.parse(content);
    } catch {
      return null;
    }
  }

  async listSnapshots(limit: number = 10): Promise<string[]> {
    try {
      const files = await fs.readdir(this.snapshotsDir);
      const jsonFiles = files.filter(f => f.endsWith('.json') && !f.startsWith('.'));

      jsonFiles.sort().reverse();
      return jsonFiles.slice(0, limit);
    } catch {
      return [];
    }
  }

  async cleanup(keepLast: number = 50): Promise<void> {
    const files = await this.listSnapshots(1000);
    if (files.length <= keepLast) return;

    const toDelete = files.slice(keepLast);
    for (const file of toDelete) {
      await fs.unlink(path.join(this.snapshotsDir, file));
      await fs.unlink(path.join(this.snapshotsDir, file.replace('.json', '.md'))).catch(() => {});
    }

    console.log(`🗑️  Removed ${toDelete.length} old snapshots (keeping ${keepLast})`);
  }
}

// CLI Interface
async function main() {
  const manager = new ContextManager(process.cwd());
  await manager.init();

  const command = process.argv[2];

  switch (command) {
    case 'snapshot':
    case 'save':
      const trigger = (process.argv[3] as ContextSnapshot['snapshot_trigger']) || 'manual';
      await manager.createSnapshot(trigger);
      break;

    case 'list':
      const snapshots = await manager.listSnapshots(20);
      console.log('📚 Recent snapshots:\n');
      snapshots.forEach(s => console.log(`  - ${s}`));
      break;

    case 'latest':
    case 'show':
      const latest = await manager.getLatestSnapshot();
      if (latest) {
        console.log('\n📸 Latest Snapshot:\n');
        console.log(JSON.stringify(latest, null, 2));
      } else {
        console.log('No snapshots found');
      }
      break;

    case 'increment':
      await manager.incrementAction();
      console.log(`Action counter: ${manager['actionCounter']}`);
      break;

    case 'cleanup':
      await manager.cleanup(50);
      break;

    case 'help':
    default:
      console.log(`
Context Manager — Sistema Matemático de Persistência

USAGE:
  tsx scripts/context-manager.ts <command> [args]

COMMANDS:
  snapshot [trigger]  Criar snapshot manual (triggers: commit, deploy, task_complete, manual)
  list                Listar snapshots recentes
  latest              Mostrar último snapshot
  increment           Incrementar contador Fibonacci (auto-snapshot se aplicável)
  cleanup             Limpar snapshots antigos (manter últimos 50)
  help                Mostrar esta ajuda

EXAMPLES:
  tsx scripts/context-manager.ts snapshot commit
  tsx scripts/context-manager.ts latest
  tsx scripts/context-manager.ts increment
      `);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}

export { ContextManager };
