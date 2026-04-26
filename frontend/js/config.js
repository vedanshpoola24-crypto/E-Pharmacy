// For production, paste your Render backend URL below:
// Example: window.MEDSTORE_API_URL = "https://medstore-api.onrender.com";
window.MEDSTORE_API_URL =
  window.MEDSTORE_API_URL ||
  "" ||
  (["localhost", "127.0.0.1"].includes(window.location.hostname) ? "http://localhost:5000" : "");
