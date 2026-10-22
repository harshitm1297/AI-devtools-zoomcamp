(function exposeGuardianCore(root, factory) {
  const core = factory();
  if (typeof module === "object" && module.exports) module.exports = core;
  root.GuardianCore = core;
})(typeof globalThis !== "undefined" ? globalThis : this, function buildGuardianCore() {
  function validateReceiptFile(file) {
    if (!file) return "Choose a receipt image first.";
    if (!["image/png", "image/jpeg"].includes(file.type)) {
      return "Choose a PNG or JPEG image no larger than 5 MB.";
    }
    if (file.size > 5 * 1024 * 1024) {
      return "Choose a PNG or JPEG image no larger than 5 MB.";
    }
    return null;
  }

  function money(value, currency = "EUR") {
    if (value == null) return "Not enough history";
    return new Intl.NumberFormat("en", { style: "currency", currency }).format(value);
  }

  function modeCopy(data) {
    if (!data.live_receipt_extraction) {
      return {
        badge: "Demo sample only",
        help: "Demo mode does not read uploaded receipts. Use the generated sample, or start local Ollama mode.",
      };
    }
    const reader = data.ai_mode === "ollama" ? "Local Ollama" : "The configured vision model";
    return {
      badge: "Live receipt reading",
      help: `${reader} reads uploaded receipts. Confirm every extracted value.`,
    };
  }

  return { validateReceiptFile, money, modeCopy };
});
