/**
 * frontend/auth_handler.js
 * 處理訪客進入、帳號註冊與登入
 */

const STORAGE_KEY_USER = "astro_current_user";

// 隨機產生訪客暱稱
function rollGuestName() {
    const prefixes = ["探索者", "觀星者", "宇航員", "領航員", "旅行者", "星際研究員"];
    const randomPrefix = prefixes[Math.floor(Math.random() * prefixes.length)];
    const randomCode = Math.floor(1000 + Math.random() * 9000);
    const input = document.getElementById("guestNameInput");
    if (input) {
        input.value = `${randomPrefix}_${randomCode}`;
    }
}

// 訪客登入
function handleGuestLogin() {
    const input = document.getElementById("guestNameInput");
    const username = input && input.value.trim() ? input.value.trim() : "訪客研究員";

    const userObj = {
        username: username,
        role: "guest",
        loginTime: new Date().toISOString()
    };

    localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(userObj));
    // 登入成功，進入主教學平台
    window.location.href = "index.html";
}

// 註冊帳號
function handleRegister() {
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

    const userObj = {
        username: username,
        role: "member",
        loginTime: new Date().toISOString()
    };

    localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(userObj));
    window.location.href = "index.html";
}

// 帳號密碼登入
function handleLogin() {
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

    const userObj = {
        username: username,
        role: "member",
        loginTime: new Date().toISOString()
    };

    localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(userObj));
    window.location.href = "index.html";
}