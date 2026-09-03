/**
 * frontend/auth.js
 * 全站共用的登入狀態守衛與工具函式。
 *
 * 儲存策略說明：
 * - 主要資料來源是 localStorage 裡的 JSON 物件（key: astro_current_user）。
 * - 另外也拆開存一份 user_id / username / role_type，是因為 profile.html
 *   目前直接讀取這幾個獨立的 key，這裡先保留相容，避免動到其他前端頁面。
 *   之後如果要重構 profile.html 改成呼叫 getCurrentUser()，
 *   就可以把這份相容存法拿掉。
 */

const ASTRO_USER_KEY = "astro_current_user";
const ASTRO_LEGACY_KEYS = ["user_id", "username", "role_type"];

(function guardPage() {
    const currentPage = window.location.pathname.split("/").pop();
    const PUBLIC_PAGES = ["login.html", ""];

    // 註：原本這裡還排除了 "login_2.html"，但整個專案裡沒有看到這個檔案，
    // 應該是舊版遺留下來的，這裡先移除。如果你那邊其實還在用 login_2.html，
    // 跟我說一聲，我再加回去。
    if (PUBLIC_PAGES.includes(currentPage)) {
        return;
    }

    const user = getCurrentUser();
    if (!user || !user.user_id) {
        clearUserSession();
        window.location.href = "login.html";
    }
})();

function getCurrentUser() {
    const raw = localStorage.getItem(ASTRO_USER_KEY);
    if (raw) {
        try {
            const parsed = JSON.parse(raw);
            if (parsed && parsed.user_id) {
                return parsed;
            }
        } catch (e) {
            // JSON 壞掉的話往下 fallback 到舊格式
        }
    }

    // 相容舊資料：只有拆開存的 key 時，組回同樣格式回傳
    const userId = localStorage.getItem("user_id");
    const username = localStorage.getItem("username");
    if (userId && username) {
        return {
            user_id: parseInt(userId, 10),
            username: username,
            role_type: localStorage.getItem("role_type") || "registered",
        };
    }
    return null;
}

/**
 * 清除所有跟登入狀態有關的 localStorage 資料。
 * 修正說明：原本 auth.js 守衛邏輯只清掉 astro_current_user 這把 key，
 * 沒有一併清掉拆開存的 user_id / username / role_type，
 * 導致被踢回登入頁後，這幾把舊 key 還留著，狀態不乾淨。
 * 現在統一用這個函式一次清乾淨。
 */
function clearUserSession() {
    localStorage.removeItem(ASTRO_USER_KEY);
    ASTRO_LEGACY_KEYS.forEach((key) => localStorage.removeItem(key));
    localStorage.removeItem("astro_lab_session_id");
}

function logout() {
    clearUserSession();
    window.location.href = "login.html";
}