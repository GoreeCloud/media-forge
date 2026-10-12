'use strict';
let sessionToken = null;
let scanned = null;
const $ = id => document.getElementById(id);

async function getJSON(path) {
  const response = await fetch(path, {cache: 'no-store'});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
  return data;
}

async function postJSON(path, body = {}) {
  if (!sessionToken) throw new Error('Local session not ready. Refresh the page.');
  const response = await fetch(path, {
    method: 'POST',
    headers: {'Content-Type': 'application/json', 'X-Media-Forge-Token': sessionToken},
    body: JSON.stringify(body)
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
  return data;
}

function status(message, error = false) {
  const el = $('action-status');
  el.textContent = message;
  el.style.color = error ? '#f5aaaa' : '#9eaec2';
}

function text(parent, tag, value, className) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  el.textContent = value;
  parent.append(el);
  return el;
}

async function scanSource() {
  const btn = $('scan');
  btn.disabled = true;
  try {
    scanned = await postJSON('/api/scan', {path: $('source').value.trim()});
    const r = $('source-result');
    r.replaceChildren();
    text(r, 'strong', `✓ ${scanned.name}`);
    const video = scanned.streams.find(s => s.type === 'video');
    text(r, 'div', `${scanned.streams.length} streams · ${video.width || '?'} × ${video.height || '?'} · ${Math.round(scanned.duration)}s · ${scanned.chapters} chapters`);
    text(r, 'div', `Video: ${scanned.streams.filter(s => s.type === 'video').map(s => s.codec).join(', ')} · Audio: ${scanned.streams.filter(s => s.type === 'audio').map(s => s.codec).join(', ') || 'none'}`);
    r.classList.remove('hidden');
    status('Scan complete. Choose a processing mode and queue the job.');
  } catch (err) {
    scanned = null;
    $('source-result').classList.add('hidden');
    status(err.message, true);
  } finally { btn.disabled = false; }
}

function updateModeUI() {
  document.querySelectorAll('.mode').forEach(label => label.classList.toggle('selected', label.querySelector('input').checked));
}

async function queueJob() {
  const btn = $('queue');
  btn.disabled = true;
  try {
    const mode = document.querySelector('input[name="mode"]:checked').value;
    const plan = {source: $('source').value.trim(), output_dir: $('output').value.trim(), mode, preset: $('preset').value, container: $('container').value};
    const job = await postJSON('/api/jobs', plan);
    status(`Queued ${job.id.slice(0, 8)} (${mode}). Processing runs on this computer.`);
    await loadJobs();
    location.hash = '#jobs';
  } catch (err) { status(err.message, true); }
  finally { btn.disabled = false; }
}

async function loadJobs() {
  try {
    const result = await getJSON('/api/jobs');
    const root = $('jobs-list');
    root.replaceChildren();
    if (!result.jobs.length) { text(root, 'div', 'No jobs yet. Jobs remain in your local database across application restarts.', 'empty-state'); return; }
    for (const job of result.jobs) {
      const node = document.createElement('div'); node.className = 'job';
      const top = text(node, 'div', '', 'job-top');
      text(top, 'strong', `${job.plan.mode.toUpperCase()} · ${job.plan.source.split(/[\\/]/).pop()}`);
      text(top, 'span', job.state, `job-status ${job.state}`);
      text(node, 'div', `Job ${job.id.slice(0,8)} · Stage: ${job.stage || 'queued'} · ${job.plan.preset}`, 'job-meta');
      const progress = text(node, 'div', '', 'progress');
      const progressBar = document.createElement('div');
      progressBar.style.width = `${Math.round(job.progress * 100)}%`;
      progress.append(progressBar);
      const actions = text(node, 'div', '', 'job-actions');
      text(actions, 'span', `${Math.round(job.progress * 100)}% complete`);
      if (job.state === 'running' || job.state === 'queued' || job.state === 'verifying' || job.state === 'processing') {
        const button = text(actions, 'button', 'Cancel', 'cancel');
        button.addEventListener('click', async () => {
          try { await postJSON(`/api/jobs/${job.id}/cancel`); await loadJobs(); }
          catch (err) { status(err.message, true); }
        });
      }
      if (job.error) text(node, 'div', job.error, 'job-error');
      if (job.outputs.length) {
        const container = text(node, 'div', '', 'outputs');
        for (const item of job.outputs) text(container, 'div', `${item.kind}: ${item.path}`);
      }
      root.append(node);
    }
  } catch (err) { status(`Failed to load queue: ${err.message}`, true); }
}

async function initialize() {
  try {
    sessionToken = (await getJSON('/api/session')).token;
    const health = await getJSON('/api/health');
    if (!health.executables.ffmpeg || !health.executables.ffprobe) status('FFmpeg/ffprobe not found. Install both to enable processing.', true);
  } catch (err) { status(`Unable to reach local engine: ${err.message}`, true); }
  $('scan').addEventListener('click', scanSource);
  $('queue').addEventListener('click', queueJob);
  $('refresh').addEventListener('click', loadJobs);
  document.querySelectorAll('input[name="mode"]').forEach(el => el.addEventListener('change', updateModeUI));
  $('source').addEventListener('change', () => {scanned = null; $('source-result').classList.add('hidden');});
  await loadJobs();
  setInterval(loadJobs, 1600);
}
initialize();
