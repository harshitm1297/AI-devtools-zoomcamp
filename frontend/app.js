const state = {
  imageDataUrl: null,
  isDemoReceipt: false,
  receiptId: null,
  purchase: null,
  assessment: null,
};
const { money, modeCopy, validateReceiptFile } = GuardianCore;
const $ = (selector) => document.querySelector(selector);
const notice = $("#notice");

function showNotice(message) {
  notice.textContent = message;
  notice.hidden = false;
}

function clearNotice() {
  notice.hidden = true;
  notice.textContent = "";
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  if (!response.ok) {
    let message = "Something went wrong.";
    try { message = (await response.json()).detail || message; } catch (_) { /* no body */ }
    throw new Error(message);
  }
  return response.json();
}

function setStep(number) {
  document.querySelectorAll(".step").forEach((element) => {
    const value = Number(element.dataset.step);
    element.classList.toggle("active", value === number);
    element.classList.toggle("done", value < number);
  });
}

function showPanel(id, step) {
  ["upload-panel", "confirm-panel", "result-panel"].forEach((panel) => {
    document.getElementById(panel).hidden = panel !== id;
  });
  setStep(step);
  clearNotice();
}

function selectImage(dataUrl, isDemoReceipt = false) {
  state.imageDataUrl = dataUrl;
  state.isDemoReceipt = isDemoReceipt;
  const preview = $("#receipt-preview");
  preview.src = dataUrl;
  preview.hidden = false;
  $("#drop-zone").classList.add("has-image");
  $("#extract-button").disabled = false;
}

function demoReceipt() {
  const canvas = document.createElement("canvas");
  canvas.width = 560;
  canvas.height = 760;
  const context = canvas.getContext("2d");
  context.fillStyle = "#fffdf8";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = "#17251d";
  context.textAlign = "center";
  context.font = "bold 34px sans-serif";
  context.fillText("NORTHSTAR MARKET", 280, 75);
  context.font = "20px monospace";
  context.fillText("12 APR 2026", 280, 115);
  context.textAlign = "left";
  const lines = [
    ["Fresh produce", "24.20"], ["Pantry", "18.70"], ["Household", "27.50"], ["Tax", "8.00"],
  ];
  context.font = "21px monospace";
  lines.forEach(([label, amount], index) => {
    context.fillText(label, 55, 210 + index * 58);
    context.textAlign = "right";
    context.fillText(`€${amount}`, 505, 210 + index * 58);
    context.textAlign = "left";
  });
  context.strokeStyle = "#a9b5a9";
  context.beginPath(); context.moveTo(55, 475); context.lineTo(505, 475); context.stroke();
  context.font = "bold 27px monospace";
  context.fillText("TOTAL", 55, 535);
  context.textAlign = "right";
  context.fillText("€78.40", 505, 535);
  context.textAlign = "center";
  context.font = "18px monospace";
  context.fillText("THANK YOU", 280, 650);
  selectImage(canvas.toDataURL("image/png"), true);
}

$("#receipt-file").addEventListener("change", (event) => {
  const file = event.target.files[0];
  if (!file) return;
  const validationError = validateReceiptFile(file);
  if (validationError) {
    showNotice(validationError);
    return;
  }
  const reader = new FileReader();
  reader.onload = () => selectImage(reader.result, false);
  reader.readAsDataURL(file);
});

const dropZone = $("#drop-zone");
["dragenter", "dragover"].forEach((name) => dropZone.addEventListener(name, (event) => {
  event.preventDefault(); dropZone.classList.add("dragging");
}));
["dragleave", "drop"].forEach((name) => dropZone.addEventListener(name, (event) => {
  event.preventDefault(); dropZone.classList.remove("dragging");
}));
dropZone.addEventListener("drop", (event) => {
  const file = event.dataTransfer.files[0];
  if (!file) return;
  const input = $("#receipt-file");
  const transfer = new DataTransfer(); transfer.items.add(file); input.files = transfer.files;
  input.dispatchEvent(new Event("change"));
});

