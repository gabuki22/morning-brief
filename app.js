/* 모닝브리프 — 브라우저는 JSON 을 읽어 그리기만 한다. 계산은 tools/ 가 미리 끝냈다. */
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const WD = ["일", "월", "화", "수", "목", "금", "토"];
  const cache = {};

  async function getJSON(path) {
    if (cache[path]) return cache[path];
    const r = await fetch(path, { cache: "no-store" });
    if (!r.ok) throw new Error(`${path} ${r.status}`);
    return (cache[path] = await r.json());
  }

  function fmtDate(iso) {
    const d = new Date(iso + "T00:00:00+09:00");
    return `${d.getFullYear()}년 ${d.getMonth() + 1}월 ${d.getDate()}일 (${WD[d.getDay()]})`;
  }

  // 시계열 → 인라인 SVG. 축·격자 없음, 0 기준선만(음수 구간이 있을 때).
  function spark(series, series2) {
    const vals = series.map((p) => p[1]).concat(series2 ? series2.map((p) => p[1]) : []);
    const min = Math.min(...vals), max = Math.max(...vals), w = 220, h = 36, pad = 3;
    const x = (i, n) => pad + (i * (w - 2 * pad)) / Math.max(1, n - 1);
    const y = (v) => max === min ? h / 2 : h - pad - ((v - min) * (h - 2 * pad)) / (max - min);
    const path = (s) => s.map((p, i) => `${i ? "L" : "M"}${x(i, s.length).toFixed(1)},${y(p[1]).toFixed(1)}`).join(" ");
    const zero = min < 0 && max > 0 ? `<line x1="0" x2="${w}" y1="${y(0).toFixed(1)}" y2="${y(0).toFixed(1)}"/>` : "";
    return `<svg class="spark" viewBox="0 0 ${w} ${h}" aria-hidden="true">${zero}<path d="${path(series)}"/>${series2 ? `<path class="s2" d="${path(series2)}"/>` : ""}</svg>`;
  }

  function badge(it) {
    if (it.is_new) return `<span class="badge new">새로움</span>`;
    return `<span class="badge">${it.streak_days}일째</span>`;
  }

  function card(it, opts = {}) {
    const m = it.metrics || {};
    const sp = m.series ? spark(m.series, m.series2) : "";
    return `<article class="card">
      <a class="title" href="${esc(it.url)}" target="_blank" rel="noopener">${esc(it.title)}</a>
      <div class="body">${esc(it.summary)}</div>
      ${sp}
      <div class="meta"><span>${esc(it.published_at || "")}</span>${opts.noBadge ? "" : badge(it)}${(it.tags || []).map((t) => `<span class="badge">${esc(t)}</span>`).join("")}</div>
    </article>`;
  }

  function weatherStrip(mod) {
    const el = $("#weather-strip");
    const items = (mod.items || []).filter((it) => (it.tags || []).includes("집")).slice(0, 7);
    if (!items.length) { el.hidden = true; return; }
    el.innerHTML = items.map((it, i) => {
      const m = it.metrics || {}, d = new Date(it.published_at + "T00:00:00+09:00");
      return `<div class="wday${i === 0 ? " today" : ""}">
        <div class="d">${i === 0 ? "오늘" : WD[d.getDay()]} ${d.getMonth() + 1}/${d.getDate()}</div>
        <div class="l">${esc(m.label || "")}</div>
        <div class="t num">${Math.round(m.tmin)}~${Math.round(m.tmax)}°</div>
        <div class="p num">비 ${m.pop}%</div>
      </div>`;
    }).join("");
    el.hidden = false;
    const t = items[0].metrics || {};
    $("#headline").textContent = `오늘 ${t.label || ""} ${Math.round(t.tmin)}~${Math.round(t.tmax)}°, 강수확률 ${t.pop}%` + (t.pm25_max ? ` · PM2.5 최대 ${Math.round(t.pm25_max)}` : "");
  }

  function statusBar(index) {
    $("#status").innerHTML = Object.entries(index.modules).map(([m, s]) =>
      `<span><i class="dot ${s.level}"></i>${esc(m)} ${s.level === "off" ? "꺼짐" : `${s.count}건`}${s.warn && s.warn.length ? ` · ${esc(s.warn.join(", "))}` : ""}${s.block && s.block.length ? ` · ${esc(s.block.join(", "))}` : ""}</span>`
    ).join("") + `<span>빌드 ${esc((index.built_at || "").replace("T", " ").slice(0, 16))}</span>`;
  }

  async function showTab(module, label) {
    document.querySelectorAll(".tab").forEach((b) => b.setAttribute("aria-selected", b.dataset.module === module));
    const panel = $("#panel");
    try {
      const mod = await getJSON(`data/${module}.json`);
      const st = mod.status || {};
      const items = mod.items || [];
      const head = `<h2 class="sect">${esc(label)} <span class="num">${items.length}</span></h2>`;
      if (st.level === "block") { panel.innerHTML = head + `<div class="empty">수집 실패 — ${esc((st.block || []).join(", "))}</div>`; return; }
      const list = module === "weather" ? items.filter((it) => it.metrics && it.metrics.series) : items;   // 날씨는 오늘 카드 하나(스트립이 7일을 이미 보여줌)
      panel.innerHTML = head + `<div class="cards">${list.map((it) => card(it, { noBadge: module === "weather" || module === "fx" })).join("") || `<div class="empty">항목 없음</div>`}</div>`;
    } catch (e) {
      panel.innerHTML = `<div class="empty">아직 수집되지 않은 모듈입니다 (${esc(module)})</div>`;
    }
  }

  async function main() {
    const index = await getJSON("data/index.json");
    $("#daydate").textContent = fmtDate(index.date);
    statusBar(index);

    const tabs = (index.site && index.site.tabs) || [];
    const tabsEl = $("#tabs");
    tabsEl.innerHTML = tabs.map((t) => {
      const s = index.modules[t.module] || {};
      const off = s.level === "off" || s.level === undefined;
      return `<button class="tab${off ? " off" : ""}" data-module="${esc(t.module)}" data-label="${esc(t.label)}" ${off ? "disabled" : ""}>${esc(t.label)}</button>`;
    }).join("");
    tabsEl.addEventListener("click", (e) => {
      const b = e.target.closest(".tab"); if (b && !b.disabled) showTab(b.dataset.module, b.dataset.label);
    });

    if (index.modules.weather && index.modules.weather.level !== "off") {
      try { weatherStrip(await getJSON("data/weather.json")); } catch (_) { /* 스트립 없이도 화면은 산다 */ }
    }
    if (index.must_know && index.must_know.length) {
      $("#must-know-list").innerHTML = index.must_know.map((k) => `<li>${esc(k.why || "")}</li>`).join("");
      $("#must-know").hidden = false;
    }
    const first = tabs.find((t) => index.modules[t.module] && !["off"].includes(index.modules[t.module].level));
    if (first) showTab(first.module, first.label);
  }

  main().catch((e) => { $("#daydate").textContent = "데이터를 불러오지 못했습니다"; $("#panel").innerHTML = `<div class="empty">${esc(e.message)}</div>`; });
})();
