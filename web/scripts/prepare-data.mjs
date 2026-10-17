// Copy the site's data into web/public/data before `vite build` or `vite dev`.
//   node scripts/prepare-data.mjs [DATA_DIR]     (default: ../data, i.e. the data branch checkout)
// Only the files the site needs are copied; backups and review lists stay behind.
import { copyFileSync, existsSync, mkdirSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";

const here = resolve(import.meta.dirname, "..");
const src = resolve(here, process.argv[2] || "../data");
const out = join(here, "public", "data");
rmSync(out, { recursive: true, force: true });
mkdirSync(join(out, "vocab"), { recursive: true });

if (!existsSync(join(src, "data.json"))) {
  console.error(`data.json not found in ${src}`);
  process.exit(1);
}
const files = readdirSync(src).filter((f) => f === "data.json" || f === "run_summary.json" || /^history_archive_\d{4}\.json$/.test(f));
for (const f of files) copyFileSync(join(src, f), join(out, f));
for (const f of ["ksa_vocabulary.json", "task_vocabulary.json", "major_vocabulary.json"]) {
  copyFileSync(resolve(here, "../vocab", f), join(out, "vocab", f));
}
const archives = files.map((f) => f.match(/^history_archive_(\d{4})\.json$/)?.[1]).filter(Boolean).sort().reverse();
writeFileSync(join(out, "index.json"), JSON.stringify({ archives }));
console.log(`copied ${files.join(", ")} + vocab from ${src}`);
