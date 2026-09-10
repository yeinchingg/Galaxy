/**
 * frontend/auth.js
 * 前端身分驗證與路由守衛：未登入自動跳轉至登入頁
 */

(function () {
  const CURRENT_USER_KEY = "astro_current_user";
  const currentPage = window.location.pathname.split("/").pop();

  // 如果目前就是登入頁，不做跳轉檢查
  if (currentPage === "login.html" || currentPage === "") {
    return;
  }

  const savedUser = localStorage.getItem(CURRENT_USER_KEY);

  // 未登入狀態，直接強制跳轉回登入頁
  if (!savedUser) {
    window.location.href = "login.html";
    return;
  }

  try {
    const userObj = JSON.parse(savedUser);
    if (!userObj || !userObj.username) {
      localStorage.removeItem(CURRENT_USER_KEY);
      window.location.href = "login.html";
    }
  } catch (e) {
    localStorage.removeItem(CURRENT_USER_KEY);
    window.location.href = "login.html";
  }
})();

function getCurrentUser() {
  const raw = localStorage.getItem("astro_current_user");
  return raw ? JSON.parse(raw) : null;
}

function logout() {
  localStorage.removeItem("astro_current_user");
  // 清掉所有帳號各自的實驗室聊天 session（astro_lab_session_id_<user_id>）
  Object.keys(localStorage)
    .filter((k) => k.startsWith("astro_lab_session_id"))
    .forEach((k) => localStorage.removeItem(k));
  window.location.href = "login.html";
}
