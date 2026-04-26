const isLocalHost = ["localhost", "127.0.0.1"].includes(window.location.hostname);
const configuredApiUrl = window.MEDSTORE_API_URL || localStorage.getItem("MEDSTORE_API_URL") || "";
const API_URL = configuredApiUrl || (isLocalHost ? "http://localhost:5000" : "");
const state = {
  token: localStorage.getItem("medstore_token"),
  user: JSON.parse(localStorage.getItem("medstore_user") || "null"),
  page: "dashboard",
  medicines: [],
  suppliers: [],
  bills: [],
  prescriptions: [],
  billItems: [],
  charts: {},
};

const $ = (id) => document.getElementById(id);
const money = (value) => `Rs ${Number(value || 0).toFixed(2)}`;
const debounce = (fn, wait = 350) => {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), wait);
  };
};

async function api(path, options = {}) {
  if (!API_URL && path.startsWith("/api/")) {
    throw new Error("Backend API URL is not configured. Add your Render backend URL in frontend/js/config.js.");
  }
  const headers = options.headers || {};
  if (!(options.body instanceof FormData)) headers["Content-Type"] = "application/json";
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  const text = await response.text();
  const data = text && response.headers.get("content-type")?.includes("application/json") ? JSON.parse(text) : null;
  if (!response.ok) {
    const message = data?.message || JSON.stringify(data?.messages || data) || text || "Request failed";
    throw new Error(message);
  }
  return data;
}

function toast(message, type = "info") {
  const el = $("toast");
  el.textContent = message;
  el.style.background = type === "error" ? "var(--danger)" : type === "success" ? "var(--brand)" : "var(--text)";
  el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), 3200);
}

function setBusy(button, busy) {
  if (!button) return;
  button.disabled = busy;
  button.classList.toggle("loading", busy);
}

function showApp() {
  $("auth-view").classList.add("hidden");
  $("app-view").classList.remove("hidden");
  $("user-chip").textContent = `${state.user?.name || "User"} - ${state.user?.role || ""}`;
  navigate(state.page);
}

function showAuth() {
  $("auth-view").classList.remove("hidden");
  $("app-view").classList.add("hidden");
}

function navigate(page) {
  state.page = page;
  document.querySelectorAll(".page").forEach((p) => p.classList.remove("active"));
  $(`page-${page}`).classList.add("active");
  document.querySelectorAll(".nav").forEach((n) => n.classList.toggle("active", n.dataset.page === page));
  $("page-title").textContent = page[0].toUpperCase() + page.slice(1);
  document.querySelector(".sidebar").classList.remove("open");
  loadPage(page).catch((err) => toast(err.message, "error"));
}

async function loadPage(page) {
  if (page === "dashboard") return loadDashboard();
  if (page === "medicines") return loadMedicines();
  if (page === "suppliers") return loadSuppliers();
  if (page === "billing") return loadBills();
  if (page === "prescriptions") return loadPrescriptions();
  if (page === "reports") return loadReports();
  if (page === "notifications") return loadNotifications();
}

async function checkHealth() {
  try {
    await api("/api/health");
    $("api-chip").textContent = "API online";
  } catch {
    $("api-chip").textContent = "API offline";
  }
}

async function login(event) {
  event.preventDefault();
  const button = event.submitter;
  setBusy(button, true);
  try {
    const data = await api("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: $("login-email").value, password: $("login-password").value }),
    });
    state.token = data.access_token;
    state.user = data.user;
    localStorage.setItem("medstore_token", state.token);
    localStorage.setItem("medstore_user", JSON.stringify(state.user));
    showApp();
    toast("Logged in", "success");
  } catch (err) {
    toast(err.message, "error");
  } finally {
    setBusy(button, false);
  }
}

async function register(event) {
  event.preventDefault();
  const payload = {
    name: $("register-name").value,
    email: $("register-email").value,
    password: $("register-password").value,
    role: $("register-role").value,
  };
  try {
    await api("/api/auth/register", { method: "POST", body: JSON.stringify(payload) });
    toast("Account created", "success");
  } catch (err) {
    toast(err.message, "error");
  }
}

