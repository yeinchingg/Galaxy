/**
 * 統一的時間與日期工具箱
 */

// 核心時間產生器：所有時間格式化都走這裡
function getFormattedTimeString(targetInput = null) {
    const targetTime = targetInput ? new Date(targetInput) : new Date();
    const now = isNaN(targetTime.getTime()) ? new Date() : targetTime;

    const dateOptions = { timeZone: "Asia/Taipei", year: 'numeric', month: '2-digit', day: '2-digit' };
    const timeOptions = {
        timeZone: "Asia/Taipei",
        hour12: false,
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
    };

    const loginTimeOptions = {
        timeZone: "Asia/Taipei",
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
    };

    return {
        dateStr: new Intl.DateTimeFormat('en-GB', dateOptions).format(now), // 例: 2026/10/08
        timeStr: new Intl.DateTimeFormat('en-GB', timeOptions).format(now), // 例: 14:33:04
        loginStr: new Intl.DateTimeFormat('zh-TW', loginTimeOptions).format(now), // 例: 2026/10/8 下午 2:47:35
        nowObj: now
    };
}

// 取得簡短日期 (例如 "10/8")，用在 sky.html
function getFormattedCurrentDate() {
    const { nowObj } = getFormattedTimeString();
    return `${nowObj.getMonth() + 1}/${nowObj.getDate()}`;
}

// 後端傳來的歷史紀錄時間戳格式化
function formatTimestamp(ts) {
    if (!ts) return "";
    let isoStr = ts.replace(" ", "T");
    if (!isoStr.endsWith("Z") && !isoStr.includes("+")) {
        isoStr += "Z";
    }
    return new Date(isoStr).toLocaleString();
}

/**
 * 計算本地恆星時 (LST) - 天文專用
 */
function calculateLST(longitude, astroTime) {
    const gast = Astronomy.SiderealTime(astroTime);
    const lst = (gast + longitude / 15.0 + 24.0) % 24.0;

    const hours = Math.floor(lst).toString().padStart(2, "0");
    const minutes = Math.floor((lst % 1) * 60).toString().padStart(2, "0");
    const seconds = Math.floor((((lst % 1) * 60) % 1) * 60).toString().padStart(2, "0");

    return `${hours}:${minutes}:${seconds}`;
}