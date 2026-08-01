function getCurrentPageName() {
    const path = window.location.pathname;
    const segments = path.split("/").filter(Boolean);
    return segments.length > 0 ? segments[segments.length - 1] : "home";
}

const CURRENT_PAGE = getCurrentPageName();
const LOGIN_PAGE = "login";

function checkAuth() {
    if (CURRENT_PAGE !== LOGIN_PAGE) {
        const userSession = localStorage.getItem("astro_user_session");
        if (!userSession) {
            localStorage.setItem("astro_redirect_after_login", CURRENT_PAGE);
            window.location.href = "/login";
            return false;
        }
    }
    return true;
}

checkAuth();