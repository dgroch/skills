import { createManifest } from './lib.mjs';

const issueId = process.argv[2] || process.env.PAPERCLIP_TASK_IDENTIFIER || process.env.PAPERCLIP_TASK_ID;
if (!issueId) {
  throw new Error('Usage: node scripts/create-manifest.mjs <ISSUE-ID>');
}

const runId = process.env.PAPERCLIP_RUN_ID || null;
const projectName = process.env.OUTPUT_PROJECT_NAME || '';
const result = await createManifest({ issueId, runId, projectName });

console.log(
  JSON.stringify(
    {
      issueId,
      manifestPath: result.manifestPath,
      fileCount: result.manifest.fileCount,
      projectName
    },
    null,
    2
  )
);
