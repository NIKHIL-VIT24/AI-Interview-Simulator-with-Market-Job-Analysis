// MAAI - Interview Page JS

// ========================
// QUESTIONS DATA
// ========================
const questions = [
  { text: "Can you explain the difference between supervised and unsupervised learning, and give an example of each?", difficulty: "MEDIUM", category: "TECHNICAL" },
  { text: "What is the time complexity of a binary search algorithm and how does it work?", difficulty: "EASY", category: "DSA" },
  { text: "Explain how you would design a scalable REST API for a real-time recommendation system.", difficulty: "HARD", category: "SYSTEM DESIGN" },
  { text: "Describe a challenging project you worked on. What was your role and what did you learn from it?", difficulty: "MEDIUM", category: "BEHAVIORAL" },
  { text: "What are the key differences between gradient boosting and random forest? When would you use each?", difficulty: "HARD", category: "ML" },
  { text: "How does a transformer model work? Explain the attention mechanism in simple terms.", difficulty: "HARD", category: "DEEP LEARNING" },
  { text: "How would you handle missing data in a large ML dataset with millions of rows?", difficulty: "MEDIUM", category: "DATA SCIENCE" },
  { text: "Explain the CAP theorem and how it applies to distributed systems.", difficulty: "HARD", category: "SYSTEM DESIGN" },
  { text: "What motivates you to pursue a career in machine learning and AI?", difficulty: "EASY", category: "BEHAVIORAL" },
  { text: "Given a stream of integers, how would you find the median at any point?", difficulty: "HARD", category: "DSA" },
];

let currentQIndex = 0;
let timerInterval = null;
let elapsedSeconds = 0;
let isRecording = false;
let mediaRecorder = null;
let webcamStream = null;

// Simulated live metrics
let eyeContact = 0;
let speechRate = 0;
let confidence = 0;
let fillerCounts = { um: 0, uh: 0, like: 0 };
let metricsInterval = null;
let sessionScore = 0;

// ========================
// INIT
// ========================
document.addEventListener('DOMContentLoaded', async () => {
  loadQuestion(0);
  startTimer();
  await initWebcam();
  startMetricsSimulation();
});

// ========================
// QUESTIONS
// ========================
function loadQuestion(index) {
  if (index >= questions.length) {
    endSession();
    return;
  }
  const q = questions[index];
  document.getElementById('questionText').textContent = q.text;
  document.getElementById('difficultyTag').textContent = q.difficulty;
  document.getElementById('categoryTag').textContent = q.category;
  document.getElementById('currentQ').textContent = index + 1;
  document.getElementById('totalQ').textContent = questions.length;

  // Update progress bar
  const pct = ((index + 1) / questions.length) * 100;
  document.getElementById('progressFill').style.width = pct + '%';

  // Update difficulty display
  const levelMap = { EASY: 'Level 1', MEDIUM: 'Level 2', HARD: 'Level 3–4' };
  document.getElementById('currentDifficulty').textContent = levelMap[q.difficulty] || 'Level 2';

  // Clear transcript
  clearTranscript();
  setAvatarStatus('Asking question...');
  setTimeout(() => setAvatarStatus('Listening...'), 2000);
}

function nextQuestion() {
  currentQIndex++;
  if (currentQIndex >= questions.length) {
    endSessionConfirm();
    return;
  }
  loadQuestion(currentQIndex);
  // Simulate score update
  sessionScore = Math.min(100, sessionScore + Math.floor(Math.random() * 12 + 5));
  document.getElementById('sessionScore').textContent = sessionScore;
  resetAnswerBars();
}

function repeatQuestion() {
  setAvatarStatus('Repeating question...');
  setTimeout(() => setAvatarStatus('Listening...'), 2000);
}

function resetAnswerBars() {
  document.getElementById('relevanceBar').style.width = '0%';
  document.getElementById('depthBar').style.width = '0%';
  document.getElementById('clarityBar').style.width = '0%';
}

// ========================
// TIMER
// ========================
function startTimer() {
  timerInterval = setInterval(() => {
    elapsedSeconds++;
    const m = String(Math.floor(elapsedSeconds / 60)).padStart(2, '0');
    const s = String(elapsedSeconds % 60).padStart(2, '0');
    document.getElementById('timer').textContent = `${m}:${s}`;
  }, 1000);
}

// ========================
// WEBCAM
// ========================
async function initWebcam() {
  try {
    webcamStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    document.getElementById('candidateVideo').srcObject = webcamStream;
  } catch (e) {
    console.warn('Webcam not available:', e);
  }
}

// ========================
// RECORDING
// ========================
function toggleRecording() {
  const btn = document.getElementById('recordBtn');
  isRecording = !isRecording;

  if (isRecording) {
    btn.classList.add('active');
    btn.innerHTML = '<span class="rec-circle"></span> Recording...';
    document.getElementById('micIndicator').textContent = '🔴 Recording';
    startTranscriptSimulation();
    startAnswerAnalysis();
  } else {
    btn.classList.remove('active');
    btn.innerHTML = '<span class="rec-circle"></span> Start Recording';
    document.getElementById('micIndicator').textContent = '🎙️ Listening';
    stopTranscriptSimulation();
  }
}

