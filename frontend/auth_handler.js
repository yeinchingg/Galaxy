/**
 * frontend/auth_handler.js
 * 處理訪客進入、帳號註冊與登入
 * -> 全部改為真正呼叫後端 API，取得資料庫中真實的 user_id，
 *    不同帳號的資料才會在 DB 裡彼此分開。
 */

const STORAGE_KEY_USER = "astro_current_user";
const API_BASE = window.location.origin;

// 隨機產生訪客暱稱
function rollGuestName() {
  const prefixes = [
    "探索者",
    "觀星者",
    "宇航員",
    "領航員",
    "旅行者",
    "星際研究員",
  ];
  const randomPrefix = prefixes[Math.floor(Math.random() * prefixes.length)];
  const randomCode = Math.floor(1000 + Math.random() * 9000);
  const input = document.getElementById("guestNameInput");
  if (input) {
    input.value = `${randomPrefix}_${randomCode}`;
  }
}

// 儲存登入資訊：統一格式，供 auth.js / profile.html / lab.html / quiz.html 共用
function saveCurrentUser(data) {
  const userObj = {
    user_id: data.user_id,
    username: data.username,
    role: data.role,
    loginTime: new Date().toISOString(),
  };
  localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(userObj));
  return userObj;
}

// 訪客登入：呼叫後端建立一個獨立的訪客帳號（每次登入都有自己的 user_id）
async function handleGuestLogin() {
  const input = document.getElementById("guestNameInput");
  const displayName =
    input && input.value.trim() ? input.value.trim() : "訪客研究員";

  try {
    const res = await fetch(`${API_BASE}/api/auth/guest`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ display_name: displayName }),
    });
    if (!res.ok) throw new Error("guest login failed");
    const data = await res.json();
    saveCurrentUser(data);
    window.location.href = "index.html";
  } catch (e) {
    console.error("訪客登入失敗", e);
    alert("訪客登入失敗，請確認伺服器是否已啟動！");
  }
}

// 註冊帳號：真正寫入資料庫的 users 表
async function handleRegister() {
  const userInp = document.getElementById("regUsername");
  const passInp = document.getElementById("regPassword");
  const errDiv = document.getElementById("regErrorMsg");

  const username = userInp ? userInp.value.trim() : "";
  const password = passInp ? passInp.value.trim() : "";

  if (!username || !password) {
    if (errDiv) {
      errDiv.textContent = "請輸入使用者名稱與密碼！";
      errDiv.style.display = "block";
    }
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) {
      if (errDiv) {
        errDiv.textContent = data.detail || "註冊失敗！";
        errDiv.style.display = "block";
      }
      return;
    }
    saveCurrentUser(data);
    window.location.href = "index.html";
  } catch (e) {
    console.error("註冊失敗", e);
    if (errDiv) {
      errDiv.textContent = "無法連線到伺服器，請稍後再試！";
      errDiv.style.display = "block";
    }
  }
}

// 帳號密碼登入：呼叫後端驗證雜湊密碼
async function handleLogin() {
  const userInp = document.getElementById("loginUsername");
  const passInp = document.getElementById("loginPassword");
  const errDiv = document.getElementById("loginErrorMsg");

  const username = userInp ? userInp.value.trim() : "";
  const password = passInp ? passInp.value.trim() : "";

  if (!username || !password) {
    if (errDiv) {
      errDiv.textContent = "帳號與密碼不能為空！";
      errDiv.style.display = "block";
    }
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) {
      if (errDiv) {
        errDiv.textContent = data.detail || "帳號或密碼錯誤！";
        errDiv.style.display = "block";
      }
      return;
    }
    saveCurrentUser(data);
    window.location.href = "index.html";
  } catch (e) {
    console.error("登入失敗", e);
    if (errDiv) {
      errDiv.textContent = "無法連線到伺服器，請稍後再試！";
      errDiv.style.display = "block";
    }
  }
}
