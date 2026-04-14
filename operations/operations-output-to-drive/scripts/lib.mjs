import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import { execFile as execFileCb } from 'node:child_process';
import { promisify } from 'node:util';

const execFile = promisify(execFileCb);

export const MANIFEST_SCHEMA_VERSION = 1;
export const MANIFEST_FILE = 'artifact-manifest.json';
export const UPLOAD_STATE_FILE = '.drive-upload-state.json';
export const SHARED_DRIVE_ID = process.env.PAPERCLIP_SHARED_DRIVE_ID || '0AFJ_DrnFD4bbUk9PVA';
export const SHARED_RESOURCES_FOLDER_ID =
  process.env.PAPERCLIP_SHARED_RESOURCES_FOLDER_ID || '1NT15AiujwHllLu0dlr2Exy_BGD88kErJ';
export const OUTPUTS_DIR = path.resolve(process.env.OUTPUTS_DIR || 'outputs');
export const RETENTION_DAYS = Number(process.env.OUTPUT_RETENTION_DAYS || 7);
export const OUTPUT_GWS_CONFIG_DIR =
  process.env.OUTPUT_GWS_CONFIG_DIR || process.env.GWS_USER_ADMIN || null;

// Matches any Paperclip issue identifier, e.g. FIGA-142, PAP-12, ZED-7
const ISSUE_DIR_PATTERN = /^[A-Z]+-\d+$/i;

const FOLDER_MIME = 'application/vnd.google-apps.folder';

function safeJsonParse(value, fallback = null) {
  try {
    return JSON.parse(value);
  } catch {
    return fallback;
  }
}

function toIsoStamp(date = new Date()) {
  return date.toISOString().replace(/[-:.]/g, '').slice(0, 15) + 'Z';
}

async function runGws(args, { dryRun = false } = {}) {
  if (dryRun) {
    return { dryRun: true, args };
  }

  const gwsEnv = { ...process.env };
  delete gwsEnv.GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE;
  if (OUTPUT_GWS_CONFIG_DIR) {
    gwsEnv.GOOGLE_WORKSPACE_CLI_CONFIG_DIR = OUTPUT_GWS_CONFIG_DIR;
  }

  const { stdout, stderr } = await execFile('gws', [...args, '--format', 'json'], {
    env: gwsEnv,
    maxBuffer: 32 * 1024 * 1024
  });
  if (stderr && stderr.trim()) {
    process.stderr.write(stderr);
  }
  return safeJsonParse(stdout, {});
}

async function walkFiles(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    if (entry.name === '.trash') {
      continue;
    }
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...(await walkFiles(fullPath)));
    } else if (entry.isFile()) {
      files.push(fullPath);
    }
  }

  return files;
}

async function sha256File(filePath) {
  const hash = crypto.createHash('sha256');
  const bytes = await fs.readFile(filePath);
  hash.update(bytes);
  return hash.digest('hex');
}

function guessMimeType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === '.png') return 'image/png';
  if (ext === '.jpg' || ext === '.jpeg') return 'image/jpeg';
  if (ext === '.svg') return 'image/svg+xml';
  if (ext === '.json') return 'application/json';
  if (ext === '.md') return 'text/markdown';
  if (ext === '.mjs') return 'text/javascript';
  return 'application/octet-stream';
}

export function issueOutputDir(issueId) {
  return path.join(OUTPUTS_DIR, issueId);
}

export function buildDrivePathParts(projectName, issueId) {
  return ['09 - Shared Resources', 'Cross-Team Projects', projectName, 'Outputs', issueId];
}

