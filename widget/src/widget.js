import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import xtermCss from '@xterm/xterm/css/xterm.css';

if (!document.getElementById('tps-xterm-css')) {
  const s = document.createElement('style');
  s.id = 'tps-xterm-css';
  s.textContent = xtermCss;
  document.head.appendChild(s);
}

// ---------------------------------------------------------------------------
// Bootstrap: mount all <script data-pack="..."> widgets on the page
// ---------------------------------------------------------------------------

function bootstrap() {
  const tags = document.querySelectorAll('script[data-pack]');
  tags.forEach(function (scriptTag) {
    if (scriptTag._tpsMounted) return;
    scriptTag._tpsMounted = true;

    const pack     = scriptTag.dataset.pack;
    const exercise = scriptTag.dataset.exercise || null;
    const tpsUrl   = (scriptTag.dataset.tpsUrl || '').replace(/\/$/, '') || location.origin.replace(/\/$/, '');

    if (!pack) {
      console.error('[TPS Widget] data-pack attribute is required.');
      return;
    }

    const container = document.createElement('div');
    scriptTag.parentNode.insertBefore(container, scriptTag.nextSibling);
    mount(container, { pack, exercise, tpsUrl });
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootstrap);
} else {
  bootstrap();
}

// ---------------------------------------------------------------------------
// State machine
// ---------------------------------------------------------------------------

// States: idle | loading | connected | no_capacity | error | terminated

function mount(root, { pack, exercise, tpsUrl }) {
  let state = 'idle';
  let sessionToken = null;
  let ws = null;
  let term = null;
  let fitAddon = null;

  // -- DOM ------------------------------------------------------------------

  root.style.cssText = 'font-family: monospace; max-width: 900px;';

  const msgEl = document.createElement('div');
  msgEl.style.cssText = 'margin-bottom: 8px; color: #d32f2f; min-height: 20px;';
  root.appendChild(msgEl);

  const btnEl = document.createElement('button');
  btnEl.style.cssText = [
    'padding: 8px 20px',
    'font-size: 14px',
    'cursor: pointer',
    'border: 1px solid #555',
    'border-radius: 4px',
    'background: #1565c0',
    'color: #fff',
  ].join(';');
  root.appendChild(btnEl);

  const termWrap = document.createElement('div');
  termWrap.style.cssText = [
    'display: none',
    'margin-top: 12px',
    'background: #1e1e1e',
    'border-radius: 4px',
    'padding: 4px',
    'height: 420px',
  ].join(';');
  root.appendChild(termWrap);

  // -- Render ---------------------------------------------------------------

  function render() {
    msgEl.textContent = '';
    termWrap.style.display = 'none';

    switch (state) {
      case 'idle':
        btnEl.textContent = 'Launch Terminal';
        btnEl.disabled = false;
        break;

      case 'loading':
        btnEl.textContent = 'Connecting…';
        btnEl.disabled = true;
        break;

      case 'connected':
        btnEl.textContent = 'Terminate Session';
        btnEl.disabled = false;
        termWrap.style.display = 'block';
        if (fitAddon) requestAnimationFrame(() => fitAddon.fit());
        break;

      case 'no_capacity':
        btnEl.textContent = 'Launch Terminal';
        btnEl.disabled = false;
        msgEl.textContent = 'No free containers available. Please try again later.';
        break;

      case 'error':
        btnEl.textContent = 'Retry';
        btnEl.disabled = false;
        msgEl.textContent = 'Connection error. Please try again.';
        break;

      case 'terminated':
        btnEl.textContent = 'Launch Terminal';
        btnEl.disabled = false;
        msgEl.textContent = 'Session ended.';
        destroyTerminal();
        break;
    }
  }

  function transition(newState) {
    state = newState;
    render();
  }

  render();

  // -- Button ---------------------------------------------------------------

  btnEl.addEventListener('click', () => {
    if (state === 'idle' || state === 'no_capacity' || state === 'error' || state === 'terminated') {
      msgEl.textContent = '';
      transition('loading');
      requestSession();
    } else if (state === 'connected') {
      terminate();
    }
  });

  // -- Session lifecycle ----------------------------------------------------

  async function requestSession() {
    try {
      const body = { pack_id: pack };
      if (exercise) body.exercise_id = exercise;

      const resp = await fetch(`${tpsUrl}/api/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (resp.status === 503) {
        transition('no_capacity');
        return;
      }

      if (!resp.ok) {
        console.error('[TPS Widget] Unexpected response:', resp.status);
        transition('error');
        return;
      }

      const data = await resp.json();
      sessionToken = data.session_token;
      connect(data.ws_url);

    } catch (err) {
      console.error('[TPS Widget] requestSession error:', err);
      transition('error');
    }
  }

  async function terminate() {
    if (!sessionToken) return;
    const token = sessionToken;
    sessionToken = null;

    closeWs();
    transition('terminated');

    try {
      await fetch(`${tpsUrl}/api/sessions/${token}`, { method: 'DELETE' });
    } catch (err) {
      console.warn('[TPS Widget] terminate fetch error (ignored):', err);
    }
  }

  function terminateBeforeUnload() {
    if (!sessionToken) return;
    const token = sessionToken;
    sessionToken = null;
    closeWs();
    // sendBeacon for reliable delivery during page unload
    fetch(`${tpsUrl}/api/sessions/${token}`, { method: 'DELETE', keepalive: true });
  }

  window.addEventListener('beforeunload', terminateBeforeUnload);

  // -- WebSocket + xterm.js -------------------------------------------------

  function connect(wsPath) {
    const proto   = location.protocol === 'https:' ? 'wss' : 'ws';
    const wsBase  = tpsUrl.replace(/^https?/, proto);
    const wsUrl   = `${wsBase}${wsPath}`;

    initTerminal();

    ws = new WebSocket(wsUrl);
    ws.binaryType = 'arraybuffer';

    ws.onopen = () => {
      transition('connected');
      sendResize();
    };

    ws.onmessage = (ev) => {
      if (!term) return;
      if (ev.data instanceof ArrayBuffer) {
        term.write(new Uint8Array(ev.data));
      } else {
        term.write(ev.data);
      }
    };

    ws.onclose = () => {
      if (state === 'connected') {
        transition('terminated');
      }
    };

    ws.onerror = (err) => {
      console.error('[TPS Widget] WebSocket error:', err);
      if (state === 'loading') {
        transition('error');
      }
    };
  }

  function closeWs() {
    if (ws) {
      ws.onclose = null;
      ws.close();
      ws = null;
    }
  }

  function initTerminal() {
    destroyTerminal();
    term = new Terminal({ cursorBlink: true, theme: { background: '#1e1e1e' } });
    fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    term.open(termWrap);

    term.onData((data) => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(new TextEncoder().encode(data));
      }
    });

    term.onResize(() => sendResize());
    window.addEventListener('resize', onWindowResize);
  }

  function destroyTerminal() {
    window.removeEventListener('resize', onWindowResize);
    if (term) {
      term.dispose();
      term = null;
    }
    fitAddon = null;
    termWrap.innerHTML = '';
  }

  function onWindowResize() {
    if (fitAddon) fitAddon.fit();
  }

  function sendResize() {
    if (!ws || ws.readyState !== WebSocket.OPEN || !term) return;
    const msg = JSON.stringify({ type: 'resize', cols: term.cols, rows: term.rows });
    ws.send(new TextEncoder().encode(msg));
  }
}