async function loadDashboard() {
  const [dashboard, analytics] = await Promise.all([api("/api/dashboard"), api("/api/reports/analytics")]);
  $("m-total").textContent = dashboard.total_medicines;
  $("m-low").textContent = dashboard.low_stock;
  $("m-expiring").textContent = dashboard.expiring_soon;
  $("m-sales").textContent = money(dashboard.sales_total);
  $("recent-bills").innerHTML = dashboard.recent_bills.map((b) => `<div class="list-item"><span>${b.invoice_number} - ${b.patient_name}</span><strong>${money(b.total)}</strong></div>`).join("") || empty("No bills yet");
  drawChart("sales-chart", "line", analytics.sales.map((x) => x.date), analytics.sales.map((x) => x.total), "Sales");
  drawChart("top-chart", "bar", analytics.top_selling.map((x) => x.name), analytics.top_selling.map((x) => x.qty), "Qty");
}

function drawChart(id, type, labels, values, label) {
  if (state.charts[id]) state.charts[id].destroy();
  state.charts[id] = new Chart($(id), {
    type,
    data: { labels, datasets: [{ label, data: values, borderColor: "#087f5b", backgroundColor: "rgba(8,127,91,.18)", tension: 0.35 }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
  });
}

function empty(text) {
  return `<div class="list-item"><span>${text}</span></div>`;
}

async function loadMedicines(page = 1) {
  const search = encodeURIComponent($("medicine-search").value || "");
  const data = await api(`/api/medicines?page=${page}&per_page=12&search=${search}`);
  state.medicines = data.items;
  $("medicine-rows").innerHTML = data.items.map(medicineRow).join("") || `<tr><td colspan="7">No medicines found</td></tr>`;
  $("medicine-pages").innerHTML = pager(data, (p) => `loadMedicines(${p})`);
  await loadSuppliers(true);
}

function medicineRow(m) {
  const status = m.status === "low_stock" ? "warn" : "ok";
  return `<tr>
    <td><strong>${m.name}</strong><br><span class="chip">${m.category}${m.rx_required ? " - Rx" : ""}</span></td>
    <td>${m.batch || "-"}</td><td><span class="badge ${status}">${m.stock}/${m.min_stock}</span></td><td>${m.expiry_date}</td>
    <td>${money(m.mrp)}</td><td>${m.supplier_name || "-"}</td>
    <td class="row-actions"><button class="icon-btn" onclick="openMedicine(${m.id})" title="Edit"><i data-lucide="pencil"></i></button><button class="icon-btn" onclick="openStock(${m.id})" title="Stock"><i data-lucide="package-plus"></i></button></td>
  </tr>`;
}

async function findBarcode() {
  const code = $("barcode-input").value.trim();
  if (!code) return;
  try {
    const m = await api(`/api/medicines/barcode/${encodeURIComponent(code)}`);
    $("medicine-search").value = m.name;
    await loadMedicines();
    toast(`Found ${m.name}`, "success");
  } catch (err) {
    toast(err.message, "error");
  }
}

async function loadSuppliers(cacheOnly = false) {
  const search = cacheOnly ? "" : encodeURIComponent($("supplier-search").value || "");
  const data = await api(`/api/suppliers?per_page=100&search=${search}`);
  state.suppliers = data.items;
  if (!cacheOnly) {
    $("supplier-rows").innerHTML = data.items.map((s) => `<tr><td><strong>${s.name}</strong></td><td>${s.contact}</td><td>${s.phone}</td><td>${s.email || "-"}</td><td>${s.city || "-"}</td><td class="row-actions"><button class="icon-btn" onclick="openSupplier(${s.id})"><i data-lucide="pencil"></i></button></td></tr>`).join("") || `<tr><td colspan="6">No suppliers found</td></tr>`;
  }
  lucide.createIcons();
}

function pager(data, action) {
  if (data.pages <= 1) return "";
  return `<button class="btn small" ${data.page <= 1 ? "disabled" : ""} onclick="${action(data.page - 1)}">Prev</button><span class="chip">${data.page}/${data.pages}</span><button class="btn small" ${data.page >= data.pages ? "disabled" : ""} onclick="${action(data.page + 1)}">Next</button>`;
}

function openModal(title, html) {
  $("modal-title").textContent = title;
  $("modal-body").innerHTML = html;
  $("modal").classList.remove("hidden");
  lucide.createIcons();
}

function closeModal() {
  $("modal").classList.add("hidden");
  $("modal-body").innerHTML = "";
}

function openMedicine(id) {
  const m = state.medicines.find((x) => x.id === id) || {};
  openModal(id ? "Edit Medicine" : "Add Medicine", `
    <form id="medicine-form" class="form-grid">
      <label>Name<input name="name" value="${m.name || ""}" required></label>
      <label>Category<input name="category" value="${m.category || ""}" required></label>
      <label>Manufacturer<input name="manufacturer" value="${m.manufacturer || ""}"></label>
      <label>Supplier<select name="supplier_id"><option value="">None</option>${state.suppliers.map((s) => `<option value="${s.id}" ${s.id === m.supplier_id ? "selected" : ""}>${s.name}</option>`).join("")}</select></label>
      <label>Barcode<input name="barcode" value="${m.barcode || ""}"></label>
      <label>Batch<input name="batch" value="${m.batch || ""}"></label>
      <label>Expiry<input name="expiry_date" type="date" value="${m.expiry_date || ""}" required></label>
      <label>Stock<input name="stock" type="number" value="${m.stock ?? 0}" required></label>
      <label>Min Stock<input name="min_stock" type="number" value="${m.min_stock ?? 50}"></label>
      <label>Reorder Qty<input name="reorder_quantity" type="number" value="${m.reorder_quantity ?? 100}"></label>
      <label>MRP<input name="mrp" type="number" step="0.01" value="${m.mrp || ""}" required></label>
      <label>Purchase<input name="purchase_price" type="number" step="0.01" value="${m.purchase_price || "0.00"}"></label>
      <label>GST %<select name="gst_rate"><option>0</option><option>5</option><option>12</option><option>18</option></select></label>
      <label>Rx Required<select name="rx_required"><option value="false">No</option><option value="true" ${m.rx_required ? "selected" : ""}>Yes</option></select></label>
      <label class="full">Description<textarea name="description">${m.description || ""}</textarea></label>
      <div class="form-actions full"><button class="btn" type="button" onclick="closeModal()">Cancel</button><button class="btn primary">Save</button></div>
    </form>`);
  $("medicine-form").onsubmit = (event) => saveMedicine(event, id);
}

async function saveMedicine(event, id) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const payload = Object.fromEntries(form.entries());
  payload.supplier_id = payload.supplier_id ? Number(payload.supplier_id) : null;
  payload.stock = Number(payload.stock);
  payload.min_stock = Number(payload.min_stock);
  payload.reorder_quantity = Number(payload.reorder_quantity);
  payload.rx_required = payload.rx_required === "true";
  try {
    await api(`/api/medicines${id ? `/${id}` : ""}`, { method: id ? "PUT" : "POST", body: JSON.stringify(payload) });
    closeModal();
    await loadMedicines();
    toast("Medicine saved", "success");
  } catch (err) {
    toast(err.message, "error");
  }
}

function openStock(id) {
  openModal("Stock Adjustment", `<form id="stock-form" class="stack"><label>Delta<input name="delta" type="number" placeholder="Use negative for reduction" required></label><label>Reason<input name="reason" required></label><div class="form-actions"><button class="btn" type="button" onclick="closeModal()">Cancel</button><button class="btn primary">Apply</button></div></form>`);
  $("stock-form").onsubmit = async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(event.currentTarget).entries());
    payload.delta = Number(payload.delta);
    try {
      await api(`/api/medicines/${id}/adjust-stock`, { method: "POST", body: JSON.stringify(payload) });
      closeModal();
      await loadMedicines();
      toast("Stock adjusted", "success");
    } catch (err) {
      toast(err.message, "error");
    }
  };
}

