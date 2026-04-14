import { createManifest, uploadIssue } from './lib.mjs';

const issueId = process.argv[2] || process.env.PAPERCLIP_TASK_IDENTIFIER || process.env.PAPERCLIP_TASK_ID;
if (!issueId) {
  throw new Error('Usage: node scripts/post-task-hook.mjs <ISSUE-ID> [--dry-run]');
}

const dryRun = process.argv.includes('--dry-run');
const runId = process.env.PAPERCLIP_RUN_ID || null;
const projectName = process.env.OUTPUT_PROJECT_NAME || '';

const manifest = await createManifest({ issueId, runId, projectName });
const uploadState = await uploadIssue({ issueId, projectName, dryRun });

console.log(
  JSON.stringify(
    {
      issueId,
      runId,
      projectName,
      dryRun,
      manifestPath: manifest.manifestPath,
      fileCount: manifest.manifest.fileCount,
      issueRootFolderId: uploadState.issueRootFolderId,
      readyForLocalGc: uploadState.readyForLocalGc
    },
    null,
    2
  )
);
