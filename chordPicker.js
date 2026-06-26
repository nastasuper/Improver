// ── Chord Picker Component ──────────────────────────────────────────────────
// Uso: ChordPicker.init(); ChordPicker.open(); ChordPicker.onDone(callback)

const ChordPicker = (() => {
  const NOTES = ['C','Db','D','Eb','E','F','F#','G','Ab','A','Bb','B'];
  const TYPES = ['maj7','m7','7','m7b5','dim','6','m6','9','7b9','7alt','sus4','aug'];

  let _onDone = null;
  let selectedNote = null;
  let selectedType = null;
  let tokens = [];
  let flipped = false;
  let initialized = false;

  function _buildHTML() {
    const notes = NOTES.map(n =>
      `<div class="note-btn" data-note="${n}">${n}</div>`
    ).join('');
    const types = TYPES.map(t =>
      `<div class="type-btn" data-type="${t}">${t}</div>`
    ).join('');

    return `
    <div>
      <div class="built-label">Progresión</div>
      <div class="built-row" id="cp-built-row">
        <span class="built-empty">Tocá una nota para empezar…</span>
      </div>
    </div>
    <div class="divider"></div>
    <div class="card-area">
      <div class="card-3d">
        <div class="card card-empty" id="cp-main-card">
          <div class="card-face front">
            <span class="card-note" id="cp-front-note">?</span>
            <span class="card-type" id="cp-front-type">nota</span>
          </div>
          <div class="card-face back">
            <span class="card-note" id="cp-back-note">?</span>
            <span class="card-type" id="cp-back-type">tipo</span>
          </div>
        </div>
      </div>
    </div>
    <div class="divider"></div>
    <div>
      <div class="section-label">Nota</div>
      <div class="notes-grid">${notes}</div>
    </div>
    <div>
      <div class="section-label">Tipo</div>
      <div class="types-grid">${types}</div>
    </div>
    <div class="divider"></div>
    <div class="actions">
      <div class="act-btn act-sep" id="cp-act-sep">/ Compás</div>
      <div class="act-btn" id="cp-act-add" style="opacity:0.35;pointer-events:none;">+ Agregar</div>
      <div class="act-btn act-del" id="cp-act-del">⌫ Borrar</div>
      <div class="act-btn act-done" id="cp-act-done">✓ Listo</div>
    </div>`;
  }

  function _selectNote(note) {
    selectedNote = note;
    selectedType = null;
    document.querySelectorAll('#cp-root .note-btn').forEach(b =>
      b.classList.toggle('selected', b.dataset.note === note)
    );
    document.querySelectorAll('#cp-root .type-btn').forEach(b =>
      b.classList.remove('selected')
    );
    const card = document.getElementById('cp-main-card');
    card.classList.remove('card-empty');
    flipped = !flipped;
    card.classList.toggle('flipped', flipped);
    const nEl = flipped ? 'cp-back-note' : 'cp-front-note';
    const tEl = flipped ? 'cp-back-type' : 'cp-front-type';
    document.getElementById(nEl).textContent = note;
    document.getElementById(tEl).textContent = 'tipo…';
    const addBtn = document.getElementById('cp-act-add');
    addBtn.style.opacity = '1';
    addBtn.style.pointerEvents = 'auto';
  }

  function _selectType(type) {
    if (!selectedNote) return;
    selectedType = type;
    document.querySelectorAll('#cp-root .type-btn').forEach(b =>
      b.classList.toggle('selected', b.dataset.type === type)
    );
    flipped = !flipped;
    const card = document.getElementById('cp-main-card');
    card.classList.toggle('flipped', flipped);
    const nEl = flipped ? 'cp-back-note' : 'cp-front-note';
    const tEl = flipped ? 'cp-back-type' : 'cp-front-type';
    document.getElementById(nEl).textContent = selectedNote;
    document.getElementById(tEl).textContent = type;
  }

  function _addCurrent() {
    if (!selectedNote) return;
    tokens.push(selectedNote + (selectedType || ''));
    selectedNote = null; selectedType = null;
    document.querySelectorAll('#cp-root .note-btn, #cp-root .type-btn').forEach(b =>
      b.classList.remove('selected')
    );
    const card = document.getElementById('cp-main-card');
    card.classList.add('card-empty');
    flipped = false;
    card.classList.remove('flipped');
    ['cp-front-note','cp-back-note'].forEach(id =>
      document.getElementById(id).textContent = '?'
    );
    ['cp-front-type','cp-back-type'].forEach(id =>
      document.getElementById(id).textContent = 'nota'
    );
    const addBtn = document.getElementById('cp-act-add');
    addBtn.style.opacity = '0.35';
    addBtn.style.pointerEvents = 'none';
    _renderBuilt();
  }

  function _addSep() {
    if (tokens.length && tokens[tokens.length - 1] !== '|') {
      tokens.push('|');
      _renderBuilt();
    }
  }

  function _deleteLast() {
    if (!tokens.length) return;
    tokens.pop();
    if (tokens.length && tokens[tokens.length - 1] === '|') tokens.pop();
    _renderBuilt();
  }

  function _renderBuilt() {
    const row = document.getElementById('cp-built-row');
    if (!tokens.length) {
      row.innerHTML = '<span class="built-empty">Tocá una nota para empezar…</span>';
      return;
    }
    row.innerHTML = tokens.map(t =>
      t === '|'
        ? '<span class="built-sep">/</span>'
        : `<span class="built-tile">${t}</span>`
    ).join('');
    row.scrollLeft = row.scrollWidth;
  }

  function _buildResult() {
    const bars = []; let bar = [];
    tokens.forEach(t => {
      if (t === '|') { if (bar.length) { bars.push(bar.join(' ')); bar = []; } }
      else bar.push(t);
    });
    if (bar.length) bars.push(bar.join(' '));
    return bars.join(' / ');
  }

  function _bindEvents() {
    document.querySelectorAll('#cp-root .note-btn').forEach(btn =>
      btn.addEventListener('click', () => _selectNote(btn.dataset.note))
    );
    document.querySelectorAll('#cp-root .type-btn').forEach(btn =>
      btn.addEventListener('click', () => _selectType(btn.dataset.type))
    );
    document.getElementById('cp-act-add').addEventListener('click', _addCurrent);
    document.getElementById('cp-act-sep').addEventListener('click', _addSep);
    document.getElementById('cp-act-del').addEventListener('click', _deleteLast);
    document.getElementById('cp-act-done').addEventListener('click', () => {
      const prog = _buildResult();
      if (_onDone) _onDone(prog);
    });
  }

  // ── API pública ────────────────────────────────────────────────────────────
  return {
    init() {
      if (initialized) return;
      let root = document.getElementById('cp-root');
      if (!root) {
        root = document.createElement('div');
        root.id = 'cp-root';
        // Insertar antes del textarea
        const textarea = document.querySelector('.textarea-row');
        textarea.parentNode.insertBefore(root, textarea);
      }
      root.innerHTML = _buildHTML();
      _bindEvents();
      initialized = true;
    },

    open(currentProg) {
      // Cargar progresión existente
      tokens = [];
      if (currentProg && currentProg.trim()) {
        currentProg.trim().split(/\s*\/\s*/).forEach((bar, i) => {
          if (i > 0) tokens.push('|');
          bar.trim().split(/\s+/).forEach(t => { if (t) tokens.push(t); });
        });
      }
      _renderBuilt();
      // Reset carta
      const card = document.getElementById('cp-main-card');
      if (card) { card.classList.add('card-empty'); card.classList.remove('flipped'); }
      flipped = false;
      document.querySelectorAll('#cp-root .note-btn, #cp-root .type-btn').forEach(b =>
        b.classList.remove('selected')
      );
      const addBtn = document.getElementById('cp-act-add');
      if (addBtn) { addBtn.style.opacity = '0.35'; addBtn.style.pointerEvents = 'none'; }
      document.getElementById('cp-root').classList.add('cp-active');
      document.querySelector('.textarea-row').style.display = 'none';
    },

    close() {
      const root = document.getElementById('cp-root');
      if (root) root.classList.remove('cp-active');
      document.querySelector('.textarea-row').style.display = '';
    },

    onDone(callback) {
      _onDone = callback;
    }
  };
})();