function openSupplier(id) {
  const s = state.suppliers.find((x) => x.id === id) || {};
  openModal(id ? "Edit Supplier" : "Add Supplier", `<form id="supplier-form" class="form-grid">
    <label>Name<input name="name" value="${s.name || ""}" required></label><label>Contact<input name="contact" value="${s.contact || ""}" required></label>
    <label>Phone<input name="phone" value="${s.phone || ""}" required></label><label>Email<input name="email" value="${s.email || ""}"></label>
    <label>City<input name="city" value="${s.city || ""}"></label><label>GST<input name="gst" value="${s.gst || ""}"></label>
    <div class="form-actions full"><button class="btn" type="button" onclick="closeModal()">Cancel</button><button class="btn primary">Save</button></div></form>`);
  $("supplier-form").onsubmit = (event) => saveSupplier(event, id);
}

async function saveSupplier(event, id) {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(event.currentTarget).entries());
  try {
    await api(`/api/suppliers${id ? `/${id}` : ""}`, { method: id ? "PUT" : "POST", body: JSON.stringify(payload) });
    closeModal();
    await loadSuppliers();
    toast("Supplier saved", "success");
  } catch (err) {
    toast(err.message, "error");
  }
}

async function loadBills() {
  const search = encodeURIComponent($("bill-search").value || "");
  const data = await api(`/api/bills?per_page=50&search=${search}`);
  state.bills = data.items;
  $("bill-rows").innerHTML = data.items.map((b) => `<tr><td><strong>${b.invoice_number}</strong></td><td>${b.patient_name}</td><td>${new Date(b.bill_date).toLocaleString()}</td><td>${money(b.gst_total)}</td><td>${money(b.total)}</td><td><span class="badge ${b.status === "refunded" ? "danger" : "ok"}">${b.status}</span></td><td class="row-actions"><button class="icon-btn" onclick="printInvoice(${b.id})" title="Print"><i data-lucide="printer"></i></button><button class="icon-btn" onclick="pdfInvoice(${b.id})" title="PDF"><i data-lucide="download"></i></button><button class="icon-btn" onclick="refundBill(${b.id})" title="Refund"><i data-lucide="rotate-ccw"></i></button></td></tr>`).join("") || `<tr><td colspan="7">No bills found</td></tr>`;
  lucide.createIcons();
}

