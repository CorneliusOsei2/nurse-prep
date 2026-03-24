// Prep — Scrolling Exam Mode
// All questions visible, each with Reveal → self-assess flow

(function () {
  'use strict';

  let answeredCount = 0;
  let correctCount = 0;
  let incorrectCount = 0;
  let timerSeconds = 0;
  let timerInterval = null;
  let quizFinished = false;

  const $ = id => document.getElementById(id);
  const timerDisplay = $('quiz-timer');
  const progressFill = $('quiz-progress-fill');
  const progressText = $('quiz-progress-text');
  const examBody = $('exam-body');
  const submitBar = $('exam-submit-bar');
  const timesupModal = $('timesup-modal');
  const quitModal = $('quit-modal');

  function init() {
    var dark = localStorage.getItem('prep_dark') === '1';
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');

    renderAllQuestions();
    startTimer();
    setupGlobalEvents();
  }

  // ── Render all questions ───────────────
  function renderAllQuestions() {
    var html = '';
    for (var i = 0; i < QUESTIONS.length; i++) {
      var q = QUESTIONS[i];
      html += '<div class="exam-q-block" id="q-block-' + i + '" data-index="' + i + '">'
        + '<div class="exam-question-card" id="q-card-' + i + '">'
        + '  <div class="exam-q-header">'
        + '    <span class="exam-q-number">Q' + (i + 1) + '</span>'
        + '    <span class="exam-q-category">' + escapeHtml(q.categoryLabel) + '</span>'
        + '  </div>'
        + '  <div class="exam-q-text">' + escapeHtml(q.question) + '</div>'
        + '  <button class="exam-reveal-btn" id="reveal-' + i + '" onclick="window._revealAnswer(' + i + ')">'
        + '    <i class="ph-bold ph-eye"></i> Show Answer'
        + '  </button>'
        + '  <div class="exam-answer-section" id="answer-' + i + '" style="display:none;">'
        + '    <div class="exam-answer-block">'
        + '      <div class="exam-answer-label">Answer</div>'
        + '      <div class="exam-answer-text">' + escapeHtml(q.answer) + '</div>'
        + '    </div>'
        + (q.rationale
          ? '    <div class="exam-rationale-block">' + escapeHtml(q.rationale) + '</div>'
          : '')
        + '    <div class="exam-assess-row" id="assess-' + i + '">'
        + '      <button class="exam-assess-btn incorrect" onclick="window._answerQuestion(' + i + ', false)">'
        + '        <i class="ph-bold ph-x"></i> Wrong'
        + '      </button>'
        + '      <button class="exam-assess-btn correct" onclick="window._answerQuestion(' + i + ', true)">'
        + '        <i class="ph-bold ph-check"></i> Got it'
        + '      </button>'
        + '    </div>'
        + '    <button class="exam-hide-btn" onclick="window._hideAnswer(' + i + ')">'
        + '      <i class="ph-bold ph-eye-slash"></i> Hide Answer'
        + '    </button>'
        + '  </div>'
        + '</div>'
        + '</div>';
    }
    examBody.innerHTML = html;
    highlightCurrent();
  }

  function highlightCurrent() {
    document.querySelectorAll('.exam-q-block.current').forEach(function(b) { b.classList.remove('current'); });
    var blocks = document.querySelectorAll('.exam-q-block');
    for (var i = 0; i < blocks.length; i++) {
      if (!blocks[i].classList.contains('completed')) {
        blocks[i].classList.add('current');
        return;
      }
    }
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML.replace(/\n/g, '<br>');
  }

  // ── Reveal answer for a question ───────
  window._revealAnswer = function(index) {
    if (quizFinished) return;
    var revealBtn = $('reveal-' + index);
    var answerSection = $('answer-' + index);
    var card = $('q-card-' + index);

    revealBtn.style.display = 'none';
    answerSection.style.display = 'block';

    // Mark this as the active question
    document.querySelectorAll('.exam-q-block.current').forEach(function(b) { b.classList.remove('current'); });
    $('q-block-' + index).classList.add('current');

    answerSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  };

  // ── Hide answer (collapse) ─────────────
  window._hideAnswer = function(index) {
    var revealBtn = $('reveal-' + index);
    var answerSection = $('answer-' + index);

    answerSection.style.display = 'none';
    revealBtn.style.display = 'block';
  };

  // ── Answer a question ──────────────────
  window._answerQuestion = function(index, isCorrect) {
    if (quizFinished) return;
    var block = $('q-block-' + index);
    var assess = $('assess-' + index);
    var card = $('q-card-' + index);

    // Prevent double-answering
    if (block.classList.contains('completed')) return;
    block.classList.add('completed');

    // Visual feedback
    if (isCorrect) {
      correctCount++;
      card.classList.add('result-correct');
    } else {
      incorrectCount++;
      card.classList.add('result-incorrect');
    }
    answeredCount++;

    // Replace assessment buttons with result badge
    assess.innerHTML = isCorrect
      ? '<div class="exam-result-badge correct"><i class="ph-bold ph-check-circle"></i> You got it right</div>'
      : '<div class="exam-result-badge incorrect"><i class="ph-bold ph-x-circle"></i> Marked for review</div>';

    // Update scoreboard
    $('score-correct').textContent = correctCount;
    $('score-incorrect').textContent = incorrectCount;
    $('score-remaining').textContent = QUIZ_TOTAL - answeredCount;

    // Update progress
    var pct = (answeredCount / QUIZ_TOTAL * 100).toFixed(0);
    progressFill.style.width = pct + '%';
    progressText.textContent = answeredCount + ' / ' + QUIZ_TOTAL + ' answered';

    // Send to API
    var q = QUESTIONS[index];
    fetch(ANSWER_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF_TOKEN },
      body: JSON.stringify({ question_id: q.id, is_correct: isCorrect }),
    }).catch(function(e) { console.error('Failed to save answer:', e); });

    // If all answered, scroll to next unanswered or show submit
    highlightCurrent();
    if (answeredCount >= QUIZ_TOTAL) {
      showSubmitButton();
    } else {
      scrollToNextUnanswered(index);
    }
  };

  function scrollToNextUnanswered(fromIndex) {
    for (var i = fromIndex + 1; i < QUESTIONS.length; i++) {
      var block = $('q-block-' + i);
      if (!block.classList.contains('completed')) {
        block.scrollIntoView({ behavior: 'smooth', block: 'start' });
        return;
      }
    }
    // Wrap around
    for (var j = 0; j < fromIndex; j++) {
      var block2 = $('q-block-' + j);
      if (!block2.classList.contains('completed')) {
        block2.scrollIntoView({ behavior: 'smooth', block: 'start' });
        return;
      }
    }
  }

  function showSubmitButton() {
    submitBar.style.display = 'block';
    submitBar.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  // ── Timer ──────────────────────────────
  function startTimer() {
    timerInterval = setInterval(function() {
      timerSeconds++;
      updateTimerDisplay();
      if (QUIZ_TIME_LIMIT && timerSeconds >= QUIZ_TIME_LIMIT * 60) {
        clearInterval(timerInterval);
        handleTimeUp();
      }
    }, 1000);
    if (QUIZ_TIME_LIMIT) timerDisplay.classList.add('has-limit');
    updateTimerDisplay();
  }

  function updateTimerDisplay() {
    if (QUIZ_TIME_LIMIT) {
      var remaining = Math.max(0, QUIZ_TIME_LIMIT * 60 - timerSeconds);
      var mins = Math.floor(remaining / 60);
      var secs = remaining % 60;
      timerDisplay.textContent = mins + ':' + secs.toString().padStart(2, '0');
      if (remaining <= 30) {
        timerDisplay.classList.add('danger');
        timerDisplay.classList.remove('warning');
      } else if (remaining <= 60) {
        timerDisplay.classList.add('warning');
      }
    } else {
      var mins2 = Math.floor(timerSeconds / 60);
      var secs2 = timerSeconds % 60;
      timerDisplay.textContent = mins2 + ':' + secs2.toString().padStart(2, '0');
    }
  }

  function handleTimeUp() {
    quizFinished = true;
    timesupModal.classList.add('visible');
  }

  // ── Finish ─────────────────────────────
  function finishQuiz() {
    if (quizFinished) return;
    quizFinished = true;
    clearInterval(timerInterval);

    // Mark unanswered as incorrect
    var promises = [];
    for (var i = 0; i < QUESTIONS.length; i++) {
      var block = $('q-block-' + i);
      if (!block.classList.contains('completed')) {
        var q = QUESTIONS[i];
        promises.push(
          fetch(ANSWER_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF_TOKEN },
            body: JSON.stringify({ question_id: q.id, is_correct: false }),
          }).catch(function() {})
        );
      }
    }

    Promise.all(promises).then(function() {
      return fetch(COMPLETE_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF_TOKEN },
        body: JSON.stringify({}),
      });
    }).then(function() {
      window.location.href = RESULTS_URL;
    }).catch(function() {
      window.location.href = RESULTS_URL;
    });
  }

  // ── Events ─────────────────────────────
  function setupGlobalEvents() {
    $('btn-quit').addEventListener('click', function() { quitModal.classList.add('visible'); });
    $('btn-quit-cancel').addEventListener('click', function() { quitModal.classList.remove('visible'); });
    $('btn-quit-confirm').addEventListener('click', finishQuiz);
    $('btn-timesup-finish').addEventListener('click', finishQuiz);
    $('btn-submit').addEventListener('click', finishQuiz);

    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        e.preventDefault();
        if (quitModal.classList.contains('visible')) quitModal.classList.remove('visible');
        else quitModal.classList.add('visible');
      }
    });
  }

  // ── Start ──────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
