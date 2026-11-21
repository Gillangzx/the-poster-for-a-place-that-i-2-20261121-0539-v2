// QUARROW VALE — entrypoint: copies the committed poster to the output directory.
import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function fail(message: string): never {
  console.error(`quarrow-vale: ${message}`);
  process.exit(1);
}

function candidates(): string[] {
  const here = dirname(fileURLToPath(import.meta.url));
  return [join(here, "entry.png"), join(process.cwd(), "entry.png"), "/bot/entry.png"];
}

function findSource(): string {
  for (const p of candidates()) {
    try {
      if (existsSync(p) && statSync(p).isFile() && statSync(p).size > 0) return p;
    } catch {
      // keep looking
    }
  }
  fail("entry.png not found next to the script, in the working directory, or in /bot");
}

function checkPng(path: string): void {
  const head = readFileSync(path).subarray(0, 8);
  if (!head.equals(PNG_MAGIC)) fail(`${path} is not a PNG file`);
}

function main(): void {
  const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
  const src = findSource();
  checkPng(src);
  mkdirSync(outDir, { recursive: true });
  const dest = join(outDir, "entry.png");
  try {
    copyFileSync(src, dest);
  } catch {
    // one read/write round-trip retry before giving up
    try {
      writeFileSync(dest, readFileSync(src));
    } catch (err) {
      fail(`could not copy entry.png to ${dest}: ${err}`);
    }
  }
  try {
    checkPng(dest);
    if (statSync(dest).size === 0) fail("output entry.png is empty");
  } catch (err) {
    fail(`output verification failed: ${err}`);
  }
  console.log(`quarrow-vale: wrote ${resolve(dest)}`);
}

main();
