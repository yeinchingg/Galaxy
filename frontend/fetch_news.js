const API_BASE = window.location.origin;
function getUserId() {
  let userId = localStorage.getItem("astronomy_user_id");
  if (!userId) {
    userId = "user_" + Math.random().toString(36).substr(2, 9);
    localStorage.setItem("astronomy_user_id", userId);
  }
  return userId;
}

const USER_ID = getUserId();

async function fetchStatus() {
  const tag = document.getElementById("user-status-tag");
  if (!tag) return;
  try {
    const res = await fetch(`${API_BASE}/`);
    if (!res.ok) throw new Error("server not ok");
    tag.textContent = "系統連線正常";
    tag.classList.remove("badge-offline");
  } catch (err) {
    tag.textContent = "離線模式";
    tag.classList.add("badge-offline");
  }
}

async function fetchDailyKnowledge() {
  const container = document.getElementById("news-scroll");
  if (!container) return;

  try {
    const res = await fetch(`${API_BASE}/api/daily-knowledge`);
    const result = await res.json();
    const list = result.data || [];

    if (list.length === 0) {
      container.innerHTML = `<p class="news-empty">暫時沒有最新新聞。</p>`;
      return;
    }

    container.innerHTML = "";
    list.forEach((news) => {
      const card = document.createElement("a");
      card.className = "news-card";
      card.href = news.url || "https://www.nasa.gov";
      card.target = "_blank";
      card.rel = "noopener noreferrer";
      card.innerHTML = `
                <img src="${news.image_url}" alt="${news.title}"
                     onerror="this.src='https://www.nasa.gov/wp-content/uploads/2023/07/main_image_deep_field_smacs0723-5mb.jpg'">
                <div class="news-card-body">
                    <h4>${news.title}</h4>
                    <p>${news.sub_title}</p>
                </div>
            `;
      container.appendChild(card);
    });
  } catch (err) {
    console.warn("新聞 API 呼叫失敗", err);
    container.innerHTML = `<p class="news-empty">暫時無法載入最新新聞。</p>`;
  }
}

async function fetchDynamicOutline() {
  const recEl = document.getElementById("outline-recommendation");
  if (!recEl) return;

  try {
    const res = await fetch(`${API_BASE}/api/outline/${USER_ID}`);
    const data = await res.json();

    if (data.status === "success" && data.outline.length > 0) {
      const top = data.outline[0];
      recEl.textContent =
        top.visit_count > 0
          ? `根據您的瀏覽習慣，為您推薦重點探索：【${top.title}】（已探索 ${top.visit_count} 次）`
          : " ";
    }
  } catch (err) {
    console.warn("大綱 API 載入失敗", err);
  }
}

async function trackAction(topic, action, params = {}) {
  try {
    await fetch(`${API_BASE}/api/track`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: USER_ID, topic, action, params }),
    });
  } catch (err) {
    console.warn("Track failed", err);
  }
}

function navigateToModule(pageUrl, topic) {
  trackAction(topic, "view_topic");
  window.location.href = pageUrl;
}

function bindModuleTracking() {
  document.querySelectorAll("[data-topic]").forEach((el) => {
    el.addEventListener("click", (e) => {
      const topic = el.getAttribute("data-topic");
      const href = el.getAttribute("href");
      if (href && href !== "#") {
        e.preventDefault();
        navigateToModule(href, topic);
      } else {
        trackAction(topic, "click");
      }
    });
  });
}

window.addEventListener("DOMContentLoaded", () => {
  fetchStatus();
  fetchDailyKnowledge();
  fetchDynamicOutline();
  bindModuleTracking();
});
