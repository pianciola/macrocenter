(() => {
  'use strict';
  const symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'DOGEUSDT'];
  function parseTicker(raw, symbol, now, previous = 0) {
    if (!raw || raw.e !== '24hrTicker' || raw.s !== symbol) return null;
    const keys = ['E', 'c', 'P', 'b', 'a', 'h', 'l', 'q'];
    if (keys.some(k => raw[k] === null || raw[k] === '' || raw[k] === undefined)) return null;
    const v = Object.fromEntries(keys.map(k => [k, Number(raw[k])]));
    if (Object.values(v).some(n => !Number.isFinite(n))) return null;
    if (v.E <= previous || now - v.E > 15000 || v.E - now > 60000) return null;
    if (v.c <= 0 || v.b <= 0 || v.a < v.b || v.l <= 0 || v.h < v.l || v.q < 0) return null;
    return v;
  }
  if (typeof module !== 'undefined' && module.exports) { module.exports = {parseTicker}; return; }
  const $ = id => document.getElementById(id);
  let socket, retry, generation = 0, stopped = false, failures = 0, received = 0, eventTime = 0;
  let points = [], selected = $('symbol').value, started = 0;
  const number = (n, digits = 2) => n.toLocaleString('es-AR', {maximumFractionDigits:digits});
  const time = t => new Date(t).toLocaleTimeString('es-AR', {timeZone:'America/Argentina/Buenos_Aires'});
  function status(text, live = false) { $('status').textContent = text; $('status').dataset.live = String(live); }
  function close() { clearTimeout(retry); generation++; if (socket) { socket.onclose = null; socket.close(); socket = null; } }
  function schedule() {
    if (stopped || document.hidden) return;
    status('Sin conexión · reintentando…');
    retry = setTimeout(connect, Math.min(30000, 1000 * 2 ** Math.min(failures++, 5)));
  }
  function connect() {
    close();
    if (stopped || document.hidden) return;
    const current = generation;
    started = Date.now(); received = 0;
    status('Conectando…');
    try { socket = new WebSocket('wss://data-stream.binance.vision/ws/' + selected.toLowerCase() + '@ticker'); }
    catch (_) { schedule(); return; }
    socket.onmessage = ev => {
      if (current !== generation) return;
      let raw; try { raw = JSON.parse(ev.data); } catch (_) { return; }
      const v = parseTicker(raw, selected, Date.now(), eventTime);
      if (!v) return;
      received = Date.now(); eventTime = v.E; failures = 0;
      status('● En vivo', true);
      const digits = v.c >= 1 ? 2 : 6;
      for (const [id, value] of [['price', v.c], ['bid', v.b], ['ask', v.a]]) $(id).textContent = number(value, digits);
      $('change').textContent = (v.P > 0 ? '+' : '') + number(v.P) + '%';
      $('change').className = v.P >= 0 ? 'up' : 'down';
      $('range').textContent = number(v.h, digits) + ' / ' + number(v.l, digits);
      $('volume').textContent = number(v.q, 0);
      $('time').textContent = time(v.E) + ' · Argentina';
      points.push([v.E, v.c]); points = points.filter(p => v.E - p[0] <= 180000).slice(-180);
      const low = Math.min(...points.map(p => p[1])), high = Math.max(...points.map(p => p[1]));
      const span = Math.max(1, v.E - points[0][0]);
      const path = points.map((p,i) => (i && p[0] - points[i-1][0] < 5000 ? 'L' : 'M') + (5 + (p[0] - points[0][0]) / span * 590).toFixed(2) + ',' + (high === low ? 75 : 140 - (p[1] - low) / (high - low) * 130).toFixed(2)).join(' ');
      $('line').setAttribute('d', path);
      $('chart-note').textContent = points.length > 1 ? time(points[0][0]) + ' — ' + time(v.E) : 'Esperando el siguiente precio…';
    };
    socket.onerror = () => { if (current === generation) status('Sin conexión · reintentando…'); };
    socket.onclose = () => { if (current === generation) schedule(); };
  }
  $('symbol').addEventListener('change', () => {
    if (!symbols.includes($('symbol').value)) return;
    selected = $('symbol').value; points = []; eventTime = 0; failures = 0;
    for (const id of ['price', 'change', 'bid', 'ask', 'range', 'volume']) $(id).textContent = '—';
    $('line').setAttribute('d', ''); $('time').textContent = 'Sin datos recibidos';
    $('chart-note').textContent = 'Esperando precios para dibujar…'; connect();
  });
  const watchdog = setInterval(() => {
    if (stopped || document.hidden) return;
    const age = Date.now() - (received || started);
    if (received && age > 10000) status('Sin datos recientes · último precio conservado');
    if (socket && age > 30000) { close(); schedule(); }
  }, 1000);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) { close(); status('Pausado · pestaña en segundo plano'); }
    else connect();
  });
  window.addEventListener('pagehide', () => { stopped = true; close(); clearInterval(watchdog); });
  connect();
})();
