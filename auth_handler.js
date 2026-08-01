// auth_handler.js - 處理登入、註冊驗證與錯誤提示

// 取得已註冊的使用者資料庫
function getUsersDB() {
    return JSON.parse(localStorage.getItem("astro_users_db") || "{}");
}

// 儲存使用者資料庫
function saveUsersDB(db) {
    localStorage.setItem("astro_users_db", JSON.stringify(db));
}

// 訪客隨機骰子功能
function rollGuestName() {
    const adjectives = ["Stellar", "Cosmic", "Astral", "Nebula", "Solar", "Quantum", "Galaxy", "Pulsar"];
    const nouns = ["Voyager", "Pioneer", "Explorer", "Observer", "Scout", "Drifter", "Navigator", "Seeker"];
    const randomAdj = adjectives[Math.floor(Math.random() * adjectives.length)];
    const randomNoun = nouns[Math.floor(Math.random() * nouns.length)];
    const randomNum = Math.floor(100 + Math.random() * 900);
    const input = document.getElementById('guestNameInput');
    if (input) {
        input.value = `${randomAdj}_${randomNoun}_${randomNum}`;
    }
}

// 1. 訪客登入處理
function handleGuestLogin() {
    const nameInput = document.getElementById('guestNameInput');
    const guestName = nameInput ? nameInput.value.trim() : "";
    const finalName = guestName ? guestName : "Guest_" + Math.random().toString(36).substr(2, 6);

    completeLogin(finalName, "訪客 (Guest)");
}

// 2. 建立新帳號處理
function handleRegister() {
    const usernameEl = document.getElementById('regUsername');
    const passwordEl = document.getElementById('regPassword');
    const errorEl = document.getElementById('regErrorMsg');

    const username = usernameEl.value.trim();
    const password = passwordEl.value.trim();

    if (!username || !password) {
        showError(errorEl, "帳號與密碼皆不得為空！");
        return;
    }

    const db = getUsersDB();
    if (db[username]) {
        showError(errorEl, "此帳號名稱已被註冊，請換一個名字或直接登入。");
        return;
    }

    // 註冊新帳號
    db[username] = { password: password, createdAt: new Date().toLocaleString() };
    saveUsersDB(db);

    completeLogin(username, "正式研究員 (Registered)");
}

// 3. 已知帳號密碼登入處理
function handleLogin() {
    const usernameEl = document.getElementById('loginUsername');
    const passwordEl = document.getElementById('loginPassword');
    const errorEl = document.getElementById('loginErrorMsg');

    const username = usernameEl.value.trim();
    const password = passwordEl.value.trim();

    if (!username || !password) {
        showError(errorEl, "請完整輸入帳號與密碼。");
        return;
    }

    const db = getUsersDB();
    if (!db[username]) {
        showError(errorEl, "查無此帳號，請先前往「建立帳號」進行註冊。");
        return;
    }

    if (db[username].password !== password) {
        showError(errorEl, "密碼輸入錯誤，請重新確認。");
        return;
    }

    completeLogin(username, "正式研究員 (Standard Account)");
}

// 顯示紅字錯誤訊息
function showError(element, message) {
    if (element) {
        element.textContent = message;
        element.style.display = "block";
    }
}

// 通用登入成功跳轉
function completeLogin(userId, accountType) {
    const sessionData = {
        userId: userId,
        accountType: accountType,
        loginTime: new Date().toLocaleString()
    };
    localStorage.setItem("astro_user_session", JSON.stringify(sessionData));

    const targetPage = localStorage.getItem("astro_redirect_after_login") || "home";
    localStorage.removeItem("astro_redirect_after_login");
    window.location.href = "/" + targetPage;
}