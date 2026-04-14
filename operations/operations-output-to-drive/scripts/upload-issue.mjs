import { uploadIssue } from './lib.mjs';

const issueId = process.argv[2] || process.env.PAPERCLIP_TASK_IDENTIFIER || process.env.PAPERCLIP_TASK_ID;
if (!issueId) {
  throw new Error('Usage: node scripts/upload-issue.mjs <ISSUE-ID> [--dry-run]');
}

const dryRun = process.argv.includes('--dry-run');
const projectName = process.env.OUTPUT_PROJECT_NAME || '';
const state = await uploadIssue({ issueId, projectName, dryRun });

console.log(
  JSON.stringify(
    {
      issueId,
      projectName,
      dryRun,
      issueRootFolderId: state.issueRootFolderId,
      uploadedCount: state.files.length,
      readyForLocalGc: state.readyForLocalGc
    },
    null,
    2
  )
);
