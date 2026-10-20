(function () {
  const CURRENT_USER_KEY = "astro_current_user";
  const currentPage = window.location.pathname.split("/").pop();
  if (currentPage === "login.html" || currentPage === "") {
    return;
  }

  const savedUser = localStorage.getItem(CURRENT_USER_KEY);

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
  Object.keys(localStorage)
    .filter((k) => k.startsWith("astro_lab_session_id"))
    .forEach((k) => localStorage.removeItem(k));
  window.location.href = "login.html";
}
