#!/usr/bin/env npx tsx
/**
 * BR-ACC Upstream Monitor — TASK-013
 * Runs 2x/day; monitors forks, PRs, issues, TASKS.md vs merged PRs.
 * Output: bracc-monitor-report.json + optional Discord/Telegram notifications.
 */

import "dotenv/config";
import { Octokit } from "@octokit/rest";
import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..");

const UPSTREAM_OWNER = "World-Open-Graph";
const UPSTREAM_REPO = "br-acc";
const OUR_REPO_OWNER = "enioxt";
const OUR_REPO = "EGOS-Inteligencia";

const REPORT_PATH = process.env.REPORT_PATH ?? path.join(__dirname, "bracc-monitor-report.json");
const STATE_PATH = process.env.STATE_PATH ?? path.join(__dirname, ".bracc-monitor-state.json");

// ---------------------------------------------------------------------------
// Config and state
// ---------------------------------------------------------------------------

function getToken(): string {
  const token = process.env.GITHUB_TOKEN ?? process.env.GH_TOKEN;
  if (!token) {
    throw new Error("Set GITHUB_TOKEN or GH_TOKEN to run the monitor.");
  }
  return token;
}

interface MonitorState {
  lastRun: string; // ISO
  knownForkIds: number[];
  knownPRNumbers: number[];
}

function ensureDirFor(filePath: string): void {
  const dir = path.dirname(filePath);
  if (dir) fs.mkdirSync(dir, { recursive: true });
}

function loadState(): MonitorState {
  try {
    const raw = fs.readFileSync(STATE_PATH, "utf-8");
    return JSON.parse(raw) as MonitorState;
  } catch {
    return {
      lastRun: "",
      knownForkIds: [],
      knownPRNumbers: [],
    };
  }
}

function saveState(state: MonitorState): void {
  ensureDirFor(STATE_PATH);
  fs.writeFileSync(STATE_PATH, JSON.stringify(state, null, 2), "utf-8");
}

// ---------------------------------------------------------------------------
// Categorize by file paths (forks + PRs)
// ---------------------------------------------------------------------------