export async function createManifest({
  issueId,
  runId = process.env.PAPERCLIP_RUN_ID || null,
  projectName = process.env.OUTPUT_PROJECT_NAME || ''
}) {
  if (!projectName) {
    throw new Error('OUTPUT_PROJECT_NAME env var is required');
  }
  const outputDir = issueOutputDir(issueId);
  const allFiles = await walkFiles(outputDir);
  const fileRecords = [];

  for (const fullPath of allFiles) {
    const base = path.basename(fullPath);
    if (base === MANIFEST_FILE || base === UPLOAD_STATE_FILE) {
      continue;
    }
    const relativePath = path.relative(outputDir, fullPath);
    const stat = await fs.stat(fullPath);
    fileRecords.push({
      relativePath,
      sizeBytes: stat.size,
      sha256: await sha256File(fullPath),
      mimeType: guessMimeType(fullPath),
      modifiedAt: stat.mtime.toISOString()
    });
  }

  fileRecords.sort((a, b) => a.relativePath.localeCompare(b.relativePath));
  const drivePathParts = buildDrivePathParts(projectName, issueId);
  const manifest = {
    schemaVersion: MANIFEST_SCHEMA_VERSION,
    generatedAt: new Date().toISOString(),
    issueId,
    runId,
    projectName,
    localOutputDir: outputDir,
    drive: {
      sharedDriveId: SHARED_DRIVE_ID,
      folderPath: drivePathParts,
      supportsAllDrives: true
    },
    fileCount: fileRecords.length,
    files: fileRecords
  };

  const manifestPath = path.join(outputDir, MANIFEST_FILE);
  await fs.writeFile(manifestPath, JSON.stringify(manifest, null, 2) + '\n', 'utf8');
  return { manifestPath, manifest };
}

async function findFolderByName({ parentId, name, dryRun }) {
  const query = [
    `mimeType='${FOLDER_MIME}'`,
    `name='${name.replace(/'/g, "\\'")}'`,
    `'${parentId}' in parents`,
    'trashed=false'
  ].join(' and ');

  const params = {
    q: query,
    supportsAllDrives: true,
    includeItemsFromAllDrives: true,
    corpora: 'drive',
    driveId: SHARED_DRIVE_ID,
    fields: 'files(id,name,webViewLink)',
    pageSize: 10
  };
  const res = await runGws(['drive', 'files', 'list', '--params', JSON.stringify(params)], { dryRun });
  const files = Array.isArray(res?.files) ? res.files : [];
  return files[0] || null;
}

async function createFolder({ parentId, name, dryRun }) {
  const json = { name, mimeType: FOLDER_MIME, parents: [parentId] };
  const params = { supportsAllDrives: true, fields: 'id,name,webViewLink' };
  return runGws(['drive', 'files', 'create', '--json', JSON.stringify(json), '--params', JSON.stringify(params)], {
    dryRun
  });
}

async function ensureFolder({ parentId, name, dryRun }) {
  const existing = await findFolderByName({ parentId, name, dryRun });
  if (existing?.id) {
    return existing;
  }
  return createFolder({ parentId, name, dryRun });
}

async function ensureDrivePath({ projectName, issueId, dryRun }) {
  const dynamicParts = ['Cross-Team Projects', projectName, 'Outputs', issueId];
  let parentId = SHARED_RESOURCES_FOLDER_ID;

  for (const part of dynamicParts) {
    const folder = await ensureFolder({ parentId, name: part, dryRun });
    parentId = folder.id || `dry-run-${part}`;
  }

  return { rootFolderId: parentId };
}

async function ensureChildFolderTree({ issueRootFolderId, subdirs, dryRun }) {
  const created = new Map();
  created.set('', issueRootFolderId);

  for (const subdir of subdirs) {
    const segments = subdir.split('/').filter(Boolean);
    let currentPath = '';
    let parentId = issueRootFolderId;

    for (const segment of segments) {
      currentPath = currentPath ? `${currentPath}/${segment}` : segment;
      if (created.has(currentPath)) {
        parentId = created.get(currentPath);
        continue;
      }

      const folder = await ensureFolder({ parentId, name: segment, dryRun });
      const id = folder.id || `dry-run-${currentPath}`;
      created.set(currentPath, id);
      parentId = id;
    }
  }

  return created;
}