// ========================
// TRANSCRIPT SIMULATION
// ========================
let transcriptInterval = null;
const samplePhrases = [
  "So, supervised learning is when the model is trained on labeled data...",
  "For example, predicting house prices based on features like size and location...",
  "Unsupervised learning, on the other hand, works with unlabeled data...",
  "Clustering algorithms like K-Means are a good example of this...",
  "The model finds patterns and structure in the data on its own...",
];
let phraseIndex = 0;

function startTranscriptSimulation() {
  const box = document.getElementById('transcriptBox');
  box.innerHTML = '';
  phraseIndex = 0;

  transcriptInterval = setInterval(() => {
    if (phraseIndex < samplePhrases.length) {
      box.innerHTML += `<span>${samplePhrases[phraseIndex]} </span>`;
      box.scrollTop = box.scrollHeight;
      phraseIndex++;
    }
  }, 1800);
}

function stopTranscriptSimulation() {
  clearInterval(transcriptInterval);
}

function clearTranscript() {
  const box = document.getElementById('transcriptBox');
  box.innerHTML = '<div class="transcript-placeholder">Your spoken answer will appear here in real time...</div>';
  stopTranscriptSimulation();
  if (isRecording) toggleRecording();
}

// ========================
// ANSWER ANALYSIS SIMULATION
// ========================
let analysisInterval = null;

function startAnswerAnalysis() {
  analysisInterval = setInterval(() => {
    const r = Math.min(100, parseInt(document.getElementById('relevanceBar').style.width) + Math.random() * 5);
    const d = Math.min(100, parseInt(document.getElementById('depthBar').style.width) + Math.random() * 4);
    const c = Math.min(100, parseInt(document.getElementById('clarityBar').style.width) + Math.random() * 6);
    document.getElementById('relevanceBar').style.width = r + '%';
    document.getElementById('depthBar').style.width = d + '%';
    document.getElementById('clarityBar').style.width = c + '%';
  }, 800);
}

// ========================
// BEHAVIORAL METRICS SIMULATION
// ========================
function startMetricsSimulation() {
  metricsInterval = setInterval(() => {
    // Eye contact
    eyeContact = Math.min(100, Math.max(40, eyeContact + (Math.random() - 0.4) * 8));
    document.getElementById('eyeContactVal').textContent = Math.round(eyeContact) + '%';
    document.getElementById('eyeBar').style.width = eyeContact + '%';

    // Speech rate
    if (isRecording) {
      speechRate = Math.min(200, Math.max(80, speechRate + (Math.random() - 0.5) * 15));
      document.getElementById('speechRateVal').textContent = Math.round(speechRate) + ' wpm';
      document.getElementById('speechBar').style.width = Math.min(100, (speechRate / 200) * 100) + '%';
    }

    // Confidence
    confidence = Math.min(100, Math.max(30, confidence + (Math.random() - 0.3) * 6));
    document.getElementById('confidenceVal').textContent = Math.round(confidence) + '%';
    document.getElementById('confidenceBar').style.width = confidence + '%';

    // Filler words simulation
    if (isRecording && Math.random() < 0.08) {
      const fillers = ['um', 'uh', 'like'];
      const f = fillers[Math.floor(Math.random() * fillers.length)];
      fillerCounts[f]++;
      updateFillerDisplay();
    }

  }, 500);
}

function updateFillerDisplay() {
  const total = fillerCounts.um + fillerCounts.uh + fillerCounts.like;
  document.getElementById('fillerVal').textContent = total;
  document.getElementById('fillerList').innerHTML =
    `<span class="filler-tag">um: ${fillerCounts.um}</span>
     <span class="filler-tag">uh: ${fillerCounts.uh}</span>
     <span class="filler-tag">like: ${fillerCounts.like}</span>`;
}

// ========================
// AVATAR STATUS
// ========================
function setAvatarStatus(text) {
  document.getElementById('avatarStatus').textContent = text;
  const indicator = document.getElementById('speakingIndicator');
  if (text.includes('Asking') || text.includes('Repeat')) {
    indicator.classList.add('active');
    setTimeout(() => indicator.classList.remove('active'), 2000);
  }
}

// ========================
// SESSION END
// ========================
function endSessionConfirm() {
  document.getElementById('endModal').style.display = 'flex';
}

function endSession() {
  endSessionConfirm();
}

function closeModal() {
  document.getElementById('endModal').style.display = 'none';
}

// Save session data before leaving
window.addEventListener('beforeunload', () => {
  clearInterval(timerInterval);
  clearInterval(metricsInterval);
  clearInterval(transcriptInterval);
  clearInterval(analysisInterval);
  if (webcamStream) webcamStream.getTracks().forEach(t => t.stop());
  // Save metrics to sessionStorage for dashboard
  sessionStorage.setItem('eyeContact', Math.round(eyeContact));
  sessionStorage.setItem('speechRate', Math.round(speechRate));
  sessionStorage.setItem('confidence', Math.round(confidence));
  sessionStorage.setItem('sessionScore', sessionScore);
  sessionStorage.setItem('fillers', JSON.stringify(fillerCounts));
  sessionStorage.setItem('questionsAnswered', currentQIndex + 1);
});