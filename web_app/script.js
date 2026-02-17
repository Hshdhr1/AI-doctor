new file mode 100644
/**

AI-ВЕТЕРИНАР — Web App Script
*/

// ===== Инициализация Telegram WebApp =====
const tg = window.Telegram?.WebApp;
if (tg) {

tg.ready();
tg.expand();

}

// Получаем user_id из Telegram initData
function getUserId() {

try {
text
  if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) {
text
      return tg.initDataUnsafe.user.id;
text
  }
} catch (e) {}
// Для тестирования без Telegram
return 0;

}

// ===== Состояние приложения =====
const state = {

userId: getUserId(),
language: 'ru',
specialization: 'therapist',
model: 'openai',
specializations: [],
chatHistory: [],
isLoading: false,

};

// ===== API URL (относительный, т.к. фронтенд раздаётся с того же сервера) =====
const API_BASE = '';

// ===== Локализация =====
const i18n = {

ru: {
text
  title: '🐾 AI-ВЕТЕРИНАР',
text
  subtitle: 'Выберите специализацию врача:',
text
  input_placeholder: 'Опишите симптомы...',
text
  settings_title: '⚙️ Настройки',
text
  label_model: 'Модель AI:',
text
  label_lang: 'Язык / Language:',
text
  btn_clear: '🗑 Очистить историю чата',
text
  nav_home: 'Главная',
text
  nav_chat: 'Чат',
text
  nav_settings: 'Настройки',
text
  typing: 'Ветеринар печатает...',
text
  error_network: 'Ошибка сети. Попробуйте позже.',
text
  welcome: 'Здравствуйте! Я ваш AI-ветеринар. Опишите симптомы вашего питомца, и я постараюсь помочь.\n\n⚠️ Помните: я ИИ и не заменяю очную консультацию ветеринара.',
text
  history_cleared: 'История чата очищена.',
},
en: {
text
  title: '🐾 AI-VET',
text
  subtitle: 'Choose a veterinary specialization:',
text
  input_placeholder: 'Describe symptoms...',
text
  settings_title: '⚙️ Settings',
text
  label_model: 'AI Model:',
text
  label_lang: 'Language:',
text
  btn_clear: '🗑 Clear chat history',
text
  nav_home: 'Home',
text
  nav_chat: 'Chat',
text
  nav_settings: 'Settings',
text
  typing: 'Vet is typing...',
text
  error_network: 'Network error. Please try again.',
text
  welcome: 'Hello! I am your AI veterinarian. Describe your pet\'s symptoms and I\'ll try to help.\n\n⚠️ Remember: I am an AI and do not replace an in-person veterinary consultation.',
text
  history_cleared: 'Chat history cleared.',
}

};

function t(key) {

return (i18n[state.language] || i18n.ru)[key] || key;

}

// ===== DOM элементы =====
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const screenSpecs = $('#screen-specializations');
const screenChat = $('#screen-chat');
const specGrid = $('#spec-grid');
const chatMessages = $('#chat-messages');
const chatInput = $('#chat-input');
const btnSend = $('#btn-send');
const btnBack = $('#btn-back');
const btnSettings = $('#btn-settings');
const modalSettings = $('#modal-settings');
const btnCloseSettings = $('#btn-close-settings');
const selectModel = $('#select-model');
const selectLangSettings = $('#select-lang-settings');
const btnClearHistory = $('#btn-clear-history');
const bottomNav = $('#bottom-nav');

// ===== API-вызовы =====
async function apiCall(endpoint, options = {}) {

try {
text
  const response = await fetch(`${API_BASE}${endpoint}`, {
text
      headers: { 'Content-Type': 'application/json' },
text
      ...options,
text
  });
text
  if (!response.ok) {
text
      const err = await response.json().catch(() => ({}));
text
      throw new Error(err.message || `HTTP ${response.status}`);
text
  }
text
  return await response.json();
} catch (e) {
text
  console.error('API Error:', e);
text
  throw e;
}

}

async function loadSpecializations() {

try {
text
  const data = await apiCall(`/api/specializations?lang=${state.language}`);
text
  state.specializations = data.specializations;
text
  renderSpecializations();
} catch (e) {
text
  console.error('Failed to load specializations:', e);
}

}

async function loadUserSettings() {

if (!state.userId) return;
try {
text
  const data = await apiCall(`/api/user/${state.userId}`);
text
  if (data.user) {
text
      state.language = data.user.language || 'ru';
text
      state.specialization = data.user.specialization || 'therapist';
text
      state.model = data.user.model || 'openai';
text
  }
} catch (e) {
text
  console.error('Failed to load user settings:', e);
}

}

async function saveSettings() {

if (!state.userId) return;
try {
text
  await apiCall('/api/settings', {
text
      method: 'POST',
text
      body: JSON.stringify({
text
          user_id: state.userId,
text
          language: state.language,
text
          specialization: state.specialization,
text
          model: state.model,
text
      }),
text
  });
} catch (e) {
text
  console.error('Failed to save settings:', e);
}

}

async function sendMessage(text) {

if (!text.trim() || state.isLoading) return;
state.isLoading = true;
btnSend.disabled = true;
// Добавить сообщение пользователя
addMessage('user', text);
chatInput.value = '';
// Показать индикатор набора
const typingEl = addMessage('typing', t('typing'));
try {
text
  const data = await apiCall('/api/chat', {
text
      method: 'POST',
text
      body: JSON.stringify({
text
          user_id: state.userId,
text
          message: text,
text
          specialization: state.specialization,
text
          language: state.language,
text
          model: state.model,
text
      }),
text
  });
text
  // Убрать индикатор
text
  typingEl.remove();
text
  // Добавить ответ
text
  addMessage('assistant', data.response);
} catch (e) {
text
  typingEl.remove();
text
  addMessage('assistant', t('error_network'));
} finally {
text
  state.isLoading = false;
text
  btnSend.disabled = false;
}

}