const CATEGORY_MAP: Array<{ pattern: RegExp | string; category: string }> = [
  { pattern: /^frontend\//, category: "frontend" },
  { pattern: /^api\//, category: "API" },
  { pattern: /^etl\//, category: "ETL" },
  { pattern: /^infra\//, category: "infra" },
  { pattern: /^docs\//, category: "docs" },
  { pattern: /\.md$/i, category: "docs" },
  { pattern: /(?:i18n|locales?|locale)\//i, category: "tradução" },
  { pattern: /\.(json|yaml|yml)$/, category: "docs" }, // config/docs-ish
];

function categorizeFilesSet(files: string[]): string[] {
  const categories = new Set<string>();
  for (const f of files) {
    let matched = false;
    for (const { pattern, category } of CATEGORY_MAP) {
      if (typeof pattern === "string" ? f.startsWith(pattern) : pattern.test(f)) {
        categories.add(category);
        matched = true;
        break;
      }
    }
    if (!matched) categories.add("other");
  }
  return [...categories].length ? [...categories] : ["other"];
}

// ---------------------------------------------------------------------------
// Forks
// ---------------------------------------------------------------------------

interface ForkEntry {
  id: number;
  full_name: string;
  html_url: string;
  created_at: string;
  new_since: boolean;
  files_changed: string[];
  categories: string[];
}

async function fetchForks(octokit: Octokit): Promise<ForkEntry[]> {
  const forks: ForkEntry[] = [];
  const state = loadState();
  const pageSize = 30;
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    const { data: list } = await octokit.repos.listForks({
      owner: UPSTREAM_OWNER,
      repo: UPSTREAM_REPO,
      sort: "newest",
      per_page: pageSize,
      page,
    });
    if (list.length === 0) hasMore = false;
    for (const fork of list) {
      const new_since = !state.knownForkIds.includes(fork.id);
      let files_changed: string[] = [];
      let categories: string[] = ["other"];

      try {
        const forkBranch = fork.default_branch ?? "main";
        const upstreamBase = "main"; // upstream default branch
        const { data: compare } = await octokit.repos.compareCommitsWithBasehead({
          owner: UPSTREAM_OWNER,
          repo: UPSTREAM_REPO,
          basehead: `${upstreamBase}...${fork.owner.login}:${forkBranch}`,
        });
        if (compare.files) {
          files_changed = compare.files.map((f) => f.filename).filter(Boolean);
          categories = categorizeFilesSet(files_changed);
        }
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        console.warn(`[bracc-monitor] compare forks ${UPSTREAM_OWNER}/${UPSTREAM_REPO} vs ${fork.full_name}: ${msg}`);
      }

      forks.push({
        id: fork.id,
        full_name: fork.full_name ?? `${fork.owner.login}/${fork.name}`,
        html_url: fork.html_url ?? `https://github.com/${fork.full_name}`,
        created_at: fork.created_at ?? "",
        new_since,
        files_changed,
        categories,
      });
    }
    page++;
    if (list.length < pageSize) hasMore = false;
  }

  return forks;
}

// ---------------------------------------------------------------------------
// Pull Requests (open, with duplicate detection and categories)
// ---------------------------------------------------------------------------

interface PREntry {
  number: number;
  title: string;
  html_url: string;
  user: string;
  labels: string[];
  files: string[];
  categories: string[];
  duplicate_of?: number[]; // other PR numbers touching same file set
  new_since: boolean;
}

async function fetchOpenPRs(octokit: Octokit): Promise<PREntry[]> {
  const state = loadState();
  const prs: PREntry[] = [];
  let page = 1;
  const pageSize = 30;

  while (true) {
    const { data: list } = await octokit.pulls.list({
      owner: UPSTREAM_OWNER,
      repo: UPSTREAM_REPO,
      state: "open",
      per_page: pageSize,
      page,
    });
    if (list.length === 0) break;

    for (const pr of list) {
      let files: string[] = [];
      try {
        const filesData = await octokit.paginate(octokit.pulls.listFiles, {
          owner: UPSTREAM_OWNER,
          repo: UPSTREAM_REPO,
          pull_number: pr.number,
        });
        files = filesData.map((f) => f.filename).filter(Boolean);
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        console.warn(`[bracc-monitor] pulls.listFiles ${UPSTREAM_OWNER}/${UPSTREAM_REPO} PR #${pr.number}: ${msg}`);
      }
      const categories = categorizeFilesSet(files);
      const labels = (pr.labels ?? []).map((l) => (typeof l === "object" && l.name ? l.name : String(l)));

      prs.push({
        number: pr.number,
        title: pr.title ?? "",
        html_url: pr.html_url ?? `https://github.com/${UPSTREAM_OWNER}/${UPSTREAM_REPO}/pull/${pr.number}`,
        user: pr.user?.login ?? "",
        labels,
        files,
        categories,
        new_since: !state.knownPRNumbers.includes(pr.number),
      });
    }
    if (list.length < pageSize) break;
    page++;
  }

  // Duplicate detection: group by sorted file set fingerprint; fallback unique per PR to avoid false positives when files are empty
  const byFingerprint = new Map<string, number[]>();
  const fingerprintKey = (pr: PREntry) =>
    pr.files.length ? pr.files.slice().sort().join("\n") : `title:${pr.title}:pr:${pr.number}`;
  for (const pr of prs) {
    const key = fingerprintKey(pr);
    const arr = byFingerprint.get(key) ?? [];
    arr.push(pr.number);
    byFingerprint.set(key, arr);
  }
  for (const pr of prs) {
    const key = fingerprintKey(pr);
    const group = byFingerprint.get(key) ?? [];
    if (group.length > 1) {
      pr.duplicate_of = group.filter((n) => n !== pr.number);
    }
  }

  return prs;
}

// ---------------------------------------------------------------------------
// Issues (upstream + cross-ref with our repo)
// ---------------------------------------------------------------------------

interface IssueEntry {
  number: number;
  title: string;
  html_url: string;
  state: string;
  possible_duplicate_of?: string; // our repo issue URL or number
}

async function fetchIssues(octokit: Octokit): Promise<{ upstream: IssueEntry[]; ours: IssueEntry[]; cross_ref: Array<{ upstream: IssueEntry; our: IssueEntry }> }> {
  const upstream: IssueEntry[] = [];
  let page = 1;
  const pageSize = 50;

  while (true) {
    const { data: list } = await octokit.issues.listForRepo({
      owner: UPSTREAM_OWNER,
      repo: UPSTREAM_REPO,
      state: "open",
      per_page: pageSize,
      page,
    });
    if (list.length === 0) break;
    const issues = list.filter((i) => !i.pull_request);
    if (issues.length === 0) {
      page++;
      continue;
    }
    for (const i of issues) {
      upstream.push({
        number: i.number,
        title: i.title ?? "",
        html_url: i.html_url ?? `https://github.com/${UPSTREAM_OWNER}/${UPSTREAM_REPO}/issues/${i.number}`,
        state: i.state ?? "open",
      });
    }
    if (list.length < pageSize) break;
    page++;
  }

  const ours: IssueEntry[] = [];
  page = 1;
  while (true) {
    try {
      const { data: list } = await octokit.issues.listForRepo({
        owner: OUR_REPO_OWNER,
        repo: OUR_REPO,
        state: "open",
        per_page: pageSize,
        page,
      });
      if (list.length === 0) break;
      const issues = list.filter((i) => !i.pull_request);
      if (issues.length === 0) {
        page++;
        continue;
      }
      for (const i of issues) {
        ours.push({
          number: i.number,
          title: i.title ?? "",
          html_url: i.html_url ?? `https://github.com/${OUR_REPO_OWNER}/${OUR_REPO}/issues/${i.number}`,
          state: i.state ?? "open",
        });
      }
      if (list.length < pageSize) break;
      page++;
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      console.warn(`[bracc-monitor] issues listForRepo ${OUR_REPO_OWNER}/${OUR_REPO} page ${page}: ${msg}`);
      break;
    }
  }

  // Simple keyword cross-ref: normalize title to words, match if significant overlap
  const cross_ref: Array<{ upstream: IssueEntry; our: IssueEntry }> = [];
  const toWords = (t: string) =>
    t
      .toLowerCase()
      .replace(/[^\w\s]/g, " ")
      .split(/\s+/)
      .filter((w) => w.length > 2);
  for (const u of upstream) {
    const uWords = new Set(toWords(u.title));
    for (const o of ours) {
      const oWords = toWords(o.title);
      const overlap = oWords.filter((w) => uWords.has(w)).length;
      if (overlap >= 2 && overlap >= Math.min(uWords.size, oWords.length) * 0.3) {
        cross_ref.push({ upstream: u, our: o });
        u.possible_duplicate_of = o.html_url;
        break; // only record first match per upstream issue
      }
    }
  }

  return { upstream, ours, cross_ref };
}

// ---------------------------------------------------------------------------
// Roadmap: TASKS.md vs merged PRs
// ---------------------------------------------------------------------------

interface TaskMatch {
  task_id: string;
  status: string;
  possible_pr: { number: number; title: string; html_url: string };
}

function parseTASKS(content: string): Array<{ id: string; status: string; title_snippet: string }> {
  const tasks: Array<{ id: string; status: string; title_snippet: string }> = [];
  const taskLine = /^### (TASK-\d+):\s*(.*?)(?:\s*✅|\s*⬜|\s*⏳|$)/im;
  const statusMatch = /(✅|⬜|⏳)/;
  const lines = content.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(taskLine);
    if (m) {
      const status = statusMatch.exec(lines[i])?.[1] ?? "⬜";
      tasks.push({
        id: m[1],
        status,
        title_snippet: (m[2] ?? "").replace(/\s*\(.*\)\s*$/, "").trim().slice(0, 80),
      });
    }
  }
  return tasks;
}

async function fetchRoadmapSuggestions(
  octokit: Octokit,
  state: MonitorState
): Promise<TaskMatch[]> {
  const tasksPath = path.join(REPO_ROOT, "TASKS.md");
  let tasksContent: string;
  try {
    tasksContent = fs.readFileSync(tasksPath, "utf-8");
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    console.warn(`[bracc-monitor] read TASKS.md ${tasksPath}: ${msg}`);
    return [];
  }
  const tasks = parseTASKS(tasksContent);
  const since = state.lastRun ? new Date(state.lastRun) : new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);

  const merged: Array<{ number: number; title: string; html_url: string; body: string }> = [];
  let page = 1;
  while (true) {
    const { data: list } = await octokit.pulls.list({
      owner: UPSTREAM_OWNER,
      repo: UPSTREAM_REPO,
      state: "closed",
      sort: "updated",
      direction: "desc",
      per_page: 30,
      page,
    });
    for (const pr of list) {
      if (!pr.merged_at) continue;
      const mergedAt = new Date(pr.merged_at);
      if (mergedAt < since) continue;
      merged.push({
        number: pr.number,
        title: pr.title ?? "",
        html_url: pr.html_url ?? `https://github.com/${UPSTREAM_OWNER}/${UPSTREAM_REPO}/pull/${pr.number}`,
        body: pr.body ?? "",
      });
    }
    if (list.length < 30) break;
    page++;
  }

  const suggestions: TaskMatch[] = [];
  const taskWords = (t: string) =>
    t
      .toLowerCase()
      .replace(/[^\w\s]/g, " ")
      .split(/\s+/)
      .filter((w) => w.length > 2);

  for (const task of tasks) {
    if (task.status === "✅") continue;
    const words = new Set(taskWords(task.title_snippet));
    for (const pr of merged) {
      const prText = `${pr.title} ${pr.body}`;
      const prWords = taskWords(prText);
      const overlap = prWords.filter((w) => words.has(w)).length;
      if (overlap >= 2 && overlap >= Math.min(words.size, prWords.length) * 0.2) {
        suggestions.push({
          task_id: task.id,
          status: task.status,
          possible_pr: { number: pr.number, title: pr.title, html_url: pr.html_url },
        });
        break; // one suggestion per task
      }
    }
  }
  return suggestions;
}

// ---------------------------------------------------------------------------
// Notifications
// ---------------------------------------------------------------------------

const WEBHOOK_TIMEOUT_MS = 10_000;

async function sendWebhookRequest(
  url: string,
  options: { method: string; body: string },
  callerName: string
): Promise<void> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), WEBHOOK_TIMEOUT_MS);
  try {
    const response = await fetch(url, {
      method: options.method,
      headers: { "Content-Type": "application/json" },
      body: options.body,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    if (!response.ok) {
      console.warn(`[${callerName}] webhook request failed: status=${response.status}`);
      return;
    }
  } catch (e) {
    clearTimeout(timeoutId);
    const message = e instanceof Error ? e.message : "unknown error";
    console.warn(`[${callerName}] webhook request error: ${message}`);
  }
}

async function notifyDiscord(text: string): Promise<void> {
  const url = process.env.DISCORD_WEBHOOK_URL;
  if (!url) return;
  await sendWebhookRequest(
    url,
    { method: "POST", body: JSON.stringify({ content: text }) },
    "notifyDiscord"
  );
}

async function notifyTelegram(text: string): Promise<void> {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;
  if (!token || !chatId) return;
  const telegramUrl = `https://api.telegram.org/bot${token}/sendMessage`;
  await sendWebhookRequest(
    telegramUrl,
    {
      method: "POST",
      body: JSON.stringify({ chat_id: chatId, text, disable_web_page_preview: true }),
    },
    "notifyTelegram"
  );
}

async function sendRelevantNotifications(report: Report): Promise<void> {
  const parts: string[] = [];
  const newForks = report.forks.filter((f) => f.new_since);
  const newPRs = report.pull_requests.filter((p) => p.new_since);
  if (newForks.length) {
    parts.push(`🆕 Forks novos: ${newForks.length}\n${newForks.slice(0, 5).map((f) => `• ${f.full_name}`).join("\n")}`);
  }
  if (newPRs.length) {
    parts.push(
      `📌 PRs novos no upstream: ${newPRs.length}\n${newPRs.slice(0, 5).map((p) => `• #${p.number} ${p.title}\n  ${p.html_url}`).join("\n\n")}`
    );
  }
  if (report.roadmap_suggestions.length) {
    parts.push(
      `📋 Sugestões TASKS ↔ PRs: ${report.roadmap_suggestions.length}\n${report.roadmap_suggestions
        .slice(0, 3)
        .map((s) => `• ${s.task_id} ↔ PR #${s.possible_pr.number}`)
        .join("\n")}`
    );
  }
  if (parts.length === 0) return;
  const text = `[BR-ACC Monitor]\n\n${parts.join("\n\n")}`;
  await Promise.all([notifyDiscord(text), notifyTelegram(text)]);
}

// ---------------------------------------------------------------------------
// Report type and main
// ---------------------------------------------------------------------------

interface Report {
  generated_at: string;
  upstream: string;
  forks: ForkEntry[];
  pull_requests: PREntry[];
  issues: { upstream: IssueEntry[]; ours: IssueEntry[]; cross_ref_count: number };
  roadmap_suggestions: TaskMatch[];
}

async function main(): Promise<void> {
  const token = getToken();
  const octokit = new Octokit({ auth: token });

  const state = loadState();
  const now = new Date().toISOString();

  console.log("Fetching forks...");
  const forks = await fetchForks(octokit);
  console.log("Fetching open PRs...");
  const pull_requests = await fetchOpenPRs(octokit);
  console.log("Fetching issues...");
  const issuesData = await fetchIssues(octokit);
  console.log("Fetching roadmap suggestions...");
  const roadmap_suggestions = await fetchRoadmapSuggestions(octokit, state);

  const report: Report = {
    generated_at: now,
    upstream: `${UPSTREAM_OWNER}/${UPSTREAM_REPO}`,
    forks,
    pull_requests,
    issues: {
      upstream: issuesData.upstream,
      ours: issuesData.ours,
      cross_ref_count: issuesData.cross_ref.length,
    },
    roadmap_suggestions,
  };

  ensureDirFor(REPORT_PATH);
  fs.writeFileSync(REPORT_PATH, JSON.stringify(report, null, 2), "utf-8");
  console.log("Report written to", REPORT_PATH);

  // Update state for next run: keep only current forks/PRs to avoid unbounded growth; new_since still works for reappearing items
  const isFirstRun = !state.lastRun;
  saveState({
    lastRun: now,
    knownForkIds: [...new Set(forks.map((f) => f.id))],
    knownPRNumbers: [...new Set(pull_requests.map((p) => p.number))],
  });

  if (!isFirstRun) {
    await sendRelevantNotifications(report);
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
