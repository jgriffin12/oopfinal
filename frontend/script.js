const API_BASE = "http://127.0.0.1:5000";

const outputEl = document.getElementById("output");
const authStatusEl = document.getElementById("auth-status");
const roleStatusEl = document.getElementById("role-status");
const userStatusEl = document.getElementById("user-status");

const patientCard = document.getElementById("patient-card");
const providerCard = document.getElementById("provider-card");
const auditCard = document.getElementById("audit-card");

let sessionState = {
  loggedIn: false,
  mfaVerified: false,
  username: "",
  role: ""
};

function showOutput(data) {
  outputEl.textContent = JSON.stringify(data, null, 2);
}

function showError(message) {
  outputEl.textContent = JSON.stringify(
    { status: "failure", message },
    null,
    2
  );
}

function updateStatusPanel() {
  authStatusEl.textContent = sessionState.mfaVerified
    ? "Authenticated"
    : sessionState.loggedIn
      ? "Password accepted, MFA pending"
      : "Not signed in";

  roleStatusEl.textContent = sessionState.role || "None selected";
  userStatusEl.textContent = sessionState.username || "None";
}

function updateVisibleSections() {
  patientCard.classList.add("hidden");
  providerCard.classList.add("hidden");
  auditCard.classList.add("hidden");

  if (!sessionState.mfaVerified) {
    return;
  }

  if (sessionState.role === "patient") {
    patientCard.classList.remove("hidden");
  }

  if (sessionState.role === "provider") {
    providerCard.classList.remove("hidden");
    auditCard.classList.remove("hidden");
  }
}

async function handleResponse(response) {
  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error("Server returned a non-JSON response.");
  }

  if (!response.ok) {
    throw new Error(data.message || "Request failed.");
  }

  return data;
}

function requireAuthenticatedSession() {
  if (!sessionState.mfaVerified) {
    showError("Please complete login and MFA verification first.");
    return false;
  }
  return true;
}

async function login() {
  const role = document.getElementById("login-role").value.trim();
  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value;

  if (!role) {
    showError("Please select whether you are a provider or patient.");
    return;
  }

  if (!username || !password) {
    showError("Username and password are required.");
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ username, password, role })
    });

    const data = await handleResponse(response);
    showOutput(data);

    if (data.status === "pending") {
      sessionState.loggedIn = true;
      sessionState.mfaVerified = false;
      sessionState.username = username;
      sessionState.role = role;

      document.getElementById("mfa-username").value = username;
      document.getElementById("patient-username").value = username;
      document.getElementById("provider-username").value = username;
      document.getElementById("audit-username").value = username;
    } else {
      sessionState.loggedIn = false;
      sessionState.mfaVerified = false;
      sessionState.username = "";
      sessionState.role = "";
    }

    updateStatusPanel();
    updateVisibleSections();
  } catch (error) {
    showError(error.message);
  }
}

async function verifyMfa() {
  const username = document.getElementById("mfa-username").value.trim();
  const code = document.getElementById("mfa-code").value.trim();

  if (!username || !code) {
    showError("Username and MFA code are required.");
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/verify-mfa`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ username, code })
    });

    const data = await handleResponse(response);
    showOutput(data);

    if (data.status === "success") {
      sessionState.mfaVerified = true;
    }

    updateStatusPanel();
    updateVisibleSections();
  } catch (error) {
    showError(error.message);
  }
}

async function getPatientRecord() {
  if (!requireAuthenticatedSession()) {
    return;
  }

  if (sessionState.role !== "patient") {
    showError("This section is for patient access only.");
    return;
  }

  const username = document.getElementById("patient-username").value.trim();
  const recordId = document.getElementById("patient-record-id").value.trim();

  if (!username || !recordId) {
    showError("Username and medical record ID are required.");
    return;
  }

  try {
    const response = await fetch(
      `${API_BASE}/records/${encodeURIComponent(recordId)}?username=${encodeURIComponent(username)}`
    );

    const data = await handleResponse(response);
    showOutput(data);
  } catch (error) {
    showError(error.message);
  }
}

async function getProviderRecord() {
  if (!requireAuthenticatedSession()) {
    return;
  }

  if (sessionState.role !== "provider") {
    showError("This section is for provider access only.");
    return;
  }

  const username = document.getElementById("provider-username").value.trim();
  const recordId = document.getElementById("provider-record-id").value.trim();

  if (!username || !recordId) {
    showError("Provider username and patient record ID are required.");
    return;
  }

  try {
    const response = await fetch(
      `${API_BASE}/records/${encodeURIComponent(recordId)}?username=${encodeURIComponent(username)}`
    );

    const data = await handleResponse(response);
    showOutput(data);
  } catch (error) {
    showError(error.message);
  }
}

async function getAuditLogs() {
  if (!requireAuthenticatedSession()) {
    return;
  }

  if (sessionState.role !== "provider") {
    showError("Only provider-side access should open audit logs in this demo.");
    return;
  }

  const username = document.getElementById("audit-username").value.trim();

  if (!username) {
    showError("Username is required.");
    return;
  }

  try {
    const response = await fetch(
      `${API_BASE}/admin/audit?username=${encodeURIComponent(username)}`
    );

    const data = await handleResponse(response);
    showOutput(data);
  } catch (error) {
    showError(error.message);
  }
}

document.getElementById("login-btn").addEventListener("click", login);
document.getElementById("mfa-btn").addEventListener("click", verifyMfa);
document.getElementById("patient-record-btn").addEventListener("click", getPatientRecord);
document.getElementById("provider-record-btn").addEventListener("click", getProviderRecord);
document.getElementById("audit-btn").addEventListener("click", getAuditLogs);
document.getElementById("clear-output-btn").addEventListener("click", () => {
  outputEl.textContent = "Responses will appear here.";
});

updateStatusPanel();
updateVisibleSections();