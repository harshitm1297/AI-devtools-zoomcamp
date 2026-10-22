const test = require("node:test");
const assert = require("node:assert/strict");

const { money, modeCopy, validateReceiptFile } = require("../core.js");


test("accepts supported receipt files within the size limit", () => {
  assert.equal(validateReceiptFile({ type: "image/png", size: 1024 }), null);
  assert.equal(validateReceiptFile({ type: "image/jpeg", size: 5 * 1024 * 1024 }), null);
});

test("rejects unsupported and oversized receipt files", () => {
  assert.match(validateReceiptFile({ type: "image/gif", size: 10 }), /PNG or JPEG/);
  assert.match(validateReceiptFile({ type: "image/png", size: 5 * 1024 * 1024 + 1 }), /5 MB/);
});

test("formats amounts and insufficient history", () => {
  assert.match(money(12.5, "EUR"), /12\.50/);
  assert.equal(money(null), "Not enough history");
});

test("makes local and demo extraction modes explicit", () => {
  assert.equal(modeCopy({ ai_mode: "demo", live_receipt_extraction: false }).badge, "Demo sample only");
  assert.match(modeCopy({ ai_mode: "ollama", live_receipt_extraction: true }).help, /Local Ollama/);
});
