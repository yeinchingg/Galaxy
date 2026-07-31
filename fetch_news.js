const API_BASE = "http://127.0.0.1:8000";

// ---------------------------------------------------------------
// 1. 使用者 ID：存在 localStorage，讓「大綱推薦 / 行為追蹤」認得同一人
// ---------------------------------------------------------------
function getUserId() {
    let userId = localStorage.getItem("astronomy_user_id");
    if (!userId) {
        userId = "user_" + Math.random().toString(36).substr(2, 9);
        localStorage.setItem("astronomy_user_id", userId);
    }
    return userId;
}

const USER_ID = getUserId();

// ---------------------------------------------------------------
// 2. 系統連線狀態（若頁面上有 #user-status-tag 才會顯示）
// ---------------------------------------------------------------
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

// ---------------------------------------------------------------
// 3. 今日天文新聞（若頁面上有 #news-scroll 才會顯示）
//    卡片樣式沿用網站既有的 card-item 視覺語言（見 <style> 的 .news-card），
//    而不是另外套一份獨立的 slider 元件系統。
// ---------------------------------------------------------------
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
            card.href = news.url;
            card.target = "_blank";
            card.rel = "noopener noreferrer";
            card.innerHTML = `
                <img src="${news.image_url}" alt="${news.title}"
                     onerror="this.src='https://via.placeholder.com/300x180?text=Astronomy+News'">
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

// ---------------------------------------------------------------
// 4. 個人化課程大綱推薦（若頁面上有 #outline-recommendation 才會顯示）
// ---------------------------------------------------------------
async function fetchDynamicOutline() {
    const recEl = document.getElementById("outline-recommendation");
    if (!recEl) return;

    try {
        const res = await fetch(`${API_BASE}/api/outline/${USER_ID}`);
        const data = await res.json();

        if (data.status === "success" && data.outline.length > 0) {
            const top = data.outline[0];
            recEl.textContent = top.visit_count > 0
                ? `根據您的瀏覽習慣，為您推薦重點探索：【${top.title}】（已探索 ${top.visit_count} 次）`
                : " ";
        }
    } catch (err) {
        console.warn("大綱 API 載入失敗", err);
    }
}

// ---------------------------------------------------------------
// 5. 使用者行為追蹤 + 模組導頁
// ---------------------------------------------------------------
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

// 幫所有 data-topic 的連結自動掛上追蹤事件，
// 不用在每個 <a> 上寫一次 onclick="trackAction(...)"。
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

// ---------------------------------------------------------------
// 進入點：頁面載入後統一初始化
// ---------------------------------------------------------------
window.addEventListener("DOMContentLoaded", () => {
    fetchStatus();
    fetchDailyKnowledge();
    fetchDynamicOutline();
    bindModuleTracking();
});
