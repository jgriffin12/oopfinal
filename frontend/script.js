const API_BASE = "https://expert-engine-69gwvjjpx7ww25gqg-5000.app.github.dev";

let selectedEmail = "";
let selectedUsername = "";
let selectedRole = "";

const emailPanel = document.getElementById("email-panel");
const loginPanel = document.getElementById("login-panel");
const registerPanel = document.getElementById("register-panel");
const mfaPanel = document.getElementById("mfa-panel");
const protectedPanel = document.getElementById("protected-panel");

const outputEl = document.getElementById("output");
const messageEl = document.getElementById("message");

const authStatusEl = document.getElementById("auth-status");
const roleStatusEl = document.getElementById("role-status");
const userStatusEl = document.getElementById("user-status");

const dashboardTitle = document.getElementById("dashboard-title");
const dashboardDescription = document.getElementById("dashboard-description");
const patientDashboard = document.getElementById("patient-dashboard");
const providerDashboard = document.getElementById("provider-dashboard");

const recordUsernameInput = document.getElementById("record-username");
const recordIdInput = document.getElementById("record-id");
const recordButton = document.getElementById("record-btn");
const recordAccessNote = document.getElementById("record-access-note");

function showPanel(panel) {
  [emailPanel, loginPanel, registerPanel, mfaPanel, protectedPanel].forEach(
    (item) => item.classList.add("hidden")
  );

  panel.classList.remove("hidden");
}

function showMessage(message, type = "info") {
  messageEl.textContent = message;
  messageEl.className = `message ${type}`;
}

function showOutput(data) {
  outputEl.textContent = JSON.stringify(data, null, 2);
}

function updateSession(authenticated, username = "", role = "") {
  authStatusEl.textContent = authenticated ? "Authenticated" : "Not signed in";
  roleStatusEl.textContent = role || "None selected";
  userStatusEl.textContent = username || "None";
}



async function handleResponse(response) {
  const data = await response.json();

  if (!response.ok || data.status === "error" || data.status === "failure") {
    throw new Error(data.message || "Request failed.");
  }

  return data;
}

async function checkEmail() {
  const email = document.getElementById("email-input").value.trim();

  if (!email) {
    showMessage("Please enter your email.", "error");
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/check-email`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email }),
    });

    const data = await handleResponse(response);
    showOutput(data);

    selectedEmail = email;

    if (data.status === "existing_user") {
      selectedUsername = data.username;
      selectedRole = data.role;

      document.getElementById("login-email").value = email;
      document.getElementById("login-username").value = data.username;
      document.getElementById("login-role").value = data.role;

      showMessage("Account found. Enter your password to continue.", "success");
      showPanel(loginPanel);
      return;
    }

    document.getElementById("register-email").value = email;

    showMessage("No account found. Register to continue.", "info");
    showPanel(registerPanel);
  } catch (error) {
    showMessage(error.message, "error");
  }
}

async function registerUser() {
  const username = document.getElementById("register-username").value.trim();
  const role = document.getElementById("register-role").value;
  const password = document.getElementById("register-password").value;
  const email = document.getElementById("register-email").value.trim();

  if (!username || !role || !password || !email) {
    showMessage("Username, role, email, and password are required.", "error");
    return;
  }

  try {
    const registerResponse = await fetch(`${API_BASE}/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        password,
        role,
        email,
      }),
    });

    const registerData = await handleResponse(registerResponse);
    showOutput(registerData);

    selectedEmail = email;
    selectedUsername = username;
    selectedRole = role;

    showMessage(
      "Registration complete. Sending your email verification code now.",
      "success"
    );

    await sendLoginRequest(username, password, role);
  } catch (error) {
    showMessage(error.message, "error");
  }
}

async function loginUser() {
  const username = document.getElementById("login-username").value.trim();
  const role = document.getElementById("login-role").value;
  const password = document.getElementById("login-password").value;

  if (!username || !role || !password) {
    showMessage("Username, role, and password are required.", "error");
    return;
  }

  await sendLoginRequest(username, password, role);
}

async function sendLoginRequest(username, password, role) {
  try {
    const response = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        password,
        role,
      }),
    });

    const data = await handleResponse(response);
    showOutput(data);

    selectedUsername = data.username || username;
    selectedRole = data.role || role;

    document.getElementById("mfa-username").value = selectedUsername;

    showMessage(
      "Verification code sent through SendGrid. Check your email.",
      "success"
    );

    showPanel(mfaPanel);
  } catch (error) {
    showMessage(error.message, "error");
  }
}

async function verifyMfa() {
  const username = document.getElementById("mfa-username").value.trim();
  const code = document.getElementById("mfa-code").value.trim();

  if (!username || !code) {
    showMessage("Username and verification code are required.", "error");
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

    selectedUsername = data.username || username;
    selectedRole = data.role || selectedRole;

    updateSession(true, selectedUsername, selectedRole);

    assignRecordAccess(selectedUsername, selectedRole);

    showMessage("MFA verified. You are signed in.", "success");
    showPanel(protectedPanel);
  } catch (error) {
    showMessage(error.message, "error");
  }
}

async function getRecord() {
  const username = document.getElementById("record-username").value.trim();
  const recordId = document.getElementById("record-id").value.trim();

  if (!username || !recordId) {
    showMessage("Username and record ID are required.", "error");
    return;
  }

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

function signOut() {
  selectedEmail = "";
  selectedUsername = "";
  selectedRole = "";

  updateSession(false);
  recordUsernameInput.value = "";
  recordIdInput.value = "1";
  recordButton.disabled = false;
  recordAccessNote.textContent =
  "Record access is assigned after MFA based on the authenticated user's role.";
  showMessage("Signed out. Enter an email to begin again.", "success");
  showPanel(emailPanel);
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("email-continue-btn").addEventListener(
    "click",
    checkEmail
  );

  document.getElementById("register-btn").addEventListener(
    "click",
    registerUser
  );

  document.getElementById("login-btn").addEventListener("click", loginUser);
  document.getElementById("mfa-btn").addEventListener("click", verifyMfa);
  document.getElementById("record-btn").addEventListener("click", getRecord);
  document.getElementById("signout-btn").addEventListener("click", signOut);

  updateSession(false);
  showPanel(emailPanel);
});