$("#demo-button").addEventListener("click", demoReceipt);
$("#extract-button").addEventListener("click", async () => {
  clearNotice();
  const button = $("#extract-button");
  button.disabled = true; button.textContent = "Extracting…";
  try {
    const result = await api("/api/receipts/extract", {
      method: "POST",
      body: JSON.stringify({
        image_data_url: state.imageDataUrl,
        is_demo: state.isDemoReceipt,
      }),
    });
    state.receiptId = result.receipt_id;
    const form = $("#confirm-form");
    ["merchant", "purchase_date", "total", "currency", "category"].forEach((name) => {
      form.elements[name].value = result[name];
    });
    showPanel("confirm-panel", 2);
  } catch (error) {
    showNotice(error.message);
  } finally {
    button.disabled = false; button.innerHTML = 'Extract details <span aria-hidden="true">→</span>';
  }
});

$("#confirm-form").addEventListener("submit", async (event) => {
  event.preventDefault(); clearNotice();
  const button = event.target.querySelector("button[type=submit]");
  button.disabled = true; button.textContent = "Building assessment…";
  const values = Object.fromEntries(new FormData(event.target).entries());
  values.total = Number(values.total);
  try {
    state.purchase = await api(`/api/receipts/${state.receiptId}/confirm`, {
      method: "POST", body: JSON.stringify(values),
    });
    state.assessment = await api(`/api/purchases/${state.purchase.id}/assess`, { method: "POST" });
    renderResult();
    showPanel("result-panel", 3);
  } catch (error) {
    showNotice(error.message);
  } finally {
    button.disabled = false; button.innerHTML = 'Confirm &amp; assess <span aria-hidden="true">→</span>';
  }
});

function renderResult() {
  const result = state.assessment;
  const verdict = $("#verdict");
  verdict.className = `verdict ${result.assessment}`;
  const labels = { unusual: "Worth a second look", typical: "Looks typical", insufficient_history: "More history needed" };
  const icons = { unusual: "!", typical: "✓", insufficient_history: "…" };
  $("#verdict-label").textContent = labels[result.assessment];
  $("#verdict-icon").textContent = icons[result.assessment];
  $("#result-explanation").textContent = result.explanation;
  $("#result-action").textContent = result.suggested_action;
  $("#result-total").textContent = money(state.purchase.amount, state.purchase.currency);
  $("#result-median").textContent = money(result.median_amount, state.purchase.currency);
  $("#result-threshold").textContent = money(result.threshold_amount, state.purchase.currency);
  $("#evidence-list").innerHTML = result.evidence.length
    ? result.evidence.map((item) => `<div class="evidence-item"><strong>${escapeHtml(item.merchant)}</strong><small>${item.purchase_date} · ${escapeHtml(item.category)}</small><b>${money(item.amount, item.currency)}</b></div>`).join("")
    : '<p class="muted">No comparable purchases were found.</p>';
  $("#feedback-box").hidden = false;
}

function escapeHtml(value) {
  const element = document.createElement("span"); element.textContent = value; return element.innerHTML;
}

$("#feedback-box").addEventListener("click", async (event) => {
  const value = event.target.dataset.helpful;
  if (!value) return;
  try {
    await api(`/api/assessments/${state.assessment.id}/feedback`, {
      method: "POST", body: JSON.stringify({ helpful: value === "true" }),
    });
    $("#feedback-box").innerHTML = "<span>Thanks—your feedback was saved.</span>";
  } catch (error) { showNotice(error.message); }
});

function reset() {
  state.imageDataUrl = null; state.isDemoReceipt = false;
  state.receiptId = null; state.purchase = null; state.assessment = null;
  $("#receipt-file").value = ""; $("#receipt-preview").hidden = true;
  $("#drop-zone").classList.remove("has-image"); $("#extract-button").disabled = true;
  showPanel("upload-panel", 1);
}

$("#start-over").addEventListener("click", reset);
$("#another-button").addEventListener("click", reset);

api("/version").then((data) => {
  const copy = modeCopy(data);
  $("#mode-badge").textContent = copy.badge;
  $("#mode-help").textContent = copy.help;
}).catch(() => { $("#mode-badge").textContent = "Mode unavailable"; });
