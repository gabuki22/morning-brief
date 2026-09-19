/* 모닝브리프 — 브라우저는 JSON 을 읽어 그리기만 한다. 계산은 tools/ 가 미리 끝냈다. */
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const WD = ["일", "월", "화", "수", "목", "금", "토"];
  const cache = {};
  let current = { module: null, label: "", tag: null };

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
  function shortTime(iso) {
    if (!iso) return "";
    const m = /^(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2}))?/.exec(iso);
    return m ? `${+m[2]}/${+m[3]}${m[4] ? " " + m[4] + ":" + m[5] : ""}` : iso;
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

  const badge = (it) => it.is_new ? `<span class="badge new">새로움</span>` : `<span class="badge">${it.streak_days}일째</span>`;
  const chg = (v) => v == null ? "" : `<span class="chg ${v > 0 ? "up" : v < 0 ? "down" : ""}">${v > 0 ? "+" : ""}${Number(v).toFixed(2)}%</span>`;

  function card(it, opts = {}) {
    const m = it.metrics || {};
    const sp = m.series ? spark(m.series, m.series2) : "";
    const head = m.chg_1d != null ? `<div class="kv num">${chg(m.chg_1d)}${m.chg_7d != null ? ` <span class="dim">7일 ${chg(m.chg_7d)}</span>` : ""}${m.chg_period != null ? ` <span class="dim">기간 ${chg(m.chg_period)}</span>` : ""}</div>` : "";
    const news = (m.news || []).map((n) => `<div class="sub"><a href="${esc(n.url)}" target="_blank" rel="noopener">${esc(n.title)}</a></div>`).join("");
    return `<article class="card">
      <a class="title" href="${esc(it.url)}" target="_blank" rel="noopener">${esc(it.title)}</a>
      ${head}
      <div class="body">${esc(it.summary)}</div>
      ${sp}${news}
      <div class="meta">${it.source_name ? `<span class="src">${esc(it.source_name)}</span>` : ""}<span>${esc(shortTime(it.published_at))}</span>${m.outlets > 1 ? `<span class="badge">매체 ${m.outlets}곳</span>` : ""}${opts.noBadge ? "" : badge(it)}${(it.tags || []).slice(0, 4).map((t) => `<span class="badge tag" data-tag="${esc(t)}">${esc(t)}</span>`).join("")}</div>
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
      `<span><i class="dot ${s.level}"></i>${esc(m)} ${s.level === "off" ? "준비 중" : `${s.count}건`}${s.warn && s.warn.length ? ` · ${esc(s.warn.join(", "))}` : ""}${s.block && s.block.length ? ` · ${esc(s.block.join(", "))}` : ""}</span>`
    ).join("") + `<span>빌드 ${esc((index.built_at || "").replace("T", " ").slice(0, 16))}</span>`;
  }

  function chips(items) {
    const freq = {};
    items.forEach((it) => (it.tags || []).forEach((t) => { freq[t] = (freq[t] || 0) + 1; }));
    const top = Object.entries(freq).sort((a, b) => b[1] - a[1]).slice(0, 8);
    if (top.length < 2) return "";
    return `<div class="chips"><button class="chip${current.tag ? "" : " on"}" data-tag="">전체 ${items.length}</button>` +
      top.map(([t, n]) => `<button class="chip${current.tag === t ? " on" : ""}" data-tag="${esc(t)}">${esc(t)} ${n}</button>`).join("") + `</div>`;
  }

  function cardsHtml(items) {
    const list = current.tag ? items.filter((it) => (it.tags || []).includes(current.tag)) : items;
    const noBadge = ["weather", "fx", "markets", "crypto", "publicdata"].includes(current.module);
    return list.map((it) => card(it, { noBadge })).join("") || `<div class="empty">항목 없음</div>`;
  }

  function renderPanel(mod) {
    const panel = $("#panel");
    const st = mod.status || {};
    let items = mod.items || [];
    const head = `<h2 class="sect">${esc(current.label)} <span class="num">${items.length}</span></h2>`;
    if (st.level === "block") { panel.innerHTML = head + `<div class="empty">수집 실패 — ${esc((st.block || []).join(", "))}</div>`; return; }
    if (current.module === "weather") items = items.filter((it) => it.metrics && it.metrics.series);   // 스트립이 7일을 이미 보여준다
    panel.innerHTML = head + (items.length > 12 ? chips(items) : "") + `<div class="cards" id="cards">${cardsHtml(items)}</div>`;
    // 칩을 누르면 칩 줄은 그대로 두고 카드만 다시 그린다 — 줄이 다시 그려지면 누른 자리가 사라진다
    panel.querySelectorAll(".chip").forEach((b) => b.addEventListener("click", () => {
      current.tag = b.dataset.tag || null;
      panel.querySelectorAll(".chip").forEach((c) => c.classList.toggle("on", (c.dataset.tag || null) === current.tag));
      $("#cards").innerHTML = cardsHtml(items);
    }));
  }

  // 큰 탭이 몇 줄로 접히든 칩 줄이 그 바로 아래에 붙도록 높이를 CSS 변수로 넘긴다
  function syncSticky() {
    const t = $("#tabs");
    if (t) document.documentElement.style.setProperty("--tabs-h", `${t.offsetHeight}px`);
  }
  window.addEventListener("resize", syncSticky);

  async function showTab(module, label) {
    document.querySelectorAll(".tab").forEach((b) => b.setAttribute("aria-selected", b.dataset.module === module));
    current = { module, label, tag: null };
    try {
      renderPanel(await getJSON(`data/${module}.json`));
    } catch (e) {
      $("#panel").innerHTML = `<div class="empty">아직 수집되지 않은 모듈입니다 (${esc(module)})</div>`;
    }
    syncSticky();
    // 아래쪽에서 탭을 바꿨으면 새 목록의 첫 카드가 탭 바로 아래 오게 (탭은 상단 고정)
    const tabsEl = $("#tabs");
    const top = tabsEl.getBoundingClientRect().top + window.scrollY;
    if (window.scrollY > top) window.scrollTo({ top, behavior: "auto" });
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
    syncSticky();

    if (index.modules.weather && index.modules.weather.level !== "off") {
      try { weatherStrip(await getJSON("data/weather.json")); } catch (_) { /* 스트립 없이도 화면은 산다 */ }
    }
    if (index.must_know && index.must_know.length) {
      $("#must-know-list").innerHTML = index.must_know.map((k) =>
        `<li><a class="it-title" href="${esc(k.url)}" target="_blank" rel="noopener">${esc(k.title)}</a><div class="it-body">${esc(k.why || "")}</div></li>`).join("");
      $("#must-know").hidden = false;
    }
    const first = tabs.find((t) => index.modules[t.module] && index.modules[t.module].level !== "off");
    if (first) showTab(first.module, first.label);
  }

  main().catch((e) => { $("#daydate").textContent = "데이터를 불러오지 못했습니다"; $("#panel").innerHTML = `<div class="empty">${esc(e.message)}</div>`; });
})();
