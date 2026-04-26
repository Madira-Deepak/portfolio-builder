const API_URL = "http://127.0.0.1:8000";

// ===== SECTION NAVIGATION =====
let currentSection = 0;

function showSection(idx) {
  document.querySelectorAll(".form-section").forEach((s) => s.classList.remove("active"));
  document.querySelectorAll(".step-btn").forEach((b) => b.classList.remove("active"));

  const section = document.querySelector(`.form-section[data-section="${idx}"]`);
  const btn = document.querySelector(`.step-btn[data-section="${idx}"]`);

  if (section) {
    section.classList.add("active");
    section.style.animation = "none";
    section.offsetHeight; // reflow
    section.style.animation = "";
  }
  if (btn) btn.classList.add("active");

  currentSection = idx;
}

function markDone(idx) {
  const btn = document.querySelector(`.step-btn[data-section="${idx}"]`);
  if (btn) btn.classList.add("done");
}

// Next buttons
document.querySelectorAll(".btn-next").forEach((btn) => {
  btn.addEventListener("click", () => {
    const next = parseInt(btn.dataset.next, 10);
    if (validateSection(currentSection)) {
      markDone(currentSection);
      showSection(next);
      document.querySelector(".main").scrollTo({ top: 0, behavior: "smooth" });
    }
  });
});

// Back buttons
document.querySelectorAll(".btn-prev").forEach((btn) => {
  btn.addEventListener("click", () => {
    showSection(parseInt(btn.dataset.prev, 10));
    document.querySelector(".main").scrollTo({ top: 0, behavior: "smooth" });
  });
});

// Sidebar nav buttons
document.querySelectorAll(".step-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    showSection(parseInt(btn.dataset.section, 10));
  });
});

// ===== VALIDATION =====
function validateSection(idx) {
  const section = document.querySelector(`.form-section[data-section="${idx}"]`);
  const required = section.querySelectorAll("[required]");
  let valid = true;

  required.forEach((field) => {
    if (!field.value.trim()) {
      field.style.borderColor = "var(--danger)";
      field.addEventListener(
        "input",
        () => (field.style.borderColor = ""),
        { once: true }
      );
      valid = false;
    }
  });

  if (!valid) {
    const first = section.querySelector("[required]:invalid, [required]");
    if (first && !first.value.trim()) first.focus();
    showError("Please fill in all required fields.");
  }

  return valid;
}

// ===== STYLE CARDS =====
document.querySelectorAll(".style-card").forEach((card) => {
  card.addEventListener("click", () => {
    document.querySelectorAll(".style-card").forEach((c) => c.classList.remove("active"));
    card.classList.add("active");
  });
});

// ===== GENERATE =====
let generatedHTML = "";

document.getElementById("portfolio-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  if (!validateSection(3)) return;

  const data = gatherFormData();
  setLoading(true);
  hideError();

  try {
    const res = await fetch(`${API_URL}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Server error");
    }

    const result = await res.json();
    generatedHTML = result.content;
    showResult(generatedHTML);
  } catch (err) {
    showError(err.message || "Failed to connect to the server. Make sure the backend is running.");
  } finally {
    setLoading(false);
  }
});

function gatherFormData() {
  const g = (id) => document.getElementById(id)?.value.trim() || "";
  const selectedStyle = document.querySelector('input[name="style"]:checked')?.value || "modern";

  return {
    name: g("name"),
    title: g("title"),
    email: g("email"),
    phone: g("phone") || null,
    location: g("location") || null,
    summary: g("summary") || null,
    education: g("education"),
    skills: g("skills"),
    projects: g("projects"),
    experience: g("experience"),
    linkedin: g("linkedin") || null,
    github: g("github") || null,
    website: g("website") || null,
    style: selectedStyle,
  };
}

// ===== RESULT MODAL =====
function showResult(html) {
  const overlay = document.getElementById("result-overlay");
  const frame = document.getElementById("preview-frame");

  // Use srcdoc — works in all browsers without CSP/sandbox issues
  frame.srcdoc = html;
  overlay.hidden = false;
}

document.getElementById("close-result").addEventListener("click", () => {
  document.getElementById("result-overlay").hidden = true;
  // Clear iframe so it doesn't keep running in background
  document.getElementById("preview-frame").srcdoc = "";
});

document.getElementById("download-btn").addEventListener("click", () => {
  if (!generatedHTML) return;
  const blob = new Blob([generatedHTML], { type: "text/html" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  const name = document.getElementById("name")?.value.replace(/\s+/g, "_") || "portfolio";
  a.href = url;
  a.download = `${name}_portfolio.html`;
  a.click();
  URL.revokeObjectURL(url);
});

document.getElementById("preview-btn").addEventListener("click", () => {
  if (!generatedHTML) return;
  const blob = new Blob([generatedHTML], { type: "text/html" });
  const url = URL.createObjectURL(blob);
  window.open(url, "_blank");
});

// Close overlay on background click
document.getElementById("result-overlay").addEventListener("click", (e) => {
  if (e.target === e.currentTarget) {
    e.currentTarget.hidden = true;
    document.getElementById("preview-frame").srcdoc = "";
  }
});

// ===== HELPERS =====
function setLoading(on) {
  document.getElementById("loading").hidden = !on;
  document.getElementById("generate-btn").disabled = on;
}

function showError(msg) {
  const banner = document.getElementById("error-banner");
  document.getElementById("error-text").textContent = msg;
  banner.hidden = false;
  setTimeout(() => { banner.hidden = true; }, 6000);
}

function hideError() {
  document.getElementById("error-banner").hidden = true;
}