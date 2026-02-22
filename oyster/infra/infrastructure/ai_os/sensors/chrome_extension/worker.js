const HUB = "http://127.0.0.1:8787/report";


async function send(payload) {
  const token = await chrome.storage.local.get(["AIOS_TOKEN"]);
  return fetch(HUB, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-AIOS-Token": token.AIOS_TOKEN || ""
    },
    body: JSON.stringify(payload)
  }).catch(() => {});
}


function getDomain(url) {
  try { return new URL(url).hostname; } catch { return ""; }
}


// Debounce per tab
const lastSent = new Map();


chrome.tabs.onActivated.addListener(async (info) => {
  const tab = await chrome.tabs.get(info.tabId);
  if (!tab || !tab.url) return;
  const domain = getDomain(tab.url);
  const key = `${info.tabId}:${domain}`;
  const now = Date.now();
  if (lastSent.get(key) && now - lastSent.get(key) < 15000) return; // 15s throttle
  lastSent.set(key, now);


  await send({ source: "chrome", domain, title: tab.title || "", intent: "none" });
});


chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (!changeInfo.url) return;
  const domain = getDomain(changeInfo.url);
  const key = `${tabId}:${domain}`;
  const now = Date.now();
  if (lastSent.get(key) && now - lastSent.get(key) < 15000) return;
  lastSent.set(key, now);


  await send({ source: "chrome", domain, title: tab.title || "", intent: "none" });
});
