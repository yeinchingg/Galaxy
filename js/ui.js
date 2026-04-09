// // ── 輔助函數 ───────────────────────────────────────────────────────────
function setText(id, txt) {
  var el = document.getElementById(id);
  if (el) el.innerText = txt;
}

async function simulate() {
  const response = await fetch('http://localhost:5000/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      logM: P.logM,
      rd: P.rd,
      sfr: P.sfr
    })
  });
  const result = await response.json();
  updateReadout(result);
  if (typeof Galaxy !== 'undefined') {
    Galaxy.build(P, result);
  } 
  console.log("AI Data:", result); 
}
  
function updateReadout(ph) {
  // 只更新我們留下的核心 ID
  setText('r-mv', '10^' + P.logM.toFixed(1) + ' M☉');
  setText('r-rv', ph.Rv.toFixed(1));  //把半徑（Rv）四捨五入到小數點第一位，然後填進 id="r-rv" 的標籤裡。
  setText('r-vv', ph.V2.toFixed(1));
  setText('r-ms', '10^' + Math.log10(ph.Ms).toFixed(1) + ' M☉'); 
  
}

function initUI() {
  Object.keys(SCHEMA).forEach(function (key) {
    var el = document.getElementById(key);
    var valDisplay = document.getElementById('v-' + key);
    if (!el) return; 
    el.addEventListener('input', function () {
      var val = parseFloat(el.value);
      P[key] = val; 
      if (valDisplay) valDisplay.innerText = val; 
      simulate(); 
    });
  });
  simulate();
  }
window.addEventListener('DOMContentLoaded', initUI);
