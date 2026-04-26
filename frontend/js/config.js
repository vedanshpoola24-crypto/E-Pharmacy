// Local default. For production, replace the empty string below with your Render backend URL:
// window.MEDSTORE_API_URL = "https://your-medstore-api.onrender.com";
window.MEDSTORE_API_URL =
  window.MEDSTORE_API_URL ||
  "" ||
  (["localhost", "127.0.0.1"].includes(window.location.hostname) ? "http://localhost:5000" : "");
