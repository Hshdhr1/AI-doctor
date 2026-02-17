specialization: 'therapist',
model: 'openai',
specializations: [],

models: [],
chatHistory: [],
isLoading: false,
};
}
}

async function loadModels() {

try {
text
  const data = await apiCall('/api/models');
text
  state.models = data.models || [];
text
  renderModels();
} catch (e) {
text
  console.error('Failed to load models:', e);
}

}

function renderModels() {

selectModel.innerHTML = '';
state.models.forEach(m => {
text
  const option = document.createElement('option');
text
  option.value = m.id;
text
  option.textContent = m.name;
text
  selectModel.appendChild(option);
});
selectModel.value = state.model;

}

async function loadUserSettings() {
if (!state.userId) return;
try {
async function init() {
await loadUserSettings();
await loadSpecializations();

await loadModels();
updateUI();
showScreen('specializations');
}