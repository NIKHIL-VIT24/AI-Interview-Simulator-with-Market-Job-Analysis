// MAAI - Dashboard JS

document.addEventListener('DOMContentLoaded', () => {
  // Load session data if available
  const eyeContact = parseInt(sessionStorage.getItem('eyeContact')) || 82;
  const speechRate = parseInt(sessionStorage.getItem('speechRate')) || 145;
  const confidence = parseInt(sessionStorage.getItem('confidence')) || 74;
  const sessionScore = parseInt(sessionStorage.getItem('sessionScore')) || 78;
  const fillers = JSON.parse(sessionStorage.getItem('fillers') || '{"um":4,"uh":6,"like":2}');

  // Simulate scores
  const techScore = Math.min(100, sessionScore + 3);
  const resumeScore = 72;
  const behaviorScore = Math.round((eyeContact * 0.2 + confidence * 0.3 + (100 - (fillers.um + fillers.uh + fillers.like) * 3) * 0.5));
  const marketScore = 68;
  const hiringProb = Math.round((techScore * 0.35 + resumeScore * 0.25 + behaviorScore * 0.25 + marketScore * 0.15));

  // Animate after short delay
  setTimeout(() => {
    animateHiringScore(hiringProb);
    animateScoreBars({ techScore, resumeScore, behaviorScore, marketScore });
    animateBehavioralCircles({ eyeContact, speechRate, behaviorScore });
    fillBehavioralTable({ eyeContact, speechRate, fillers, behaviorScore });
    buildQuestionTable();
    buildDifficultyChart();
  }, 400);
});

// ========================
// HIRING PROBABILITY RING
// ========================
function animateHiringScore(score) {
  const el = document.getElementById('hiringScore');
  const ring = document.getElementById('hiringRingFill');
  const verdict = document.getElementById('hiringVerdict');

  // Animate number
  let current = 0;
  const interval = setInterval(() => {
    current = Math.min(score, current + 2);
    el.textContent = current;
    if (current >= score) clearInterval(interval);
  }, 30);

  // Animate ring (circumference = 2π×80 ≈ 502)
  const circumference = 502;
  const offset = circumference - (score / 100) * circumference;
  ring.style.strokeDashoffset = offset;

  // Verdict
  if (score >= 80) {
    verdict.textContent = '✅ Strong Hire';
    verdict.style.color = 'var(--accent3)';
  } else if (score >= 60) {
    verdict.textContent = '🟡 Likely Hire';
    verdict.style.color = 'var(--accent2)';
  } else {
    verdict.textContent = '🔴 Needs Improvement';
    verdict.style.color = 'var(--accent-red)';
  }
}

// ========================
// SCORE BARS
// ========================
function animateScoreBars({ techScore, resumeScore, behaviorScore, marketScore }) {
  const bars = [
    { barId: 'techScoreBar', valId: 'techScoreVal', value: techScore },
    { barId: 'resumeScoreBar', valId: 'resumeScoreVal', value: resumeScore },
    { barId: 'behaviorScoreBar', valId: 'behaviorScoreVal', value: behaviorScore },
    { barId: 'marketScoreBar', valId: 'marketScoreVal', value: marketScore },
  ];

  bars.forEach(({ barId, valId, value }) => {
    const bar = document.getElementById(barId);
    const val = document.getElementById(valId);
    if (bar) bar.style.width = value + '%';
    if (val) val.textContent = value + '%';
  });
}

// ========================
// BEHAVIORAL CIRCLES
// ========================
function animateBehavioralCircles({ eyeContact, speechRate, behaviorScore }) {
  const circles = [
    { ringId: 'eyeRing', pctId: 'eyePct', value: eyeContact, label: eyeContact + '%' },
    { ringId: 'speechRing', pctId: 'speechPct', value: Math.min(100, (speechRate / 200) * 100), label: speechRate },
    { ringId: 'emotionRing', pctId: 'emotionPct', value: behaviorScore, label: behaviorScore + '%' },
  ];

  // Circumference for r=32: 2π×32 ≈ 201
  const circ = 201;
  circles.forEach(({ ringId, pctId, value, label }) => {
    const ring = document.getElementById(ringId);
    const pct = document.getElementById(pctId);
    if (ring) ring.style.strokeDashoffset = circ - (value / 100) * circ;
    if (pct) pct.textContent = label;
  });
}

