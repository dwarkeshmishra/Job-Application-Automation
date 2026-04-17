// content.js — Extracts job description from current page
function extractJobData() {
  const hostname = window.location.hostname;

  if (hostname.includes("linkedin")) {
    return {
      title: document.querySelector(".job-details-jobs-unified-top-card__job-title")?.innerText || document.querySelector("h1")?.innerText || "",
      company: document.querySelector(".job-details-jobs-unified-top-card__company-name")?.innerText || "",
      jd_text: document.querySelector(".jobs-description__content")?.innerText || document.querySelector(".description__text")?.innerText || "",
      job_url: window.location.href,
      source: "linkedin"
    };
  }

  if (hostname.includes("naukri")) {
    return {
      title: document.querySelector(".jd-header-title")?.innerText || document.querySelector("h1")?.innerText || "",
      company: document.querySelector(".jd-header-comp-name")?.innerText || "",
      jd_text: document.querySelector(".job-desc")?.innerText || document.querySelector(".dang-inner-html")?.innerText || "",
      job_url: window.location.href,
      source: "naukri"
    };
  }

  if (hostname.includes("indeed")) {
    return {
      title: document.querySelector(".jobsearch-JobInfoHeader-title")?.innerText || document.querySelector("h1")?.innerText || "",
      company: document.querySelector("[data-testid='inlineHeader-companyName']")?.innerText || "",
      jd_text: document.querySelector("#jobDescriptionText")?.innerText || "",
      job_url: window.location.href,
      source: "indeed"
    };
  }

  // Fallback: grab all visible text
  return {
    title: document.title,
    company: "",
    jd_text: document.body.innerText.substring(0, 5000),
    job_url: window.location.href,
    source: "manual"
  };
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "extractJD") {
    sendResponse(extractJobData());
  }
});

// Make extractJobData available globally
window.extractJobData = extractJobData;