async function readJsonFile(filePath, fallback) {
  try {
    const raw = await fs.readFile(filePath, 'utf8');
    return safeJsonParse(raw, fallback);
  } catch {
    return fallback;
  }
}

async function listMatchingFiles({ parentId, name, dryRun }) {
  const query = [`name='${name.replace(/'/g, "\\'")}'`, `'${parentId}' in parents`, 'trashed=false'].join(' and ');
  const params = {
    q: query,
    supportsAllDrives: true,
    includeItemsFromAllDrives: true,
    corpora: 'drive',
    driveId: SHARED_DRIVE_ID,
    fields: 'files(id,name,md5Checksum,size,webViewLink)',
    pageSize: 10
  };
  const res = await runGws(['drive', 'files', 'list', '--params', JSON.stringify(params)], { dryRun });
  return Array.isArray(res?.files) ? res.files : [];
}

async function uploadSingleFile({ localPath, parentId, name, mimeType, dryRun }) {
  const json = { name, parents: [parentId], mimeType };
  const params = { supportsAllDrives: true, fields: 'id,name,webViewLink,md5Checksum,size' };
  return runGws(
    ['drive', 'files', 'create', '--upload', localPath, '--json', JSON.stringify(json), '--params', JSON.stringify(params)],
    { dryRun }
  );
}

export async function uploadIssue({ issueId, projectName = process.env.OUTPUT_PROJECT_NAME || '', dryRun = false }) {
  if (!projectName) {
    throw new Error('OUTPUT_PROJECT_NAME env var is required');
  }
  const outputDir = issueOutputDir(issueId);
  const manifestPath = path.join(outputDir, MANIFEST_FILE);
  const statePath = path.join(outputDir, UPLOAD_STATE_FILE);
  let manifest = await readJsonFile(manifestPath, null);

  if (!manifest) {
    const created = await createManifest({ issueId, projectName });
    manifest = created.manifest;
  }

  const drivePath = await ensureDrivePath({ projectName, issueId, dryRun });
  const subdirs = Array.from(
    new Set(
      manifest.files
        .map((file) => path.posix.dirname(file.relativePath))
        .filter((dir) => dir && dir !== '.')
    )
  );
  const folderMap = await ensureChildFolderTree({
    issueRootFolderId: drivePath.rootFolderId,
    subdirs,
    dryRun
  });

  const currentState = (await readJsonFile(statePath, null)) || {
    schemaVersion: 1,
    issueId,
    files: []
  };
  const byRelativePath = new Map(currentState.files.map((f) => [f.relativePath, f]));
  const uploadedFiles = [];

  for (const file of manifest.files) {
    const dir = path.posix.dirname(file.relativePath);
    const folderId = folderMap.get(dir === '.' ? '' : dir) || drivePath.rootFolderId;
    const localPath = path.join(outputDir, file.relativePath);
    const prior = byRelativePath.get(file.relativePath);

    if (prior?.sha256 === file.sha256 && prior?.driveFileId) {
      uploadedFiles.push({ ...prior, status: 'already-recorded' });
      continue;
    }

    const existing = await listMatchingFiles({
      parentId: folderId,
      name: path.basename(file.relativePath),
      dryRun
    });
    if (existing[0]?.id) {
      uploadedFiles.push({
        relativePath: file.relativePath,
        sha256: file.sha256,
        driveFileId: existing[0].id,
        webViewLink: existing[0].webViewLink || null,
        status: 'already-in-drive'
      });
      continue;
    }

    const uploaded = await uploadSingleFile({
      localPath,
      parentId: folderId,
      name: path.basename(file.relativePath),
      mimeType: file.mimeType,
      dryRun
    });

    uploadedFiles.push({
      relativePath: file.relativePath,
      sha256: file.sha256,
      driveFileId: uploaded.id || null,
      webViewLink: uploaded.webViewLink || null,
      status: dryRun ? 'dry-run' : 'uploaded'
    });
  }

  const manifestUpload = await uploadSingleFile({
    localPath: manifestPath,
    parentId: drivePath.rootFolderId,
    name: MANIFEST_FILE,
    mimeType: 'application/json',
    dryRun
  });

  const state = {
    schemaVersion: 1,
    issueId,
    projectName,
    sharedDriveId: SHARED_DRIVE_ID,
    issueRootFolderId: drivePath.rootFolderId,
    uploadedAt: new Date().toISOString(),
    retentionDays: RETENTION_DAYS,
    drivePath: buildDrivePathParts(projectName, issueId),
    manifest: {
      fileName: MANIFEST_FILE,
      driveFileId: manifestUpload.id || null,
      webViewLink: manifestUpload.webViewLink || null
    },
    files: uploadedFiles,
    readyForLocalGc: !dryRun && uploadedFiles.length === manifest.files.length
  };

  if (!dryRun) {
    await fs.writeFile(statePath, JSON.stringify(state, null, 2) + '\n', 'utf8');
  }
  return state;
}

