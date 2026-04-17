// popup.js — Extracts JD from active tab and sends to local API
document.getElementById("captureBtn").addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const statusEl = document.getElementById("status");
  statusEl.textContent = "Extracting...";
  statusEl.style.color = "#94a3b8";

  try {
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        return window.extractJobData ? window.extractJobData() : {
          title: document.title,
          company: "",
          jd_text: document.body.innerText.substring(0, 5000),
          job_url: window.location.href,
          source: "manual"
        };
      }
    });

    const data = results[0].result;

    if (!data.title) {
      statusEl.textContent = "⚠️ Couldn't extract job data from this page";
      statusEl.style.color = "#f59e0b";
      return;
    }

    statusEl.textContent = `Sending: ${data.title.substring(0, 30)}...`;

    const response = await fetch("http://localhost:8000/api/jobs/manual", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    const result = await response.json();

    if (result.duplicate) {
      statusEl.textContent = "📌 Already captured!";
      statusEl.style.color = "#f59e0b";
    } else {
      statusEl.textContent = `✅ Captured! Match: ${Math.round((result.match_score || 0) * 100)}%`;
      statusEl.style.color = "#10b981";
    }
  } catch (e) {
    statusEl.textContent = "❌ Error: Is the copilot running?";
    statusEl.style.color = "#ef4444";
    console.error(e);
  }
});