async function loadChatHistory() {

if (!state.userId) return;
try {
text
  const data = await apiCall(`/api/history/${state.userId}/${state.specialization}`);
text
  chatMessages.innerHTML = '';
text
  if (data.history && data.history.length > 0) {
text
      data.history.forEach(msg => {
text
          addMessage(msg.role, msg.content);
text
      });
text
  } else {
text
      addMessage('assistant', t('welcome'));
text
  }
} catch (e) {
text
  chatMessages.innerHTML = '';
text
  addMessage('assistant', t('welcome'));
}

}

async function clearHistory() {

if (!state.userId) return;
try {
text
  await apiCall('/api/clear_history', {
text
      method: 'POST',
text
      body: JSON.stringify({
text
          user_id: state.userId,
text
          specialization: state.specialization,
text
      }),
text
  });
text
  chatMessages.innerHTML = '';
text
  addMessage('assistant', t('history_cleared'));
} catch (e) {
text
  console.error('Failed to clear history:', e);
}

}

// ===== Рендеринг =====
function renderSpecializations() {

specGrid.innerHTML = '';
state.specializations.forEach(spec => {
text
  const card = document.createElement('div');
text
  card.className = `spec-card${spec.id === state.specialization ? ' selected' : ''}`;
text
  card.dataset.id = spec.id;
text
  card.innerHTML = `
text
      <span class="spec-icon">${spec.icon}</span>
text
      <span class="spec-name">${spec.name}</span>
text
  `;
text
  card.addEventListener('click', () => selectSpecialization(spec.id));
text
  specGrid.appendChild(card);
});

}

function selectSpecialization(specId) {

state.specialization = specId;
saveSettings();
renderSpecializations();
showScreen('chat');
loadChatHistory();
updateChatHeader();

}

function updateChatHeader() {

const spec = state.specializations.find(s => s.id === state.specialization);
if (spec) {
text
  $('#chat-spec-icon').textContent = spec.icon;
text
  $('#chat-spec-name').textContent = spec.name;
}

}

function addMessage(role, content) {

const div = document.createElement('div');
div.className = message ${role};
div.textContent = content;
chatMessages.appendChild(div);
chatMessages.scrollTop = chatMessages.scrollHeight;
return div;

}

function showScreen(name) {

screenSpecs.classList.remove('active');
screenChat.classList.remove('active');
if (name === 'specializations') {
text
  screenSpecs.classList.add('active');
} else if (name === 'chat') {
text
  screenChat.classList.add('active');
} else if (name === 'settings') {
text
  openSettings();
text
  return;
}
// Обновить навигацию
text
  btn.classList.toggle('active', btn.dataset.screen === name);
});

}

function updateUI() {

// Заголовки
$('#header-title').textContent = t('title');
$('#subtitle').textContent = t('subtitle');
chatInput.placeholder = t('input_placeholder');
$('#settings-title').textContent = t('settings_title');
$('#label-model').textContent = t('label_model');
$('#label-lang').textContent = t('label_lang');
$('#btn-clear-history').textContent = t('btn_clear');
// Навигация
text
  const key = el.dataset.i18n;
text
  if (key) el.textContent = t(key);
});
// Язык
text
  btn.classList.toggle('active', btn.dataset.lang === state.language);
});
// Настройки
selectModel.value = state.model;
selectLangSettings.value = state.language;

}

function openSettings() {

modalSettings.classList.remove('hidden');
selectModel.value = state.model;
selectLangSettings.value = state.language;

}

function closeSettings() {

modalSettings.classList.add('hidden');

}

// ===== Обработчики событий =====

// Отправка сообщения
btnSend.addEventListener('click', () => {

sendMessage(chatInput.value);

});

chatInput.addEventListener('keydown', (e) => {

if (e.key === 'Enter' && !e.shiftKey) {
text
  e.preventDefault();
text
  sendMessage(chatInput.value);
}

});

// Назад к специализациям
btnBack.addEventListener('click', () => {

showScreen('specializations');

});

// Настройки
btnSettings.addEventListener('click', openSettings);
btnCloseSettings.addEventListener('click', closeSettings);
$('.modal-overlay')?.addEventListener('click', closeSettings);

// Выбор модели
selectModel.addEventListener('change', () => {

state.model = selectModel.value;
saveSettings();

});

// Выбор языка в настройках
selectLangSettings.addEventListener('change', async () => {

state.language = selectLangSettings.value;
await saveSettings();
await loadSpecializations();
updateUI();
updateChatHeader();

});

// Переключатель языка на главной
$$('.lang-btn').forEach(btn => {

btn.addEventListener('click', async () => {
text
  state.language = btn.dataset.lang;
text
  await saveSettings();
text
  await loadSpecializations();
text
  updateUI();
});

});

// Очистка истории
btnClearHistory.addEventListener('click', async () => {

await clearHistory();
closeSettings();

});

// Нижняя навигация
$$('.nav-btn').forEach(btn => {

btn.addEventListener('click', () => {
text
  const screen = btn.dataset.screen;
text
  if (screen === 'settings') {
text
      openSettings();
text
  } else if (screen === 'chat') {
text
      showScreen('chat');
text
      loadChatHistory();
text
      updateChatHeader();
text
  } else {
text
      showScreen(screen);
text
  }
});

});

// ===== Инициализация =====
async function init() {

await loadUserSettings();
await loadSpecializations();
updateUI();
showScreen('specializations');

}

init();