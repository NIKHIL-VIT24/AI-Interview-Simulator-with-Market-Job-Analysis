// MAAI - Setup Page JS

let currentStep = 1;

function nextStep(n) {
  // Hide current
  document.querySelectorAll('.setup-step').forEach(s => s.classList.remove('active'));
  // Show target
  document.getElementById('step' + n)?.classList.add('active');
  currentStep = n;
  updateProgress(n);
  if (n === 3) checkDevices();
}

function updateProgress(n) {
  for (let i = 1; i <= 3; i++) {
    const step = document.getElementById('prog' + i);
    if (!step) continue;
    step.classList.remove('active', 'done');
    if (i < n) step.classList.add('done');
    if (i === n) step.classList.add('active');
  }
}

function handleFileUpload(input) {
  const file = input.files[0];
  if (!file) return;
  const status = document.getElementById('uploadStatus');
  const fileName = document.getElementById('uploadedFileName');
  const preview = document.getElementById('skillPreview');
  const zone = document.getElementById('uploadZone');

  fileName.textContent = file.name;
  status.style.display = 'flex';
  preview.style.display = 'block';
  zone.style.borderColor = 'var(--accent3)';
  zone.style.background = 'rgba(34,197,94,0.05)';
}

let stream = null;

async function checkDevices() {
  const camStatus = document.getElementById('camStatus');
  const micStatus = document.getElementById('micStatus');
  const video = document.getElementById('cameraPreview');

  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    video.srcObject = stream;
    camStatus.textContent = '✓ Ready';
    camStatus.className = 'device-status ok';
    micStatus.textContent = '✓ Ready';
    micStatus.className = 'device-status ok';
  } catch (e) {
    camStatus.textContent = '✗ Denied';
    camStatus.className = 'device-status error';
    micStatus.textContent = '✗ Denied';
    micStatus.className = 'device-status error';
    console.warn('Device access denied:', e);
  }
}

function goToInterview() {
  // Save setup info to sessionStorage
  const name = document.getElementById('candidateName')?.value || 'Candidate';
  const role = document.getElementById('targetRole')?.value || 'software_engineer';
  sessionStorage.setItem('candidateName', name);
  sessionStorage.setItem('targetRole', role);
  // Stop stream before navigating
  if (stream) stream.getTracks().forEach(t => t.stop());
  window.location.href = 'interview.html';
}

// Init progress
updateProgress(1);