console.log("script.js loaded");
const form = document.getElementById("loginForm");

if (form) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    console.log("submit fired");

    const errorEl = document.getElementById("error");
    errorEl.innerText = "";

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
      const res = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        errorEl.innerText = data.detail || "Login failed";
        return;
      }

      // Save token + go dashboard
      localStorage.setItem("token", data.access_token);
      window.location.href = "/dashboard";
    } catch (err) {
      errorEl.innerText = "Network error";
    }
  });
}
const registerForm = document.getElementById("registerForm");

if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    console.log("REGISTER submit fired"); // <-- HERE

    const msgEl = document.getElementById("registerMessage");
    msgEl.innerText = "";

    const email = document.getElementById("registerEmail").value;
    const password = document.getElementById("registerPassword").value;

    try {
      const response = await fetch("/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();
      console.log("register status:", response.status);
      console.log("register data:", data);

      if (!response.ok) {
        msgEl.innerText = data.detail || "Registration failed";
        return;
      }

      msgEl.innerText = "Registration successful. You can now log in.";
    } catch (err) {
      msgEl.innerText = "Server error. Try again.";
    }
  });
} else {
  console.log("registerForm not found");
}