export async function listIssueDirs() {
  const entries = await fs.readdir(OUTPUTS_DIR, { withFileTypes: true });
  return entries
    .filter((entry) => entry.isDirectory() && ISSUE_DIR_PATTERN.test(entry.name))
    .map((entry) => entry.name)
    .sort();
}

export async function reconcileIssues({ issueIds = null, projectName = process.env.OUTPUT_PROJECT_NAME || '', dryRun = false }) {
  if (!projectName) {
    throw new Error('OUTPUT_PROJECT_NAME env var is required');
  }
  const issues = issueIds && issueIds.length ? issueIds : await listIssueDirs();
  const results = [];

  for (const issueId of issues) {
    const statePath = path.join(issueOutputDir(issueId), UPLOAD_STATE_FILE);
    const state = await readJsonFile(statePath, null);
    if (state?.readyForLocalGc === true && !dryRun) {
      results.push({ issueId, status: 'already-synced' });
      continue;
    }
    const synced = await uploadIssue({ issueId, projectName, dryRun });
    results.push({ issueId, status: dryRun ? 'dry-run' : 'synced', files: synced.files.length });
  }

  return results;
}

export async function runGc({ now = new Date(), dryRun = false }) {
  const trashRoot = path.join(OUTPUTS_DIR, '.trash');
  await fs.mkdir(trashRoot, { recursive: true });
  const moved = [];
  const deleted = [];

  const issueIds = await listIssueDirs();
  for (const issueId of issueIds) {
    const statePath = path.join(issueOutputDir(issueId), UPLOAD_STATE_FILE);
    const state = await readJsonFile(statePath, null);
    if (!state?.readyForLocalGc) {
      continue;
    }

    const sourceDir = issueOutputDir(issueId);
    const targetDir = path.join(trashRoot, issueId, toIsoStamp(now));
    if (!dryRun) {
      await fs.mkdir(path.dirname(targetDir), { recursive: true });
      await fs.rename(sourceDir, targetDir);
    }
    moved.push({ issueId, from: sourceDir, to: targetDir });
  }

  const cutoff = now.getTime() - RETENTION_DAYS * 24 * 60 * 60 * 1000;
  const trashIssues = await fs.readdir(trashRoot, { withFileTypes: true });
  for (const issueEntry of trashIssues) {
    if (!issueEntry.isDirectory()) {
      continue;
    }
    const issueTrashDir = path.join(trashRoot, issueEntry.name);
    const snapshots = await fs.readdir(issueTrashDir, { withFileTypes: true });
    for (const snapshot of snapshots) {
      if (!snapshot.isDirectory()) {
        continue;
      }
      const snapshotPath = path.join(issueTrashDir, snapshot.name);
      const stat = await fs.stat(snapshotPath);
      if (stat.mtime.getTime() <= cutoff) {
        if (!dryRun) {
          await fs.rm(snapshotPath, { recursive: true, force: true });
        }
        deleted.push(snapshotPath);
      }
    }
  }

  return { moved, deleted, retentionDays: RETENTION_DAYS };
}
