// Prep — Study Page Logic
// Fetches cards from Django API, handles flip, TTS, swipe, rating

(function () {
  'use strict';

  // ── State ──────────────────────────────
  let allCards = [];
  let filteredCards = [];
  let currentIndex = 0;
  let isFlipped = false;
  let activeCategory = 'all';
  let activeSections = [];
  let studyMode = 'all';
  let settings = { darkMode: localStorage.getItem('prep_dark') === '1', audioEnabled: false, speechRate: 1.0 };
  let session = { studied: new Set(), correct: 0, total: 0 };
  let touchStartX = 0;
  let touchStartY = 0;
  let isSwiping = false;

  // ── DOM ────────────────────────────────
  const $ = id => document.getElementById(id);
  const flashcard = $('flashcard');
  const cardContainer = $('card-container');
  const cardQuestion = $('card-question');
  const cardAnswer = $('card-answer');
  const cardRationale = $('card-rationale');
  const cardCategory = $('card-category');
  const cardCategoryBack = $('card-category-back');
  const ratingBar = $('rating-bar');
  const progressFill = $('progress-fill');
  const progressText = $('progress-text');
  const emptyState = $('empty-state');
  const cardCount = $('card-count');
  const statsModal = $('stats-modal');
  const statsBody = $('stats-body');

  // ── Init ───────────────────────────────
  const urlParams = new URLSearchParams(window.location.search);
  const initCategory = urlParams.get('category') || 'all';
  const initDeck = urlParams.get('deck') || '';
  const initSection = urlParams.get('section') || '';
  const initMode = urlParams.get('mode') || '';

  async function init() {
    applyTheme();
    if (initCategory && initCategory !== 'all') {
      activeCategory = initCategory;
    }
    if (initSection) {
      activeSections = [initSection];
    }
    if (initMode) {
      studyMode = initMode;
      const modeSelect = $('study-mode');
      if (modeSelect) modeSelect.value = initMode;
    }
    await fetchCards(activeCategory);
    filterCards();
    showCard();
    updateSessionStats();
    setupEventListeners();
    setupTouchGestures();
    setupKeyboard();
    registerServiceWorker();
  }

  // ── Fetch Cards from API ───────────────
  async function fetchCards(category) {
    try {
      const params = new URLSearchParams();
      if (category && category !== 'all') params.set('category', category);
      if (initDeck) params.set('deck', initDeck);
      const sections = activeSections.length ? activeSections : (initSection ? [initSection] : []);
      if (sections.length) params.set('section', sections.join(','));
      const qs = params.toString();
      const url = qs ? `${API_CARDS_URL}?${qs}` : API_CARDS_URL;
      const res = await fetch(url);
      const data = await res.json();
      allCards = data.cards;
    } catch (e) {
      console.error('Failed to fetch cards:', e);
    }
  }

  // ── Filtering ──────────────────────────
  function filterCards() {
    let cards = [...allCards];
    const today = new Date().toISOString().split('T')[0];

    switch (studyMode) {
      case 'new':
        cards = cards.filter(c => !c.progress || c.progress.timesStudied === 0);
        break;
      case 'weak':
        cards = cards.filter(c => c.progress && c.progress.lastRating <= 3 && c.progress.timesStudied > 0);
        break;
      case 'due':
        cards = cards.filter(c => {
          const p = c.progress;
          return !p || !p.nextReview || p.nextReview <= today;
        });
        break;
      case 'shuffle':
        shuffleArray(cards);
        break;
    }

    filteredCards = cards;
    currentIndex = 0;
    isFlipped = false;
    cardCount.textContent = `${cards.length} card${cards.length !== 1 ? 's' : ''}`;
  }

  function shuffleArray(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
  }

  // ── Card Display ───────────────────────
  function showCard(direction) {
    if (filteredCards.length === 0) {
      cardContainer.style.display = 'none';
      emptyState.style.display = 'block';
      ratingBar.classList.remove('visible');
      progressFill.style.width = '0%';
      progressText.textContent = '0 / 0';
      return;
    }

    cardContainer.style.display = 'block';
    emptyState.style.display = 'none';

    if (direction) {
      const exitClass = direction === 'next' ? 'swipe-left' : 'swipe-right';
      const enterClass = direction === 'next' ? 'enter-right' : 'enter-left';
      cardContainer.classList.add(exitClass);
      setTimeout(() => {
        cardContainer.classList.remove(exitClass);
        renderCard();
        cardContainer.classList.add(enterClass);
        setTimeout(() => cardContainer.classList.remove(enterClass), 350);
      }, 300);
    } else {
      renderCard();
    }
  }

  function renderCard() {
    const card = filteredCards[currentIndex];
    if (!card) return;

    isFlipped = false;
    flashcard.classList.remove('flipped');
    ratingBar.classList.remove('visible');

    cardCategory.innerHTML = '<i class="' + (card.categoryIcon || '') + '"></i> ' + card.categoryLabel;
    cardCategoryBack.innerHTML = '<i class="' + (card.categoryIcon || '') + '"></i> ' + card.categoryLabel;
    cardQuestion.textContent = card.question;
    cardAnswer.textContent = card.answer;
    cardRationale.textContent = card.rationale ? card.rationale : '';

    const pct = filteredCards.length > 0
      ? ((currentIndex + 1) / filteredCards.length * 100).toFixed(0)
      : 0;
    progressFill.style.width = `${pct}%`;
    progressText.textContent = `${currentIndex + 1} / ${filteredCards.length}`;

    if (settings.audioEnabled) speak(card.question);
  }

  function flipCard() {
    if (filteredCards.length === 0) return;
    isFlipped = !isFlipped;
    flashcard.classList.toggle('flipped', isFlipped);
    ratingBar.classList.toggle('visible', isFlipped);
    if (isFlipped && settings.audioEnabled) {
      speak(filteredCards[currentIndex].answer);
    }
  }

  function nextCard() {
    if (filteredCards.length === 0) return;
    currentIndex = (currentIndex + 1) % filteredCards.length;
    showCard('next');
  }

  function prevCard() {
    if (filteredCards.length === 0) return;
    currentIndex = (currentIndex - 1 + filteredCards.length) % filteredCards.length;
    showCard('prev');
  }

  // ── Rating (calls Django API) ──────────
  async function rateCard(rating) {
    const card = filteredCards[currentIndex];
    if (!card) return;

    try {
      const url = RATE_URL_TEMPLATE.replace('{id}', card.id);
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': CSRF_TOKEN,
        },
        body: JSON.stringify({ rating }),
      });
      const data = await res.json();
      if (data.ok) {
        card.progress = data.progress;
      }
    } catch (e) {
      console.error('Failed to rate card:', e);
    }

    session.studied.add(card.id);
    session.total++;
    if (rating >= 3) session.correct++;
    updateSessionStats();

    setTimeout(() => nextCard(), 400);
  }

  // ── Audio / TTS ────────────────────────
  function speak(text) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.rate = settings.speechRate;
    u.lang = 'en-US';
    const voices = window.speechSynthesis.getVoices();
    const v = voices.find(v => v.name.includes('Samantha'))
      || voices.find(v => v.lang === 'en-US' && v.localService)
      || voices.find(v => v.lang.startsWith('en'));
    if (v) u.voice = v;
    window.speechSynthesis.speak(u);
  }

  function toggleAudio() {
    settings.audioEnabled = !settings.audioEnabled;
    const btn = $('btn-audio');
    var ai = document.getElementById('audio-icon');
    if (ai) ai.className = settings.audioEnabled ? 'ph-bold ph-speaker-high' : 'ph-bold ph-speaker-slash';
    btn.classList.toggle('audio-active', settings.audioEnabled);
    if (settings.audioEnabled && filteredCards.length > 0) {
      const card = filteredCards[currentIndex];
      speak(isFlipped ? card.answer : card.question);
    } else {
      window.speechSynthesis?.cancel();
    }
  }

  function speakCurrent() {
    if (filteredCards.length === 0) return;
    const btn = $('btn-speak');
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      if (btn) btn.innerHTML = '<i class="ph-bold ph-speaker-high"></i> Read';
      return;
    }
    const card = filteredCards[currentIndex];
    const text = isFlipped ? `${card.answer}. ${card.rationale}` : card.question;
    if (btn) btn.innerHTML = '<i class="ph-bold ph-stop"></i> Stop';
    const u = new SpeechSynthesisUtterance(text);
    u.rate = settings.speechRate;
    u.lang = 'en-US';
    const voices = window.speechSynthesis.getVoices();
    const v = voices.find(v => v.name.includes('Samantha'))
      || voices.find(v => v.lang === 'en-US' && v.localService)
      || voices.find(v => v.lang.startsWith('en'));
    if (v) u.voice = v;
    u.onend = function() { if (btn) btn.innerHTML = '<i class="ph-bold ph-speaker-high"></i> Read'; };
    u.onerror = function() { if (btn) btn.innerHTML = '<i class="ph-bold ph-speaker-high"></i> Read'; };
    window.speechSynthesis.speak(u);
  }

  // ── Dark Mode ──────────────────────────
  function toggleDarkMode() {
    settings.darkMode = !settings.darkMode;
    localStorage.setItem('prep_dark', settings.darkMode ? '1' : '0');
    applyTheme();
  }

  function applyTheme() {
    document.documentElement.setAttribute('data-theme', settings.darkMode ? 'dark' : 'light');
    const btn = $('btn-dark-mode');
    var di = document.getElementById('dark-icon'); if(di) di.className = settings.darkMode ? 'ph-bold ph-moon' : 'ph-bold ph-sun';
    document.querySelector('meta[name="theme-color"]')
      ?.setAttribute('content', settings.darkMode ? '#0f172a' : '#0d9488');
  }

  // ── Session Stats (removed from UI) ────
  function updateSessionStats() {}

  // ── Stats Modal (fetches from API) ─────
  async function showStatsModal() {
    try {
      const res = await fetch(API_STATS_URL);
      const data = await res.json();

      $('stat-streak').innerHTML = '<i class="ph-bold ph-flame"></i> ' + data.streak;

      let html = `
        <div class="stat-grid">
          <div class="stat-card"><div class="stat-big">${data.studied}/${data.totalCards}</div><div class="stat-desc">Cards Studied</div></div>
          <div class="stat-card"><div class="stat-big">${data.mastered}</div><div class="stat-desc">Mastered</div></div>
          <div class="stat-card"><div class="stat-big">${data.weak}</div><div class="stat-desc">Need Work</div></div>
          <div class="stat-card"><div class="stat-big">${data.streak}</div><div class="stat-desc">Day Streak</div></div>
        </div>
        <h3 style="font-size:15px;margin-bottom:8px;">By Category</h3>
        <div class="category-stats">
      `;

      for (const cat of data.categories) {
        html += `
          <div class="category-stat-row">
            <span class="category-stat-name">${cat.name}</span>
            <div class="category-stat-bar">
              <div class="mini-bar"><div class="mini-bar-fill" style="width:${cat.pct}%"></div></div>
              <span class="category-stat-pct">${cat.pct}%</span>
            </div>
          </div>
        `;
      }
      html += '</div>';

      statsBody.innerHTML = html;
      statsModal.classList.add('visible');
    } catch (e) {
      console.error('Failed to fetch stats:', e);
    }
  }

  function hideStatsModal() { statsModal.classList.remove('visible'); }

  // ── Event Listeners ────────────────────
  function setupEventListeners() {
    cardContainer.addEventListener('click', e => {
      if (e.target.closest('.rating-btn')) return;
      flipCard();
    });

    $('btn-next').addEventListener('click', nextCard);
    $('btn-prev').addEventListener('click', prevCard);
    $('btn-speak').addEventListener('click', speakCurrent);
    $('btn-audio').addEventListener('click', toggleAudio);
    $('btn-dark-mode').addEventListener('click', toggleDarkMode);
    $('btn-stats').addEventListener('click', showStatsModal);

    document.querySelectorAll('.rating-btn').forEach(btn => {
      btn.addEventListener('click', e => {
        e.stopPropagation();
        rateCard(parseInt(btn.dataset.rating));
      });
    });

    // Topic multi-select dropdown
    var catTrigger = $('cat-trigger');
    var catMenu = $('cat-menu');
    var catLabel = $('cat-label');

    if (catTrigger) {
      catTrigger.addEventListener('click', function(e) {
        e.stopPropagation();
        catMenu.classList.toggle('open');
        catTrigger.classList.toggle('open');
      });

      document.addEventListener('click', function(e) {
        if (!catMenu.contains(e.target) && e.target !== catTrigger) {
          catMenu.classList.remove('open');
          catTrigger.classList.remove('open');
        }
      });

      catMenu.addEventListener('click', function(e) { e.stopPropagation(); });

      // "All" checkbox toggles everything
      var allCheck = catMenu.querySelector('[data-all]');
      var topicChecks = catMenu.querySelectorAll('.topic-check:not([data-all])');

      if (allCheck) {
        allCheck.addEventListener('change', function() {
          topicChecks.forEach(function(cb) { cb.checked = false; });
          allCheck.checked = true;
        });
      }

      topicChecks.forEach(function(cb) {
        cb.addEventListener('change', function() {
          if (cb.checked && allCheck) allCheck.checked = false;
          // If none selected, re-check All
          var anyChecked = Array.from(topicChecks).some(function(c) { return c.checked; });
          if (!anyChecked && allCheck) allCheck.checked = true;
        });
      });

      // Apply button
      var applyBtn = $('apply-topics');
      if (applyBtn) {
        applyBtn.addEventListener('click', async function() {
          var selected = Array.from(topicChecks).filter(function(c) { return c.checked; }).map(function(c) { return c.value; });
          activeSections = selected;

          if (selected.length === 0) {
            catLabel.innerHTML = '<i class="ph-bold ph-squares-four"></i> All Topics';
          } else if (selected.length === 1) {
            var label = topicChecks[Array.from(topicChecks).findIndex(function(c) { return c.checked; })].parentElement.querySelector('span').textContent;
            catLabel.innerHTML = '<i class="ph-bold ph-book-open"></i> ' + label;
          } else {
            catLabel.innerHTML = '<i class="ph-bold ph-book-open"></i> ' + selected.length + ' topics';
          }

          catMenu.classList.remove('open');
          catTrigger.classList.remove('open');
          await fetchCards(activeCategory);
          filterCards();
          showCard();
        });
      }
    }

    var modeEl = $('study-mode');
    if (modeEl) {
      modeEl.addEventListener('change', e => {
        studyMode = e.target.value;
        filterCards();
        showCard();
      });
    }

    $('close-stats').addEventListener('click', hideStatsModal);
    $('close-stats-2').addEventListener('click', hideStatsModal);
    statsModal.addEventListener('click', e => { if (e.target === statsModal) hideStatsModal(); });
  }

  // ── Keyboard ───────────────────────────
  function setupKeyboard() {
    document.addEventListener('keydown', e => {
      if (statsModal.classList.contains('visible')) {
        if (e.key === 'Escape') hideStatsModal();
        return;
      }
      switch (e.key) {
        case ' ': case 'Enter': e.preventDefault(); flipCard(); break;
        case 'ArrowRight': e.preventDefault(); nextCard(); break;
        case 'ArrowLeft': e.preventDefault(); prevCard(); break;
        case 's': case 'S': e.preventDefault(); speakCurrent(); break;
        case 'd': case 'D': e.preventDefault(); toggleDarkMode(); break;
        case '1': if (isFlipped) { e.preventDefault(); rateCard(1); } break;
        case '2': if (isFlipped) { e.preventDefault(); rateCard(3); } break;
        case '3': if (isFlipped) { e.preventDefault(); rateCard(5); } break;
      }
    });
  }

  // ── Touch / Swipe ──────────────────────
  function setupTouchGestures() {
    cardContainer.addEventListener('touchstart', e => {
      touchStartX = e.changedTouches[0].screenX;
      touchStartY = e.changedTouches[0].screenY;
      isSwiping = false;
    }, { passive: true });

    cardContainer.addEventListener('touchend', e => {
      const dx = e.changedTouches[0].screenX - touchStartX;
      const dy = e.changedTouches[0].screenY - touchStartY;
      if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy)) {
        isSwiping = true;
        dx < 0 ? nextCard() : prevCard();
        e.preventDefault();
      }
    });

    cardContainer.addEventListener('click', e => {
      if (isSwiping) { e.preventDefault(); e.stopPropagation(); isSwiping = false; }
    }, true);
  }

  // ── PWA ────────────────────────────────
  function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').catch(() => {});
    }
  }

  // ── Voices ─────────────────────────────
  if ('speechSynthesis' in window) {
    speechSynthesis.onvoiceschanged = () => {};
    speechSynthesis.getVoices();
  }

  // ── Start ──────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