function openBill() {
  state.billItems = [];
  openModal("Create Bill", `<form id="bill-form" class="stack">
    <div class="form-grid"><label>Patient<input name="patient_name" required></label><label>Phone<input name="phone"></label><label>Doctor<input name="doctor_name"></label><label>Prescription ID<input name="prescription_id" type="number"></label></div>
    <div class="toolbar"><select id="bill-med">${state.medicines.map((m) => `<option value="${m.id}">${m.name} - ${money(m.mrp)} - Stock ${m.stock}</option>`).join("")}</select><input id="bill-qty" type="number" min="1" value="1"><input id="bill-discount" type="number" step="0.01" value="0"><button class="btn" type="button" onclick="addBillItem()">Add Item</button></div>
    <div class="table-wrap"><table><thead><tr><th>Medicine</th><th>Qty</th><th>Discount</th><th></th></tr></thead><tbody id="bill-item-rows"></tbody></table></div>
    <label>Payment Mode<select name="mode"><option value="cash">Cash</option><option value="card">Card</option><option value="upi">UPI</option></select></label>
    <div class="form-actions"><button class="btn" type="button" onclick="closeModal()">Cancel</button><button class="btn primary">Create Invoice</button></div>
  </form>`);
  renderBillItems();
  $("bill-form").onsubmit = saveBill;
}

function addBillItem() {
  const id = Number($("bill-med").value);
  const med = state.medicines.find((m) => m.id === id);
  state.billItems.push({ medicine_id: id, name: med.name, qty: Number($("bill-qty").value), discount: $("bill-discount").value || "0.00" });
  renderBillItems();
}

function renderBillItems() {
  $("bill-item-rows").innerHTML = state.billItems.map((item, i) => `<tr><td>${item.name}</td><td>${item.qty}</td><td>${money(item.discount)}</td><td class="row-actions"><button class="icon-btn" type="button" onclick="state.billItems.splice(${i},1);renderBillItems()"><i data-lucide="trash-2"></i></button></td></tr>`).join("") || `<tr><td colspan="4">No items</td></tr>`;
  lucide.createIcons();
}

