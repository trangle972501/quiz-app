import fs from "node:fs/promises";

const sourcePath = "data/istqb/ctai/en/quiz_data.json";
const outputPath = "data/istqb/ctai/vi/quiz_data.json";
const separator = "@@QZSEP@@";
const source = JSON.parse(await fs.readFile(sourcePath, "utf8"));
const texts = new Set();

for (const item of source) {
  texts.add(item.question);
  for (const option of item.options) texts.add(option);
  for (const answer of item.answer) texts.add(answer);
  for (const [option, explanation] of Object.entries(item.explaination)) {
    texts.add(option);
    texts.add(explanation);
  }
}

const textList = [...texts];
const translations = new Map();
const batches = [];
let batch = [];
let batchLength = 0;
for (const [index, text] of textList.entries()) {
  const marker = `@@Q${String(index).padStart(5, "0")}@@`;
  const wrapped = `${marker}${text}${marker}`;
  if (batch.length && batchLength + wrapped.length + separator.length > 3000) {
    batches.push(batch);
    batch = [];
    batchLength = 0;
  }
  batch.push({ marker, text, wrapped });
  batchLength += wrapped.length + separator.length;
}
if (batch.length) batches.push(batch);

async function translateBatch(entries) {
  const content = entries.map((entry) => entry.wrapped).join(`\n${separator}\n`);
  const url = new URL("https://translate.googleapis.com/translate_a/single");
  url.searchParams.set("client", "gtx");
  url.searchParams.set("sl", "en");
  url.searchParams.set("tl", "vi");
  url.searchParams.set("dt", "t");
  url.searchParams.set("q", content);

  let response;
  for (let attempt = 0; attempt < 5; attempt++) {
    response = await fetch(url);
    if (response.ok) break;
    if (response.status !== 429 && response.status < 500) {
      throw new Error(`Translation service returned HTTP ${response.status}`);
    }
    await new Promise((resolve) => setTimeout(resolve, 1000 * (attempt + 1)));
  }
  if (!response?.ok) throw new Error("Translation service retries exhausted");

  const result = await response.json();
  const translated = result[0].map((part) => part[0]).join("");
  for (const entry of entries) {
    const start = translated.indexOf(entry.marker);
    const end = translated.indexOf(entry.marker, start + entry.marker.length);
    if (start < 0 || end < 0) {
      throw new Error(`Translation marker missing for: ${entry.text.slice(0, 60)}`);
    }
    translations.set(entry.text, translated.slice(start + entry.marker.length, end));
  }
}

for (let index = 0; index < batches.length; index += 2) {
  await Promise.all(batches.slice(index, index + 2).map(translateBatch));
  console.log(`Translated batch ${Math.min(index + 2, batches.length)}/${batches.length}`);
}

function translated(text) {
  const value = translations.get(text);
  if (value === undefined) throw new Error(`No translation found for: ${text.slice(0, 60)}`);
  return value;
}

const output = source.map((item) => {
  const explanation = {};
  for (const [option, detail] of Object.entries(item.explaination)) {
    explanation[translated(option)] = translated(detail);
  }
  return {
    question: translated(item.question),
    options: item.options.map(translated),
    answer: item.answer.map(translated),
    explaination: explanation,
  };
});

await fs.writeFile(outputPath, `${JSON.stringify(output, null, 4)}\n`, "utf8");
console.log(`Wrote ${output.length} questions and ${translations.size} translated text entries to ${outputPath}`);