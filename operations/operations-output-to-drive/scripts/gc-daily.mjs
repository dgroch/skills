import { runGc } from './lib.mjs';

const dryRun = process.argv.includes('--dry-run');
const result = await runGc({ dryRun });

console.log(
  JSON.stringify(
    {
      dryRun,
      retentionDays: result.retentionDays,
      movedCount: result.moved.length,
      deletedCount: result.deleted.length,
      moved: result.moved,
      deleted: result.deleted
    },
    null,
    2
  )
);