async function saveBill(event) {
  event.preventDefault();
  const form = Object.fromEntries(new FormData(event.currentTarget).entries());
  if (!state.billItems.length) return toast("Add at least one item", "error");
  const previewTotal = state.billItems.reduce((sum, item) => {
    const med = state.medicines.find((m) => m.id === item.medicine_id);
    const taxable = Number(med.mrp) * item.qty - Number(item.discount || 0);
    return sum + taxable + taxable * Number(med.gst_rate || 0) / 100;
  }, 0);
  const { mode, ...billFields } = form;
  const items = state.billItems.map((item) => ({
    medicine_id: item.medicine_id,
    qty: item.qty,
    discount: item.discount || "0.00",
  }));
  const payload = {
    ...billFields,
    prescription_id: form.prescription_id ? Number(form.prescription_id) : null,
    items,
    payments: [{ mode, amount: previewTotal.toFixed(2) }],
  };
  try {
    const bill = await api("/api/bills", { method: "POST", body: JSON.stringify(payload) });
    closeModal();
    await Promise.all([loadBills(), loadMedicines()]);
    toast(`Invoice ${bill.invoice_number} created`, "success");
  } catch (err) {
    toast(err.message, "error");
  }
}

async function printInvoice(id) {
  const bill = state.bills.find((b) => b.id === id) || await api(`/api/bills/${id}`);
  const win = window.open("", "_blank");
  win.document.write(invoiceHtml(bill));
  win.document.close();
  win.print();
}

function pdfInvoice(id) {
  const bill = state.bills.find((b) => b.id === id);
  const doc = new jspdf.jsPDF();
  doc.text(`Invoice ${bill.invoice_number}`, 14, 18);
  doc.text(`Patient: ${bill.patient_name}`, 14, 30);
  doc.text(`Total: ${money(bill.total)}`, 14, 42);
  doc.text(`GST: ${money(bill.gst_total)}`, 14, 54);
  doc.save(`${bill.invoice_number}.pdf`);
}

function invoiceHtml(bill) {
  return `<html><head><title>${bill.invoice_number}</title><style>body{font-family:Arial;padding:24px}table{width:100%;border-collapse:collapse}td,th{border-bottom:1px solid #ddd;padding:8px;text-align:left}</style></head><body><h1>MedStore Invoice</h1><p>${bill.invoice_number}</p><p>${bill.patient_name} - ${bill.phone || ""}</p><table><tr><th>Item</th><th>Qty</th><th>Total</th></tr>${(bill.items || []).map((i) => `<tr><td>${i.name}</td><td>${i.qty}</td><td>${money(i.line_total)}</td></tr>`).join("")}</table><h2>${money(bill.total)}</h2></body></html>`;
}

async function refundBill(id) {
  if (!confirm("Refund this bill and restore stock?")) return;
  try {
    await api(`/api/bills/${id}/refund`, { method: "POST", body: "{}" });
    await loadBills();
    toast("Bill refunded", "success");
  } catch (err) {
    toast(err.message, "error");
  }
}

async function loadPrescriptions() {
  const search = encodeURIComponent($("rx-search").value || "");
  const data = await api(`/api/prescriptions?per_page=50&search=${search}`);
  state.prescriptions = data.items;
  $("rx-rows").innerHTML = data.items.map((r) => `<tr><td>${r.patient_name}</td><td>${r.doctor_name}</td><td>${r.issue_date}</td><td>${r.valid_until || "-"}</td><td><span class="badge">${r.status}</span></td><td class="row-actions"><button class="icon-btn" onclick="verifyRx(${r.id})"><i data-lucide="badge-check"></i></button></td></tr>`).join("") || `<tr><td colspan="6">No prescriptions found</td></tr>`;
  lucide.createIcons();
}

function openPrescription() {
  openModal("Upload Prescription", `<form id="rx-form" class="form-grid">
    <label>Patient<input name="patient_name" required></label><label>Age<input name="age" type="number"></label>
    <label>Doctor<input name="doctor_name" required></label><label>Reg No<input name="doctor_reg_no"></label>
    <label>Issue Date<input name="issue_date" type="date" required></label><label>Valid Until<input name="valid_until" type="date"></label>
    <label class="full">Medicines<textarea name="medicines_text"></textarea></label><label class="full">File<input name="file" type="file" accept="image/*,.pdf"></label>
    <div class="form-actions full"><button class="btn" type="button" onclick="closeModal()">Cancel</button><button class="btn primary">Save</button></div></form>`);
  $("rx-form").onsubmit = savePrescription;
}

async function savePrescription(event) {
  event.preventDefault();
  try {
    await api("/api/prescriptions", { method: "POST", body: new FormData(event.currentTarget), headers: {} });
    closeModal();
    await loadPrescriptions();
    toast("Prescription saved", "success");
  } catch (err) {
    toast(err.message, "error");
  }
}

