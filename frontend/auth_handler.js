// frontend/auth_handler.js
// login.html 專用的表單處理邏輯。
// 註冊 / 登入 / 訪客登入 分別打 /api/auth/register、/api/auth/login、/api/auth/guest，
// 成功後統一用 saveUserSession() 把使用者資料寫進 localStorage，
// 存的格式跟 auth.js 的 getCurrentUser() 對齊。

function rollGuestName() {
    const adjectives = ["Stellar", "Cosmic", "Astral", "Solar", "Lunar", "Nebula", "Quantum", "Orbit"];
    const nouns = ["Voyager", "Observer", "Explorer", "Pioneer", "Drifter", "Scout", "Seeker", "Astromer"];
    const randomAdj = adjectives[Math.floor(Math.random() * adjectives.length)];
    const randomNoun = nouns[Math.floor(Math.random() * nouns.length)];
    const randomNum = Math.floor(Math.random() * 900) + 100;

    const input = document.getElementById('guestNameInput');
    if (input) {
        input.value = `${randomAdj}_${randomNoun}_${randomNum}`;
    }
}

/**
 * 統一儲存使用者工作階段資料。
 * 同時寫入 JSON 物件（主要格式，供 auth.js 的 getCurrentUser() 讀取）
 * 以及拆開的獨立 key（profile.html 目前直接讀這幾個 key，保留相容用）。
 */
function saveUserSession(result) {
    const userData = {
        user_id: result.user_id,
        username: result.username,
        role_type: result.role_type,
    };
    localStorage.setItem('astro_current_user', JSON.stringify(userData));
    localStorage.setItem('user_id', result.user_id);
    localStorage.setItem('username', result.username);
    localStorage.setItem('role_type', result.role_type);
}

/**
 * 共用的 POST /api/auth/xxx 呼叫邏輯，避免三個表單各自重複寫一份 fetch。
 */
async function postAuth(endpoint, payload) {
    const response = await fetch(`/api/auth/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    const result = await response.json().catch(() => ({}));
    return { ok: response.ok, result };
}

async function handleGuestLogin() {
    const username = document.getElementById('guestNameInput')?.value.trim() || "";
    if (!username) {
        alert("請輸入或隨機產生訪客顯示名稱！");
        return;
    }

    try {
        const { ok, result } = await postAuth('guest', { username });
        if (ok) {
            saveUserSession(result);
            window.location.href = '/index.html';
        } else {
            alert(result.detail || "訪客登入失敗");
        }
    } catch (error) {
        console.error("Network error:", error);
        alert("無法連線至伺服器。");
    }
}

async function handleRegister() {
    const username = document.getElementById('regUsername')?.value.trim() || "";
    const password = document.getElementById('regPassword')?.value.trim() || "";
    const errorMsg = document.getElementById('regErrorMsg');

    if (!username || !password) {
        showError(errorMsg, "帳號與密碼皆不得為空！");
        return;
    }

    try {
        const { ok, result } = await postAuth('register', { username, password });
        if (ok) {
            saveUserSession(result);
            window.location.href = '/index.html';
        } else {
            showError(errorMsg, result.detail || "註冊失敗");
        }
    } catch (error) {
        console.error("Network error:", error);
        showError(errorMsg, "無法連線至伺服器。");
    }
}

async function handleLogin() {
    const username = document.getElementById('loginUsername')?.value.trim() || "";
    const password = document.getElementById('loginPassword')?.value.trim() || "";
    const errorMsg = document.getElementById('loginErrorMsg');

    if (!username || !password) {
        showError(errorMsg, "請輸入帳號與密碼！");
        return;
    }

    try {
        const { ok, result } = await postAuth('login', { username, password });
        if (ok) {
            saveUserSession(result);
            window.location.href = '/index.html';
        } else {
            showError(errorMsg, result.detail || "帳號或密碼錯誤");
        }
    } catch (error) {
        console.error("Network error:", error);
        showError(errorMsg, "無法連線至伺服器。");
    }
}

function showError(element, message) {
    if (element) {
        element.style.display = 'block';
        element.innerText = message;
    } else {
        alert(message);
    }
}