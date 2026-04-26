// Production backend on Render.
window.MEDSTORE_API_URL =
  window.MEDSTORE_API_URL ||
  (["localhost", "127.0.0.1"].includes(window.location.hostname)
    ? "http://localhost:5000"
    : "https://medstore-api.onrender.com");