async function verifyRx(id) {
  await api(`/api/prescriptions/${id}/verify`, { method: "POST", body: "{}" });
  await loadPrescriptions();
  toast("Prescription verified", "success");
}

async function loadReports() {
  const [analytics, supplier] = await Promise.all([api("/api/reports/analytics"), api("/api/reports/supplier-wise")]);
  $("gst-report").textContent = money(analytics.gst_report.gst_collected);
  $("profit-report").textContent = money(analytics.profit_loss.gross_profit);
  $("supplier-report").innerHTML = supplier.map((s) => `<div class="list-item"><span>${s.supplier}</span><strong>${s.medicine_count} medicines - ${s.stock_units} units</strong></div>`).join("");
}

async function loadNotifications() {
  const data = await api("/api/notifications");
  $("notification-list").innerHTML = data.map((n) => `<div class="list-item"><span><strong>${n.title}</strong><br>${n.message}</span><button class="btn small" onclick="markNotification(${n.id})">Read</button></div>`).join("") || empty("No notifications");
}

async function markNotification(id) {
  await api(`/api/notifications/${id}/read`, { method: "POST", body: "{}" });
  await loadNotifications();
}

async function refreshAlerts() {
  await api("/api/notifications/refresh-alerts", { method: "POST", body: "{}" });
  await loadNotifications();
  toast("Alerts refreshed", "success");
}

async function chat(event) {
  event.preventDefault();
  const input = $("chat-input");
  const message = input.value.trim();
  if (!message) return;
  appendChat(message, "user");
  input.value = "";
  try {
    const data = await api("/api/ai/chat", { method: "POST", body: JSON.stringify({ message }) });
    appendChat(`${data.answer}${data.matches?.length ? "<br>" + data.matches.map((m) => `${m.name} - Stock ${m.stock} - ${money(m.mrp)}`).join("<br>") : ""}`);
  } catch (err) {
    appendChat(err.message);
  }
}

function appendChat(html, who = "assistant") {
  $("chat-log").insertAdjacentHTML("beforeend", `<div class="bubble ${who}">${html}</div>`);
  $("chat-log").scrollTop = $("chat-log").scrollHeight;
}

function wire() {
  $("login-form").onsubmit = login;
  $("register-form").onsubmit = register;
  $("toggle-register").onclick = () => {
    const form = $("register-form");
    form.style.display = form.style.display === "grid" ? "none" : "grid";
  };
  $("logout-btn").onclick = () => {
    localStorage.removeItem("medstore_token");
    localStorage.removeItem("medstore_user");
    state.token = null;
    state.user = null;
    showAuth();
  };
  $("theme-btn").onclick = () => {
    const next = document.documentElement.dataset.theme === "dark" ? "" : "dark";
    document.documentElement.dataset.theme = next;
    localStorage.setItem("theme", next);
  };
  $("mobile-menu").onclick = () => document.querySelector(".sidebar").classList.toggle("open");
  $("modal-close").onclick = closeModal;
  document.querySelectorAll(".nav,[data-page-link]").forEach((el) => el.onclick = () => navigate(el.dataset.page || el.dataset.pageLink));
  $("medicine-search").oninput = debounce(() => loadMedicines());
  $("supplier-search").oninput = debounce(() => loadSuppliers());
  $("bill-search").oninput = debounce(() => loadBills());
  $("rx-search").oninput = debounce(() => loadPrescriptions());
  $("barcode-btn").onclick = findBarcode;
  $("add-medicine-btn").onclick = () => openMedicine();
  $("add-supplier-btn").onclick = () => openSupplier();
  $("new-bill-btn").onclick = async () => { await loadMedicines(); openBill(); };
  $("add-rx-btn").onclick = openPrescription;
  $("refresh-alerts-btn").onclick = refreshAlerts;
  $("chat-form").onsubmit = chat;
}

document.documentElement.dataset.theme = localStorage.getItem("theme") || "";
wire();
Object.assign(window, {
  state,
  navigate,
  loadMedicines,
  openMedicine,
  openStock,
  openSupplier,
  addBillItem,
  renderBillItems,
  printInvoice,
  pdfInvoice,
  refundBill,
  verifyRx,
  markNotification,
  closeModal,
});
lucide.createIcons();
checkHealth();
if (state.token) showApp(); else showAuth();
