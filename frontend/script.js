const API_BASE = "http://127.0.0.1:5000";

const outputEl = document.getElementById("output");
const authStatusEl = document.getElementById("auth-status");
const roleStatusEl = document.getElementById("role-status");
const userStatusEl = document.getElementById("user-status");
const globalErrorEl = document.getElementById("global-error");

const registerPanel = document.getElementById("register-panel");
const loginPanel = document.getElementById("login-panel");

let sessionState = {
  loggedIn: false,
  mfaVerified: false,
  username: "",
  role: "",
};

function showOutput(data) {
  outputEl.textContent = JSON.stringify(data, null, 2);
}

function showMessage(message, type = "info") {
  globalErrorEl.textContent = message;
  globalErrorEl.classList.remove("hidden");

  if (type === "success") {
    globalErrorEl.classList.remove("error");
    globalErrorEl.classList.add("success");
  } else {
    globalErrorEl.classList.remove("success");
    globalErrorEl.classList.add("error");
  }
}

function clearMessage() {
  globalErrorEl.textContent = "";
  globalErrorEl.classList.add("hidden");
  globalErrorEl.classList.remove("error", "success");
}

function updateStatusPanel() {
  if (sessionState.mfaVerified) {
    authStatusEl.textContent = "Authenticated";
  } else if (sessionState.loggedIn) {
    authStatusEl.textContent = "MFA pending";
  } else {
    authStatusEl.textContent = "Not signed in";
  }

  roleStatusEl.textContent = sessionState.role || "None selected";
  userStatusEl.textContent = sessionState.username || "None";
}

function switchAuthMode() {
  const selectedMode = document.querySelector(
    'input[name="auth-mode"]:checked'
  ).value;

  if (selectedMode === "register") {
    registerPanel.classList.remove("hidden");
    loginPanel.classList.add("hidden");
  } else {
    registerPanel.classList.add("hidden");
    loginPanel.classList.remove("hidden");
  }

  clearMessage();
}

async function handleResponse(response) {
  const data = await response.json();

  if (!response.ok || data.status === "error" || data.status === "failure") {
    throw new Error(data.message || "Request failed.");
  }

  return data;
}

async function registerUser() {
  clearMessage();

  const role = document.getElementById("register-role").value;
  const username = document.getElementById("register-username").value.trim();
  const email = document.getElementById("register-email").value.trim();
  const password = document.getElementById("register-password").value;

  if (!role || !username || !email || !password) {
    showMessage("Role, username, email, and password are required.", "error");
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        role,
        username,
        email,
        password,
      }),
    });

    const data = await handleResponse(response);
    showOutput(data);

    document.getElementById("login-role").value = role;
    document.getElementById("login-username").value = username;

    showMessage(
      "Registration complete. Your email is stored for MFA. You can now log in.",
      "success"
    );

    document.getElementById("mode-login").checked = true;
    switchAuthMode();
  } catch (error) {
    showMessage(error.message, "error");
  }
}

async function loginUser() {
  clearMessage();

  const role = document.getElementById("login-role").value;
  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value;

  if (!role || !username || !password) {
    showMessage("Role, username, and password are required.", "error");
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        role,
        username,
        password,
      }),
    });

    const data = await handleResponse(response);
    showOutput(data);

    sessionState.loggedIn = true;
    sessionState.mfaVerified = false;
    sessionState.username = data.username || username;
    sessionState.role = data.role || role;

    document.getElementById("mfa-username").value = sessionState.username;

    const patientUsername = document.getElementById("patient-username");
    const providerUsername = document.getElementById("provider-username");
    const auditUsername = document.getElementById("audit-username");

    if (patientUsername) {
      patientUsername.value = sessionState.username;
    }

    if (providerUsername) {
      providerUsername.value = sessionState.username;
    }

    if (auditUsername) {
      auditUsername.value = sessionState.username;
    }

    updateStatusPanel();

    showMessage(
      "Password accepted. Check your registered email for the MFA code.",
      "success"
    );
  } catch (error) {
    showMessage(
      `${error.message} If this is a new user, register first with an email.`,
      "error"
    );
  }
}

async function verifyMfa() {
  clearMessage();

  const username = document.getElementById("mfa-username").value.trim();
  const code = document.getElementById("mfa-code").value.trim();

  if (!username || !code) {
    showMessage("Username and MFA code are required.", "error");
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/verify-mfa`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        code,
      }),
    });

    const data = await handleResponse(response);
    showOutput(data);

    sessionState.mfaVerified = true;
    sessionState.username = data.username || username;
    sessionState.role = data.role || sessionState.role;

    updateStatusPanel();
    showMessage("MFA verified. Login complete.", "success");
  } catch (error) {
    showMessage(error.message, "error");
  }
}

async function getProviderRecord() {
  clearMessage();

  if (!sessionState.mfaVerified) {
    showMessage("Please complete login and MFA first.", "error");
    return;
  }

  const recordId = document.getElementById("provider-record-id").value.trim();
  const username = sessionState.username;

  try {
    const response = await fetch(
      `${API_BASE}/records/${recordId}?username=${encodeURIComponent(username)}`
    );

    const data = await handleResponse(response);
    showOutput(data);
    showMessage("Protected record retrieved.", "success");
  } catch (error) {
    showMessage(error.message, "error");
  }
}

async function logoutUser() {
  clearMessage();

  if (sessionState.username) {
    try {
      await fetch(`${API_BASE}/logout`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: sessionState.username,
        }),
      });
    } catch {
      // Clear local session even if logout route fails.
    }
  }

  sessionState = {
    loggedIn: false,
    mfaVerified: false,
    username: "",
    role: "",
  };

  updateStatusPanel();
  showMessage("Signed out. You can register or log in again.", "success");
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("mode-register").addEventListener(
    "change",
    switchAuthMode
  );
  document.getElementById("mode-login").addEventListener("change", switchAuthMode);
  document.getElementById("register-btn").addEventListener("click", registerUser);
  document.getElementById("login-btn").addEventListener("click", loginUser);
  document.getElementById("mfa-btn").addEventListener("click", verifyMfa);

  const providerRecordButton = document.getElementById("provider-record-btn");
  if (providerRecordButton) {
    providerRecordButton.addEventListener("click", getProviderRecord);
  }

  const logoutButton = document.getElementById("logout-btn");
  if (logoutButton) {
    logoutButton.addEventListener("click", logoutUser);
  }

  updateStatusPanel();
  switchAuthMode();
});
