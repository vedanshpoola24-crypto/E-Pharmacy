// Production backend on Render.
window.MEDSTORE_API_URL =
  window.MEDSTORE_API_URL ||
  "https://medstore-api.onrender.com" ||
  (["localhost", "127.0.0.1"].includes(window.location.hostname) ? "http://localhost:5000" : "");
