import { reconcileIssues } from './lib.mjs';

const dryRun = process.argv.includes('--dry-run');
const issueIds = process.argv.slice(2).filter((arg) => /^[A-Z]+-\d+$/i.test(arg));
const projectName = process.env.OUTPUT_PROJECT_NAME || '';

const results = await reconcileIssues({ issueIds, projectName, dryRun });
console.log(
  JSON.stringify(
    {
      dryRun,
      projectName,
      scannedIssues: issueIds.length ? issueIds : 'all',
      results
    },
    null,
    2
  )
);