// ========================
// BEHAVIORAL TABLE
// ========================
function fillBehavioralTable({ eyeContact, speechRate, fillers, behaviorScore }) {
  const srNorm = Math.min(1, speechRate / 160).toFixed(2);
  const pdVal = (Math.random() * 0.3 + 0.1).toFixed(2);
  const fcNorm = Math.max(0, (1 - (fillers.um + fillers.uh + fillers.like) * 0.03)).toFixed(2);
  const ecNorm = (eyeContact / 100).toFixed(2);
  const bmVal = (Math.random() * 0.15 + 0.05).toFixed(2);
  const esVal = (behaviorScore / 100).toFixed(2);

  const ids = ['srVal', 'pdVal', 'fcVal', 'ecVal', 'bmVal', 'esVal'];
  const vals = [srNorm, pdVal, fcNorm, ecNorm, bmVal, esVal];
  ids.forEach((id, i) => {
    const el = document.getElementById(id);
    if (el) el.textContent = vals[i];
  });
}

// ========================
// QUESTION TABLE
// ========================
const questionData = [
  { q: "Supervised vs Unsupervised Learning", diff: "MEDIUM", score: 85, time: "3:12", status: "Pass" },
  { q: "Binary Search Time Complexity", diff: "EASY", score: 95, time: "1:45", status: "Pass" },
  { q: "Scalable REST API Design", diff: "HARD", score: 62, time: "4:30", status: "Pass" },
  { q: "Challenging Project Experience", diff: "MEDIUM", score: 88, time: "2:55", status: "Pass" },
  { q: "Gradient Boosting vs Random Forest", diff: "HARD", score: 71, time: "3:50", status: "Pass" },
  { q: "Transformer Model & Attention", diff: "HARD", score: 58, time: "4:10", status: "Partial" },
  { q: "Handling Missing Data", diff: "MEDIUM", score: 80, time: "2:20", status: "Pass" },
  { q: "CAP Theorem", diff: "HARD", score: 54, time: "3:40", status: "Partial" },
  { q: "Career Motivation in ML/AI", diff: "EASY", score: 92, time: "2:05", status: "Pass" },
  { q: "Median from Data Stream", diff: "HARD", score: 45, time: "4:55", status: "Fail" },
];

function buildQuestionTable() {
  const body = document.getElementById('qtBody');
  if (!body) return;
  body.innerHTML = questionData.map((q, i) => {
    const diffColor = q.diff === 'EASY' ? 'var(--accent3)' : q.diff === 'MEDIUM' ? 'var(--accent2)' : 'var(--accent-red)';
    const statusColor = q.status === 'Pass' ? 'var(--accent3)' : q.status === 'Partial' ? 'var(--accent2)' : 'var(--accent-red)';
    const scoreColor = q.score >= 80 ? 'var(--accent3)' : q.score >= 60 ? 'var(--accent2)' : 'var(--accent-red)';
    return `<div class="qt-row-item">
      <span style="color:var(--text-muted);font-family:var(--font-mono);font-size:12px">${i + 1}</span>
      <span style="font-size:13px">${q.q}</span>
      <span style="color:${diffColor};font-family:var(--font-mono);font-size:11px">${q.diff}</span>
      <span style="color:${scoreColor};font-family:var(--font-display);font-weight:700">${q.score}</span>
      <span style="color:var(--text-muted);font-family:var(--font-mono);font-size:12px">${q.time}</span>
      <span style="color:${statusColor};font-size:12px;font-weight:600">${q.status}</span>
    </div>`;
  }).join('');
}

// ========================
// DIFFICULTY CHART
// ========================
const difficultyProgress = [1, 1, 2, 2, 3, 3, 4, 3, 3, 4]; // difficulty per question
const colors = ['var(--accent3)', 'var(--accent)', 'var(--accent2)', 'var(--accent-red)'];

function buildDifficultyChart() {
  const chart = document.getElementById('diffChart');
  if (!chart) return;
  const maxH = 100;
  chart.innerHTML = difficultyProgress.map((d, i) => {
    const h = (d / 4) * maxH;
    const c = colors[d - 1];
    return `<div class="diff-bar" style="height:${h}px;background:${c};opacity:0.8" title="Q${i+1}: Level ${d}">
      <span>Q${i+1}</span>
    </div>`;
  }).join('');
}