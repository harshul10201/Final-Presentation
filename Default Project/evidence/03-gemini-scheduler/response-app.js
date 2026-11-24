const pageTitle = {
  dashboard: 'Dashboard',
  meetings: 'Meetings',
  schedule: 'Schedule',
  digest: 'Weekly digest',
  chat: 'Ask AI',
};

let currentPage = 'dashboard';

function esc(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function card(inner, extraClass = '') {
  return `<div class="card ${extraClass}">${inner}</div>`;
}

async function api(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch (_) {
    data = text;
  }
  if (!res.ok) {
    const message = (data && data.detail) || (typeof data === 'string' && data) || `Request failed (${res.status})`;
    throw new Error(message);
  }
  return data;
}

function setActiveNav(page) {
  document.querySelectorAll('.nav button[data-page]').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.page === page);
  });
}

async function schedule() {
  const content = document.getElementById('content');
  let meetings = [];
  let loadError = '';

  try {
    meetings = await api('/schedule');
  } catch (err) {
    loadError = err.message;
  }

  const aiSection = card(`
    <h3>Schedule with AI</h3>
    <div class="row">
      <input id="ai-schedule-input" type="text" placeholder="e.g. Schedule a meeting with Rahul and Priya on 25 December 2026 at 15:00 about launch prep" />
      <button id="ai-schedule-btn" type="button">Schedule with AI</button>
    </div>
    <div id="ai-schedule-error" class="error-text"></div>
  `);

  const manualSection = card(`
    <h3>Manual Schedule</h3>
    <form id="manual-schedule-form" class="schedule-form">
      <input name="title" type="text" placeholder="Meeting title" required />
      <input name="date" type="text" placeholder="Date (YYYY-MM-DD)" required />
      <input name="time" type="text" placeholder="Time (HH:MM or TBD)" value="TBD" />
      <input name="participants" type="text" placeholder="Participants" />
      <input name="agenda" type="text" placeholder="Agenda" />
      <button type="submit">Add Meeting</button>
    </form>
    <div id="manual-schedule-error" class="error-text"></div>
  `);

  const listHtml = loadError
    ? card(`<p class="error-text">${esc(loadError)}</p>`)
    : meetings.length === 0
      ? card('<p>No scheduled meetings yet.</p>')
      : meetings
          .map((m) =>
            card(`
              <div class="meeting-item">
                <div>
                  <div class="meeting-header">
                    <strong>${esc(m.title)}</strong>
                    <span class="status-pill status-${esc(m.status)}">${esc(m.status)}</span>
                  </div>
                  <div>Date: ${esc(m.date)} | Time: ${esc(m.time || 'TBD')}</div>
                  ${m.participants ? `<div>Participants: ${esc(m.participants)}</div>` : ''}
                  ${m.agenda ? `<div>Agenda: ${esc(m.agenda)}</div>` : ''}
                </div>
                <div class="actions">
                  <button type="button" data-action="complete" data-id="${esc(m.id)}">Mark completed</button>
                  <button type="button" data-action="cancel" data-id="${esc(m.id)}">Cancel</button>
                  <button type="button" data-action="delete" data-id="${esc(m.id)}">Delete</button>
                </div>
              </div>
            `)
          )
          .join('');

  content.innerHTML = `${aiSection}${manualSection}<div id="schedule-list">${listHtml}</div>`;

  const aiInput = document.getElementById('ai-schedule-input');
  const aiBtn = document.getElementById('ai-schedule-btn');
  const aiError = document.getElementById('ai-schedule-error');

  aiBtn.addEventListener('click', async () => {
    aiError.textContent = '';
    const text = aiInput.value.trim();
    if (!text) {
      aiError.textContent = 'Please enter a meeting description.';
      return;
    }
    aiBtn.disabled = true;
    try {
      await api('/schedule/ai', {
        method: 'POST',
        body: JSON.stringify({ text }),
      });
      await render('schedule');
    } catch (err) {
      aiError.textContent = err.message;
      aiBtn.disabled = false;
    }
  });

  const manualForm = document.getElementById('manual-schedule-form');
  const manualError = document.getElementById('manual-schedule-error');
  manualForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    manualError.textContent = '';
    const formData = new FormData(manualForm);
    const payload = {
      title: String(formData.get('title') || '').trim(),
      date: String(formData.get('date') || '').trim(),
      time: String(formData.get('time') || 'TBD').trim() || 'TBD',
      participants: String(formData.get('participants') || '').trim(),
      agenda: String(formData.get('agenda') || '').trim(),
    };
    try {
      await api('/schedule', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      await render('schedule');
    } catch (err) {
      manualError.textContent = err.message;
    }
  });

  content.querySelectorAll('button[data-action]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const id = btn.dataset.id;
      const action = btn.dataset.action;
      try {
        if (action === 'complete') {
          await api(`/schedule/${id}/status`, {
            method: 'PATCH',
            body: JSON.stringify({ status: 'completed' }),
          });
        } else if (action === 'cancel') {
          await api(`/schedule/${id}/status`, {
            method: 'PATCH',
            body: JSON.stringify({ status: 'cancelled' }),
          });
        } else if (action === 'delete') {
          await api(`/schedule/${id}`, {
            method: 'DELETE',
          });
        }
        await render('schedule');
      } catch (err) {
        aiError.textContent = err.message;
      }
    });
  });
}

async function render(page = currentPage) {
  currentPage = pageTitle[page] ? page : 'dashboard';
  setActiveNav(currentPage);
  document.getElementById('page-title').textContent = pageTitle[currentPage];

  switch (currentPage) {
    case 'schedule':
      await schedule();
      break;
    default:
      document.getElementById('content').innerHTML = card(`<p>${esc(pageTitle[currentPage])}</p>`);
      break;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.nav button[data-page]').forEach((btn) => {
    btn.addEventListener('click', () => render(btn.dataset.page));
  });
  render('dashboard');
});