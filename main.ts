// SABLEMERE — poster entrypoint.
//
// Copies the committed entry.png into the output directory the harness asks
// for ($MAKEFUN_OUTPUT_DIR, or /output when it is not set). Standard library
// only; no network, no dependencies.

import { copyFile, mkdir, readFile, stat, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function scriptDir() {
  return dirname(fileURLToPath(import.meta.url));
}

function candidates() {
  return [
    join(scriptDir(), "entry.png"),
    join(process.cwd(), "entry.png"),
    "/bot/entry.png",
  ];
}

function outputDir() {
  return process.env.MAKEFUN_OUTPUT_DIR || "/output";
}

async function looksLikePng(path) {
  try {
    const head = await readFile(path, { flag: "r" });
    return head.subarray(0, PNG_MAGIC.length).equals(PNG_MAGIC);
  } catch {
    return false;
  }
}

async function main() {
  const destDir = resolve(outputDir());
  await mkdir(destDir, { recursive: true });
  const dest = join(destDir, "entry.png");

  let source = null;
  for (const path of candidates()) {
    try {
      const info = await stat(path);
      if (info.isFile() && info.size > 0) {
        source = path;
        break;
      }
    } catch {
      // Not here; try the next location.
    }
  }
  if (source === null) {
    throw new Error("entry.png not found next to main.ts, in the cwd, or in /bot");
  }

  try {
    await copyFile(source, dest);
  } catch (err) {
    // One retry through a plain read/write round-trip.
    const data = await readFile(source);
    await writeFile(dest, data);
    if (err) {
      // The first attempt failed; the round-trip above is the recovery.
    }
  }

  if (!(await looksLikePng(dest))) {
    throw new Error("output is not a PNG (bad magic bytes)");
  }
  const info = await stat(dest);
  console.log(`wrote ${dest} (${info.size} bytes)`);
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
