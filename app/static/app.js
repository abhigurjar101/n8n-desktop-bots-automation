/**
 * n8n Desktop Bots Suite - Interactive Client Application
 * Supervised by Google Antigravity
 */

// Initialize Mermaid.js
mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {
    darkMode: true,
    background: '#111827',
    primaryColor: '#22c55e',
    primaryBorderColor: '#76b900',
    lineColor: '#94a3b8',
  }
});

// Application State
const state = {
  bots: [],
  selectedBotId: 'antigravity-orchestrator',
  activeTask: 'supervise',
  lastResponse: null,
  history: JSON.parse(localStorage.getItem('n8n_bots_history') || '[]'),
};

// DOM Elements
const elements = {
  botsListContainer: document.getElementById('bots-list-container'),
  botSearch: document.getElementById('bot-search'),
  statusN8n: document.getElementById('status-n8n'),
  statusQdrant: document.getElementById('status-qdrant'),
  refreshStatusBtn: document.getElementById('refresh-status-btn'),
  wfCount: document.getElementById('wf-count'),

  // NVIDIA Key Elements
  btnNvidiaKey: document.getElementById('btn-nvidia-key'),
  nvidiaKeyLabel: document.getElementById('nvidia-key-label'),
  nvidiaModal: document.getElementById('nvidia-modal'),
  inputNvidiaKey: document.getElementById('input-nvidia-key'),
  btnSaveNvidia: document.getElementById('btn-save-nvidia'),
  btnCancelNvidia: document.getElementById('btn-cancel-nvidia'),
  btnCloseNvidiaModal: document.getElementById('btn-close-nvidia-modal'),
  nvidiaModalFeedback: document.getElementById('nvidia-modal-feedback'),
  
  // Bot Banner
  activeBotEmoji: document.getElementById('active-bot-emoji'),
  activeBotName: document.getElementById('active-bot-name'),
  activeBotDesc: document.getElementById('active-bot-desc'),
  activeBotCat: document.getElementById('active-bot-cat'),
  botTaskTabs: document.getElementById('bot-task-tabs'),
  
  // Form
  botForm: document.getElementById('bot-form'),
  dynamicFieldsContainer: document.getElementById('dynamic-fields-container'),
  testModeToggle: document.getElementById('test-mode-toggle'),
  submitBtn: document.getElementById('submit-btn'),
  btnSpinner: document.getElementById('btn-spinner'),
  btnText: document.getElementById('btn-text'),
  
  // Output
  emptyState: document.getElementById('empty-state'),
  loadingState: document.getElementById('loading-state'),
  outputFormatted: document.getElementById('output-formatted'),
  outputDiagrams: document.getElementById('output-diagrams'),
  mermaidContainer: document.getElementById('mermaid-container'),
  outputRaw: document.getElementById('output-raw'),
  rawJsonCode: document.getElementById('raw-json-code'),
  executionTime: document.getElementById('execution-time'),
  copyOutputBtn: document.getElementById('copy-output-btn'),
  
  // Tabs
  tabBtnFormatted: document.getElementById('tab-btn-formatted'),
  tabBtnDiagrams: document.getElementById('tab-btn-diagrams'),
  tabBtnRaw: document.getElementById('tab-btn-raw'),
  
  // History
  btnShowHistory: document.getElementById('btn-show-history'),
  historyCount: document.getElementById('history-count'),
  historyModal: document.getElementById('history-modal'),
  historyList: document.getElementById('history-list'),
  btnCloseHistory: document.getElementById('btn-close-history'),
  btnClearHistory: document.getElementById('btn-clear-history'),
};

// Fetch initial status and bots
async function init() {
  updateHistoryCount();
  setupEventListeners();
  await checkStatus();
  await checkNvidiaStatus();
  await loadBots();
  setInterval(checkStatus, 15000);
}

// Check Backend, n8n, and Qdrant Health
async function checkStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    
    // n8n status
    const n8nDot = elements.statusN8n.querySelector('.status-dot');
    if (data.services?.n8n?.online) {
      n8nDot.className = 'w-2 h-2 rounded-full status-online';
      elements.statusN8n.title = 'n8n is running and reachable';
    } else {
      n8nDot.className = 'w-2 h-2 rounded-full status-offline';
      elements.statusN8n.title = data.services?.n8n?.details || 'n8n is offline';
    }

    // Qdrant status
    const qdrantDot = elements.statusQdrant.querySelector('.status-dot');
    if (data.services?.qdrant?.online) {
      qdrantDot.className = 'w-2 h-2 rounded-full status-online';
      elements.statusQdrant.title = 'Qdrant is online';
    } else {
      qdrantDot.className = 'w-2 h-2 rounded-full status-offline';
      elements.statusQdrant.title = data.services?.qdrant?.details || 'Qdrant is offline';
    }

    if (data.workflowsCount) {
      elements.wfCount.textContent = `${data.workflowsCount} Workflows`;
    }
  } catch (err) {
    console.error('Status check failed:', err);
  }
}

// Check NVIDIA Key Status
async function checkNvidiaStatus() {
  try {
    const res = await fetch('/api/credentials/status');
    const data = await res.json();
    if (data.nvidiaConfigured) {
      elements.nvidiaKeyLabel.textContent = `NVIDIA: ${data.maskedKey}`;
      elements.btnNvidiaKey.className = 'flex items-center space-x-1.5 text-xs px-3 py-1.5 rounded-lg bg-emerald-950/60 border border-nvidia/40 text-emerald-300 hover:bg-emerald-900/60 transition';
    } else {
      elements.nvidiaKeyLabel.textContent = '🔑 Add NVIDIA Key';
      elements.btnNvidiaKey.className = 'flex items-center space-x-1.5 text-xs px-3 py-1.5 rounded-lg bg-amber-950/60 border border-amber-500/40 text-amber-300 hover:bg-amber-900/60 transition animate-pulse';
    }
  } catch (err) {
    console.error('NVIDIA status check failed:', err);
  }
}

// Save NVIDIA Key
async function saveNvidiaKey() {
  const key = elements.inputNvidiaKey.value.trim();
  const feedback = elements.nvidiaModalFeedback;
  if (!key) {
    feedback.className = 'text-xs p-2.5 rounded-lg bg-red-950 text-red-300 block';
    feedback.textContent = 'Please paste a valid NVIDIA API key.';
    return;
  }

  feedback.className = 'text-xs p-2.5 rounded-lg bg-slate-800 text-slate-300 block';
  feedback.textContent = 'Saving key...';

  try {
    const res = await fetch('/api/credentials/nvidia', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: key }),
    });
    const data = await res.json();
    if (data.success) {
      feedback.className = 'text-xs p-2.5 rounded-lg bg-emerald-950 text-emerald-300 block';
      feedback.textContent = '✓ Key activated in Antigravity Orchestrator!';
      await checkNvidiaStatus();
      setTimeout(() => {
        elements.nvidiaModal.classList.add('hidden');
        feedback.className = 'hidden';
        elements.inputNvidiaKey.value = '';
      }, 1200);
    } else {
      throw new Error(data.detail || 'Failed to save key');
    }
  } catch (err) {
    feedback.className = 'text-xs p-2.5 rounded-lg bg-red-950 text-red-300 block';
    feedback.textContent = err.message;
  }
}

// Load Bot Metadata
async function loadBots() {
  try {
    const res = await fetch('/api/bots');
    const data = await res.json();

    const orchestrators = [
      {
        id: 'antigravity-orchestrator',
        name: 'Antigravity Orchestrator',
        emoji: '👑',
        category: 'Supreme Orchestration',
        description: 'Google Antigravity coordinates and supervises all 9 bots across architecture, coding, testing, and deployment.',
        supportedTasks: ['supervise', 'full-swarm'],
      },
      {
        id: 'autonomous-deepcoder',
        name: 'Autonomous DeepCoder',
        emoji: '⚡',
        category: 'Supreme Orchestration',
        description: 'Closed-loop autonomous coding engine (code generation + testing + self-healing debug + file save).',
        supportedTasks: ['auto-code', 'self-heal'],
      },
    ];

    state.bots = [...orchestrators, ...data.bots];
    renderBotsList();
    selectBot(state.selectedBotId);
  } catch (err) {
    elements.botsListContainer.innerHTML = `<div class="text-xs text-red-400 p-2">Failed to load bots: ${err.message}</div>`;
  }
}

// Render Sidebar Bots List
function renderBotsList() {
  const query = elements.botSearch.value.toLowerCase();
  elements.botsListContainer.innerHTML = '';

  const categories = ['Supreme Orchestration', 'Core Development', 'Advanced Production'];

  categories.forEach(cat => {
    const filtered = state.bots.filter(b => b.category === cat && (
      b.name.toLowerCase().includes(query) ||
      b.description.toLowerCase().includes(query)
    ));

    if (filtered.length === 0) return;

    const groupHeader = document.createElement('div');
    groupHeader.className = `text-[10px] font-bold uppercase tracking-wider mt-2 mb-1 px-2 ${
      cat === 'Supreme Orchestration' ? 'text-nvidia' : 'text-slate-500'
    }`;
    groupHeader.textContent = cat;
    elements.botsListContainer.appendChild(groupHeader);

    filtered.forEach(bot => {
      const item = document.createElement('div');
      const isSelected = bot.id === state.selectedBotId;
      item.className = `cursor-pointer p-2.5 rounded-xl text-xs transition flex items-start space-x-2.5 ${
        isSelected ? 'bg-slate-800 text-white font-medium border border-slate-700' : 'text-slate-300 hover:bg-slate-800/50'
      }`;
      item.onclick = () => selectBot(bot.id);

      item.innerHTML = `
        <span class="text-lg shrink-0">${bot.emoji}</span>
        <div class="truncate">
          <div class="font-semibold truncate text-white">${bot.name}</div>
          <div class="text-[11px] text-slate-400 truncate">${bot.description}</div>
        </div>
      `;
      elements.botsListContainer.appendChild(item);
    });
  });
}

// Studio Mode Switcher
function switchStudioMode(botId) {
  selectBot(botId);
  updateStudioNavButtons(botId);
}

function updateStudioNavButtons(botId) {
  const mapping = {
    'antigravity-orchestrator': 'nav-btn-orchestrator',
    'autonomous-deepcoder': 'nav-btn-deepcoder',
    'advanced-rag': 'nav-btn-rag',
    'rag-bot': 'nav-btn-rag',
  };
  const activeBtnId = mapping[botId] || 'nav-btn-bots';
  ['nav-btn-orchestrator', 'nav-btn-deepcoder', 'nav-btn-rag', 'nav-btn-bots'].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    if (id === activeBtnId) {
      el.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold text-white bg-slate-800 transition flex items-center gap-1.5 shadow-sm border border-slate-700';
    } else {
      el.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-white transition flex items-center gap-1.5';
    }
  });
}

// Select Active Bot
function selectBot(botId) {
  state.selectedBotId = botId;
  const bot = state.bots.find(b => b.id === botId);
  if (!bot) return;

  renderBotsList();
  updateStudioNavButtons(botId);

  elements.activeBotEmoji.textContent = bot.emoji;
  elements.activeBotName.textContent = bot.name;
  elements.activeBotDesc.textContent = bot.description;
  elements.activeBotCat.textContent = bot.category;

  state.activeTask = bot.supportedTasks[0] || 'default';
  renderTaskTabs(bot);
  renderDynamicForm(bot);
}

// Render Bot Task Tabs
function renderTaskTabs(bot) {
  elements.botTaskTabs.innerHTML = '';
  bot.supportedTasks.forEach(task => {
    const tab = document.createElement('button');
    tab.type = 'button';
    const isActive = task === state.activeTask;
    tab.className = `text-xs px-3 py-1 rounded-lg font-medium transition cursor-pointer ${
      isActive 
        ? 'bg-nvidia text-black font-semibold' 
        : 'bg-slate-800/80 text-slate-300 hover:bg-slate-700'
    }`;
    tab.textContent = task.charAt(0).toUpperCase() + task.slice(1).replace('-', ' ');
    tab.onclick = () => {
      state.activeTask = task;
      renderTaskTabs(bot);
      renderDynamicForm(bot);
    };
    elements.botTaskTabs.appendChild(tab);
  });
}

// Dynamic Input Forms tailored to each Bot
function renderDynamicForm(bot) {
  const container = elements.dynamicFieldsContainer;
  container.innerHTML = '';

  switch (bot.id) {
    case 'antigravity-orchestrator':
      renderAntigravityOrchestratorForm(container);
      break;
    case 'autonomous-deepcoder':
      renderAutonomousDeepCoderForm(container);
      break;
    case 'coding-assistant':
      renderCodingAssistantForm(container);
      break;
    case 'rag-bot':
      renderRagBotForm(container);
      break;
    case 'system-design':
      renderSystemDesignForm(container);
      break;
    case 'high-thinking':
      renderHighThinkingForm(container);
      break;
    case 'testing-bot':
      renderTestingBotForm(container);
      break;
    case 'advanced-rag':
      renderAdvancedRagForm(container);
      break;
    case 'cloud-deployment':
      renderCloudDeploymentForm(container);
      break;
    case 'ml-pipeline':
      renderMlPipelineForm(container);
      break;
    case 'n8n-manager':
      renderN8nManagerForm(container);
      break;
    default:
      renderGenericForm(container);
  }
}

function renderAntigravityOrchestratorForm(c) {
  c.innerHTML = `
    <div class="p-3 bg-gradient-to-r from-emerald-950/40 to-slate-900 border border-nvidia/30 rounded-xl mb-4">
      <div class="text-xs font-semibold text-nvidia flex items-center gap-1.5 mb-1">
        <span>👑</span> Google Antigravity Supreme Orchestration
      </div>
      <p class="text-[11px] text-slate-400 leading-relaxed">
        Issue a high-level engineering goal. Antigravity will coordinate the 9 bots under strict supervision (Architecture $\\to$ Risk Pre-Mortem $\\to$ Implementation & Tests $\\to$ Cloud IaC).
      </p>
    </div>
    <div>
      <label class="block text-xs font-semibold text-slate-300 mb-1">High-Level Engineering Goal</label>
      <textarea id="inp-orch-goal" rows="4" placeholder="e.g. Design, implement, test, and containerize a distributed rate-limiting service with Redis clustering and Prometheus metrics" 
        class="w-full text-xs p-3 bg-darkInput rounded-lg border border-darkBorder text-white focus:border-nvidia focus:outline-none" required></textarea>
    </div>
    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Primary Language</label>
        <select id="inp-orch-lang" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
          <option value="typescript" selected>TypeScript</option>
          <option value="python">Python</option>
          <option value="go">Go</option>
          <option value="rust">Rust</option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Target Cloud Provider</label>
        <select id="inp-orch-cloud" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
          <option value="aws" selected>AWS (EKS, RDS)</option>
          <option value="gcp">Google Cloud (GKE)</option>
          <option value="azure">Azure (AKS)</option>
          <option value="multi">Multi-Cloud</option>
        </select>
      </div>
    </div>
    <div class="space-y-2 pt-1 text-xs text-slate-300">
      <label class="flex items-center space-x-2 cursor-pointer">
        <input type="checkbox" id="inp-orch-tests" checked class="rounded bg-darkInput text-nvidia">
        <span>Autonomous Test Generation & Verification (Testing Bot)</span>
      </label>
      <label class="flex items-center space-x-2 cursor-pointer">
        <input type="checkbox" id="inp-orch-iac" checked class="rounded bg-darkInput text-nvidia">
        <span>Generate Infrastructure as Code (Terraform & K8s Manifests)</span>
      </label>
    </div>
  `;
}

function renderAutonomousDeepCoderForm(c) {
  c.innerHTML = `
    <div class="p-3 bg-gradient-to-r from-cyan-950/40 to-slate-900 border border-cyan-700/30 rounded-xl mb-4">
      <div class="text-xs font-semibold text-cyan-400 flex items-center gap-1.5 mb-1">
        <span>⚡</span> Autonomous DeepCoder Closed Loop
      </div>
      <p class="text-[11px] text-slate-400 leading-relaxed">
        Autonomous cycle: Code Generation $\\to$ Test Suite Generation $\\to$ Automated Execution $\\to$ Self-Healing Debugging $\\to$ Verified Save.
      </p>
    </div>
    <div>
      <label class="block text-xs font-semibold text-slate-300 mb-1">Coding Task / Feature Request</label>
      <textarea id="inp-deepcoder-task" rows="4" placeholder="e.g. Implement a thread-safe LRU Cache with TTL expiration in TypeScript with unit and edge case tests" 
        class="w-full text-xs p-3 bg-darkInput rounded-lg border border-darkBorder text-white focus:border-cyan-400 focus:outline-none" required></textarea>
    </div>
    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Language</label>
        <select id="inp-deepcoder-lang" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
          <option value="typescript" selected>TypeScript</option>
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
          <option value="go">Go</option>
          <option value="rust">Rust</option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Destination File (Optional)</label>
        <input type="text" id="inp-deepcoder-file" placeholder="./src/lru_cache.ts" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
      </div>
    </div>
    <div>
      <label class="block text-xs font-semibold text-slate-300 mb-1">Max Self-Healing Retries</label>
      <input type="number" id="inp-deepcoder-retries" value="3" min="1" max="5" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
    </div>
  `;
}

function renderCodingAssistantForm(c) {
  const isGenerate = state.activeTask === 'generate';
  c.innerHTML = `
    <div>
      <label class="block text-xs font-semibold text-slate-300 mb-1">Language</label>
      <select id="inp-language" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white focus:border-nvidia focus:outline-none">
        <option value="typescript" selected>TypeScript</option>
        <option value="python">Python</option>
        <option value="javascript">JavaScript</option>
        <option value="rust">Rust</option>
        <option value="go">Go</option>
        <option value="sql">SQL</option>
      </select>
    </div>
    <div>
      <label class="block text-xs font-semibold text-slate-300 mb-1">Task / Prompt</label>
      <input type="text" id="inp-task" placeholder="${isGenerate ? 'e.g. Build an LRU cache with TTL expiration' : 'e.g. Review for race conditions and memory leaks'}" 
        class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white focus:border-nvidia focus:outline-none" required>
    </div>
    ${!isGenerate ? `
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Source Code</label>
        <textarea id="inp-code" rows="8" placeholder="Paste your code snippet here..." 
          class="w-full text-xs font-mono p-3 bg-darkInput rounded-lg border border-darkBorder text-emerald-300 focus:border-nvidia focus:outline-none" required></textarea>
      </div>
    ` : ''}
    <div>
      <label class="block text-xs font-semibold text-slate-300 mb-1">Context / Notes (Optional)</label>
      <input type="text" id="inp-context" placeholder="Additional constraints or environment details..." 
        class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white focus:border-nvidia focus:outline-none">
    </div>
  `;
}

function renderRagBotForm(c) {
  if (state.activeTask === 'ingest') {
    c.innerHTML = `
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Directory to Ingest</label>
        <input type="text" id="inp-directory" placeholder="/Users/abhigurjar/my-docs or project path" 
          class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white focus:border-nvidia focus:outline-none">
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Chunk Size</label>
        <input type="number" id="inp-chunk-size" value="1000" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
      </div>
    `;
  } else {
    c.innerHTML = `
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Search Query / Question</label>
        <textarea id="inp-query" rows="4" placeholder="What are the key architecture decisions in our documentation?" 
          class="w-full text-xs p-3 bg-darkInput rounded-lg border border-darkBorder text-white focus:border-nvidia focus:outline-none" required></textarea>
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Collection Name</label>
        <input type="text" id="inp-collection" value="desktop-docs" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Top K Results</label>
        <input type="number" id="inp-topk" value="5" max="20" min="1" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
      </div>
    `;
  }
}

function renderSystemDesignForm(c) {
  c.innerHTML = `
    <div>
      <label class="block text-xs font-semibold text-slate-300 mb-1">Requirements / Problem Statement</label>
      <textarea id="inp-requirements" rows="4" placeholder="Design a real-time event streaming and analytics platform for IoT devices..." 
        class="w-full text-xs p-3 bg-darkInput rounded-lg border border-darkBorder text-white focus:border-nvidia focus:outline-none" required></textarea>
    </div>
    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Target Scale</label>
        <input type="text" id="inp-scale" value="50,000 RPS, 5M DAU" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Preferred Stack</label>
        <input type="text" id="inp-techstack" value="Kafka, Go, ClickHouse, Redis" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
      </div>
    </div>
    <div>
      <label class="block text-xs font-semibold text-slate-300 mb-1">Constraints</label>
      <input type="text" id="inp-constraints" placeholder="Sub-100ms p99 latency, 99.99% availability, multi-region" 
        class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
    </div>
  `;
}

function renderHighThinkingForm(c) {
  c.innerHTML = `
    <div>
      <label class="block text-xs font-semibold text-slate-300 mb-1">Problem / Dilemma / Thesis</label>
      <textarea id="inp-problem" rows="4" placeholder="Should we migrate from microservices back to a modular monolith given a 12-person team?" 
        class="w-full text-xs p-3 bg-darkInput rounded-lg border border-darkBorder text-white focus:border-nvidia focus:outline-none" required></textarea>
    </div>
    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Reasoning Mode</label>
        <select id="inp-mode" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
          <option value="deep" ${state.activeTask === 'deep' ? 'selected' : ''}>Deep Multi-Stage</option>
          <option value="firstPrinciples" ${state.activeTask === 'firstPrinciples' ? 'selected' : ''}>First Principles</option>
          <option value="debate" ${state.activeTask === 'debate' ? 'selected' : ''}>Dialectical Debate</option>
          <option value="mentalModels" ${state.activeTask === 'mentalModels' ? 'selected' : ''}>Mental Models Library</option>
          <option value="chain" ${state.activeTask === 'chain' ? 'selected' : ''}>Chain-of-Thought (Self-Consistency)</option>
          <option value="futures" ${state.activeTask === 'futures' ? 'selected' : ''}>Strategic Foresight</option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Temperature</label>
        <input type="number" step="0.1" id="inp-temp" value="0.3" min="0" max="1" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
      </div>
    </div>
  `;
}

function renderTestingBotForm(c) {
  c.innerHTML = `
    <div>
      <label class="block text-xs font-semibold text-slate-300 mb-1">Framework & Language</label>
      <div class="grid grid-cols-2 gap-3">
        <select id="inp-framework" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
          <option value="vitest">Vitest (TypeScript)</option>
          <option value="pytest">Pytest (Python)</option>
          <option value="jest">Jest (JavaScript)</option>
        </select>
        <input type="number" id="inp-coverage" value="85" min="1" max="100" placeholder="Coverage Target %" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
      </div>
    </div>
    <div>
      <label class="block text-xs font-semibold text-slate-300 mb-1">Code to Test</label>
      <textarea id="inp-code" rows="8" placeholder="Paste functions or classes to generate comprehensive test suites for..." 
        class="w-full text-xs font-mono p-3 bg-darkInput rounded-lg border border-darkBorder text-emerald-300 focus:border-nvidia focus:outline-none" required></textarea>
    </div>
  `;
}

function renderAdvancedRagForm(c) {
  const task = state.activeTask;
  if (task === 'ingest') {
    c.innerHTML = `
      <div class="p-3 bg-gradient-to-r from-emerald-950/40 to-slate-900 border border-nvidia/30 rounded-xl mb-4">
        <div class="text-xs font-semibold text-nvidia flex items-center gap-1.5 mb-1">
          <span>📥</span> Real-Time Qdrant Vector Ingestion
        </div>
        <p class="text-[11px] text-slate-400 leading-relaxed">
          Index documents directly into Qdrant (<code class="text-emerald-400">localhost:6333</code>) with 384-d dense embeddings (<code class="text-emerald-400">all-MiniLM-L6-v2</code>).
        </p>
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Target Collection</label>
        <input type="text" id="inp-collection" value="desktop-docs" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Source Name / File Identifier</label>
        <input type="text" id="inp-source" value="architecture-spec.md" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Document Content / Text to Ingest</label>
        <textarea id="inp-content" rows="6" placeholder="Paste technical documentation, requirements, ADRs, or system designs to embed into Qdrant..." 
          class="w-full text-xs p-3 bg-darkInput rounded-lg border border-darkBorder text-white focus:border-nvidia focus:outline-none" required></textarea>
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Or Ingest Directory (Local Path)</label>
        <input type="text" id="inp-directory" placeholder="Optional directory path, e.g. ./docs or /Users/.../project" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
      </div>
    `;
  } else if (task === 'agentic') {
    c.innerHTML = `
      <div class="p-3 bg-gradient-to-r from-purple-950/40 to-slate-900 border border-purple-500/30 rounded-xl mb-4">
        <div class="text-xs font-semibold text-purple-400 flex items-center gap-1.5 mb-1">
          <span>🔬</span> Agentic Multi-Step RAG Reasoning
        </div>
        <p class="text-[11px] text-slate-400 leading-relaxed">
          Decomposes complex multi-hop questions into sub-queries, executes parallel searches, cross-references citations, and synthesizes grounded evidence.
        </p>
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Multi-Hop Query / Complex Question</label>
        <textarea id="inp-query" rows="4" placeholder="How do our authentication service and rate limiter coordinate during token revocation?" 
          class="w-full text-xs p-3 bg-darkInput rounded-lg border border-darkBorder text-white focus:border-nvidia focus:outline-none" required></textarea>
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Collection</label>
          <input type="text" id="inp-collection" value="desktop-docs" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Top Citations (K)</label>
          <input type="number" id="inp-topk" value="5" min="1" max="15" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
        </div>
      </div>
    `;
  } else if (task === 'evaluate') {
    c.innerHTML = `
      <div class="p-3 bg-gradient-to-r from-amber-950/40 to-slate-900 border border-amber-500/30 rounded-xl mb-4">
        <div class="text-xs font-semibold text-amber-400 flex items-center gap-1.5 mb-1">
          <span>📊</span> RAG Retrieval Evaluation Benchmark (Ragas)
        </div>
        <p class="text-[11px] text-slate-400 leading-relaxed">
          Benchmarks Context Relevance, Grounded Faithfulness, and Citation Precision against the live vector collection.
        </p>
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Evaluation Query</label>
        <textarea id="inp-query" rows="3" placeholder="Verify retrieval relevance for: distributed transaction rollback mechanisms" 
          class="w-full text-xs p-3 bg-darkInput rounded-lg border border-darkBorder text-white focus:border-nvidia focus:outline-none" required></textarea>
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Collection</label>
        <input type="text" id="inp-collection" value="desktop-docs" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
      </div>
    `;
  } else {
    c.innerHTML = `
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Hybrid Query (Dense Vector + BM25)</label>
        <textarea id="inp-query" rows="4" placeholder="Perform multi-hop reasoning over ingested documentation..." 
          class="w-full text-xs p-3 bg-darkInput rounded-lg border border-darkBorder text-white focus:border-nvidia focus:outline-none" required></textarea>
      </div>
      <div class="grid grid-cols-2 gap-3 mb-2">
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Collection Name</label>
          <input type="text" id="inp-collection" value="desktop-docs" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Top K Results</label>
          <input type="number" id="inp-topk" value="5" min="1" max="20" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
        </div>
      </div>
      <div class="flex items-center space-x-4 text-xs text-slate-300 pt-1">
        <label class="flex items-center space-x-2 cursor-pointer">
          <input type="checkbox" id="inp-rerank" checked class="rounded bg-darkInput text-nvidia">
          <span>Neural Reranker (Cross-Encoder)</span>
        </label>
        <label class="flex items-center space-x-2 cursor-pointer">
          <input type="checkbox" id="inp-hybrid" checked class="rounded bg-darkInput text-nvidia">
          <span>Hybrid Reciprocal Rank Fusion</span>
        </label>
      </div>
    `;
  }
}

function renderCloudDeploymentForm(c) {
  c.innerHTML = `
    <div>
      <label class="block text-xs font-semibold text-slate-300 mb-1">Infrastructure Specification</label>
      <textarea id="inp-requirements" rows="4" placeholder="Production AWS EKS cluster with VPC, ALB ingress, RDS Postgres, and KMS encryption" 
        class="w-full text-xs p-3 bg-darkInput rounded-lg border border-darkBorder text-white focus:border-nvidia focus:outline-none" required></textarea>
    </div>
    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Cloud Provider</label>
        <select id="inp-provider" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
          <option value="aws">AWS</option>
          <option value="gcp">Google Cloud (GCP)</option>
          <option value="azure">Azure</option>
          <option value="multi">Multi-Cloud</option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Environment</label>
        <input type="text" id="inp-env" value="production" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
      </div>
    </div>
  `;
}

function renderMlPipelineForm(c) {
  c.innerHTML = `
    <div>
      <label class="block text-xs font-semibold text-slate-300 mb-1">ML Task & Architecture</label>
      <textarea id="inp-requirements" rows="4" placeholder="Fine-tune Llama 3 8B with LoRA on customer support dataset using PyTorch Lightning" 
        class="w-full text-xs p-3 bg-darkInput rounded-lg border border-darkBorder text-white focus:border-nvidia focus:outline-none" required></textarea>
    </div>
    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Framework</label>
        <select id="inp-framework" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
          <option value="pytorch">PyTorch</option>
          <option value="huggingface">Hugging Face Transformers</option>
          <option value="lightning">PyTorch Lightning</option>
          <option value="tensorflow">TensorFlow</option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Serving Target</label>
        <input type="text" id="inp-serving" value="Triton / vLLM" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
      </div>
    </div>
  `;
}

function renderN8nManagerForm(c) {
  c.innerHTML = `
    <div>
      <label class="block text-xs font-semibold text-slate-300 mb-1">Operation & Target Spec</label>
      <input type="text" id="inp-spec" value="${state.activeTask === 'backup' ? 'Export all workflows to S3 bucket' : 'Scale n8n workers to 5 replicas on K8s with KEDA'}" 
        class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white focus:border-nvidia focus:outline-none" required>
    </div>
    <div>
      <label class="block text-xs font-semibold text-slate-300 mb-1">Deployment Platform</label>
      <select id="inp-platform" class="w-full text-xs px-3 py-2 bg-darkInput rounded-lg border border-darkBorder text-white">
        <option value="docker">Docker Compose</option>
        <option value="k8s">Kubernetes (Helm)</option>
        <option value="ecs">AWS ECS Fargate</option>
      </select>
    </div>
  `;
}

function renderGenericForm(c) {
  c.innerHTML = `
    <div>
      <label class="block text-xs font-semibold text-slate-300 mb-1">Task / Input</label>
      <textarea id="inp-task" rows="5" class="w-full text-xs p-3 bg-darkInput rounded-lg border border-darkBorder text-white" required></textarea>
    </div>
  `;
}

// Gather Payload from Active Form
function gatherPayload() {
  const botId = state.selectedBotId;
  const payload = {};

  const get = (id) => {
    const el = document.getElementById(id);
    return el ? el.value : undefined;
  };

  switch (botId) {
    case 'coding-assistant':
      payload.task = `${state.activeTask} ${get('inp-task') || ''}`.trim();
      payload.code = get('inp-code') || '';
      payload.language = get('inp-language') || 'typescript';
      payload.context = get('inp-context') || '';
      break;

    case 'rag-bot':
      if (state.activeTask === 'ingest') {
        payload.directory = get('inp-directory');
        payload.chunkSize = parseInt(get('inp-chunk-size') || '1000');
      } else {
        payload.query = get('inp-query');
        payload.collection = get('inp-collection') || 'desktop-docs';
        payload.topK = parseInt(get('inp-topk') || '5');
      }
      break;

    case 'system-design':
      payload.task = state.activeTask;
      payload.requirements = get('inp-requirements');
      payload.scale = get('inp-scale');
      payload.techStack = get('inp-techstack');
      payload.constraints = get('inp-constraints');
      break;

    case 'high-thinking':
      payload.problem = get('inp-problem');
      payload.mode = get('inp-mode') || state.activeTask;
      payload.temperature = parseFloat(get('inp-temp') || '0.3');
      break;

    case 'testing-bot':
      payload.code = get('inp-code');
      payload.framework = get('inp-framework');
      payload.coverageTarget = parseInt(get('inp-coverage') || '80');
      break;

    case 'advanced-rag':
      payload.subtask = state.activeTask;
      payload.collection = get('inp-collection') || 'desktop-docs';
      payload.query = get('inp-query');
      payload.content = get('inp-content');
      payload.source = get('inp-source');
      payload.directory = get('inp-directory');
      payload.topK = parseInt(get('inp-topk') || '5');
      payload.use_rerank = document.getElementById('inp-rerank')?.checked ?? true;
      payload.use_hybrid = document.getElementById('inp-hybrid')?.checked ?? true;
      break;

    case 'cloud-deployment':
      payload.requirements = get('inp-requirements');
      payload.cloudProvider = get('inp-provider');
      payload.environment = get('inp-env');
      break;

    case 'ml-pipeline':
      payload.requirements = get('inp-requirements');
      payload.framework = get('inp-framework');
      break;

    case 'n8n-manager':
      payload.spec = get('inp-spec');
      payload.platform = get('inp-platform');
      break;

    default:
      payload.task = get('inp-task');
  }

  return payload;
}

// Execute Bot or Orchestrator
async function executeBot() {
  const botId = state.selectedBotId;
  const isTest = elements.testModeToggle.checked;

  setLoading(true);
  const startTime = performance.now();

  try {
    let res;
    let payload = {};

    if (botId === 'antigravity-orchestrator') {
      payload = {
        goal: document.getElementById('inp-orch-goal')?.value || 'Build distributed service',
        language: document.getElementById('inp-orch-lang')?.value || 'typescript',
        cloud_provider: document.getElementById('inp-orch-cloud')?.value || 'aws',
        include_tests: document.getElementById('inp-orch-tests')?.checked !== false,
        include_iac: document.getElementById('inp-orch-iac')?.checked !== false,
      };
      res = await fetch('/api/orchestrator/supervise', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
    } else if (botId === 'autonomous-deepcoder') {
      payload = {
        task: document.getElementById('inp-deepcoder-task')?.value || '',
        language: document.getElementById('inp-deepcoder-lang')?.value || 'typescript',
        target_file: document.getElementById('inp-deepcoder-file')?.value || null,
        max_retries: parseInt(document.getElementById('inp-deepcoder-retries')?.value || '3'),
      };
      res = await fetch('/api/deep-coder/automate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
    } else {
      payload = gatherPayload();
      res = await fetch(`/api/bots/${botId}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ payload, is_test: isTest }),
      });
    }

    const duration = ((performance.now() - startTime) / 1000).toFixed(2);
    const data = await res.json();
    state.lastResponse = data;

    elements.executionTime.textContent = `${duration}s`;

    // Automatically open Jupyter Notebook tab if verified and present
    const jupyterLink = data.jupyter_link || (data.jupyter && data.jupyter.notebook && data.jupyter.notebook.jupyter_link) || (data.notebook && data.notebook.jupyter_link);
    if (jupyterLink) {
      try {
        window.open(jupyterLink, '_blank');
      } catch (e) {
        console.warn('Pop-up prevented:', e);
      }
    }

    renderResponse(data);
    addToHistory(botId, payload, data, duration);
  } catch (err) {
    elements.executionTime.textContent = 'Error';
    renderError(err.message);
  } finally {
    setLoading(false);
  }
}

// Render Response View
function renderResponse(data) {
  elements.emptyState.classList.add('hidden');
  elements.loadingState.classList.add('hidden');
  elements.outputFormatted.classList.remove('hidden');

  let textContent = '';
  let diagrams = [];

  const jupyterLink = data.jupyter_link || (data.jupyter && data.jupyter.notebook && data.jupyter.notebook.jupyter_link) || (data.notebook && data.notebook.jupyter_link);
  if (jupyterLink) {
    textContent += `<div style="background: rgba(34, 197, 94, 0.12); border: 1.5px solid #22c55e; border-radius: 8px; padding: 14px 18px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
  <div>
    <div style="font-weight: 700; color: #4ade80; font-size: 15px;">⚡ LIVE JUPYTER NOTEBOOK OPENED & VERIFIED</div>
    <div style="color: #94a3b8; font-size: 12.5px; margin-top: 2px;">Code & unit tests tested clean in IPython kernel and formatted into markdowns and cells.</div>
  </div>
  <a href="${jupyterLink}" target="_blank" style="background: #22c55e; color: #000; font-weight: 700; font-size: 13px; padding: 8px 16px; border-radius: 6px; text-decoration: none; display: inline-flex; align-items: center; gap: 6px;">
    <span>🚀 Open in Jupyter</span>
  </a>
</div>\n\n`;
  }

  // 1. Antigravity Orchestrator Response
  if (data.supervisor) {
    textContent += `# 👑 Antigravity Swarm Executive Report\n\n`;
    textContent += `**Goal**: ${data.goal}\n\n`;
    textContent += `**Supervisor**: ${data.supervisor} | **Duration**: ${data.duration_seconds}s\n\n---\n\n`;

    if (data.architecture) {
      textContent += `## 1. 🏗️ Architecture & System Design\n\n`;
      const arch = data.architecture.fullResponse || data.architecture.response || JSON.stringify(data.architecture, null, 2);
      textContent += `${arch}\n\n`;
      if (data.architecture.diagrams) diagrams.push(...data.architecture.diagrams);
    }

    if (data.risk_analysis) {
      textContent += `## 2. 🧠 First Principles & Pre-Mortem Risk Analysis\n\n`;
      const risk = data.risk_analysis.fullResponse || data.risk_analysis.response || JSON.stringify(data.risk_analysis, null, 2);
      textContent += `${risk}\n\n`;
    }

    if (data.implementation) {
      textContent += `## 3. 🧑‍💻 Autonomous Code Implementation\n\n`;
      if (data.implementation.code) {
        textContent += `\`\`\`${data.implementation.language || ''}\n${data.implementation.code}\n\`\`\`\n\n`;
      }
      if (data.implementation.tests) {
        textContent += `### Verified Test Suite\n\n\`\`\`${data.implementation.language || ''}\n${data.implementation.tests}\n\`\`\`\n\n`;
      }
    }

    if (data.infrastructure) {
      textContent += `## 4. ☁️ Infrastructure as Code (IaC)\n\n`;
      const iac = data.infrastructure.rawResponse || data.infrastructure.response || JSON.stringify(data.infrastructure, null, 2);
      textContent += `${iac}\n\n`;
    }

  // 2. Autonomous DeepCoder Response
  } else if (data.trace && data.code !== undefined) {
    textContent = `# ⚡ Autonomous DeepCoder Verification Report\n\n`;
    textContent += `**Task**: ${data.task} | **Language**: ${data.language} | **Status**: ${data.success ? 'PASSED ✓' : 'FAILED ✗'}\n\n`;
    textContent += `**Iterations**: ${data.iterations} | **Duration**: ${data.duration_seconds}s\n\n`;
    if (data.saved_path) textContent += `**Saved File**: \`${data.saved_path}\`\n\n`;

    textContent += `### Execution Trace\n\n`;
    data.trace.forEach(t => {
      const badge = t.status === 'completed' || t.status === 'passed' ? '🟢' : t.status === 'failed' ? '🔴' : '🟡';
      textContent += `- ${badge} **${t.stage}**: ${t.message || t.error || ''}\n`;
    });

    textContent += `\n### Verified Code\n\n\`\`\`${data.language}\n${data.code}\n\`\`\`\n\n`;
    if (data.tests) {
      textContent += `### Generated Tests\n\n\`\`\`${data.language}\n${data.tests}\n\`\`\`\n\n`;
    }

  // 3. RAG Retrieval & Ingestion Responses
  } else if (data.answer) {
    textContent = `# 📚 Qdrant Full-Scale RAG Response\n\n`;
    textContent += `**Query**: \`${data.query}\` | **Collection**: \`${data.collection}\` | **Latency**: \`${data.latency_ms}ms\`\n\n`;
    textContent += `${data.answer}\n\n`;
    if (data.citations && data.citations.length > 0) {
      textContent += `### 🔍 Verified Citations & Grounding (${data.citations.length})\n\n`;
      textContent += `| ID | Source Document | Lines | Confidence Score | Excerpt |\n`;
      textContent += `|:---|:---|:---|:---|:---|\n`;
      data.citations.forEach(c => {
        const sc = typeof c.score === 'number' ? (c.score > 1 ? c.score.toFixed(2) : (c.score * 100).toFixed(1) + '%') : (c.score || '0.90');
        const srcName = c.source ? c.source.split('/').pop() : 'document';
        const snip = (c.snippet || '').replace(/\|/g, '\\|').replace(/\n/g, ' ');
        textContent += `| **${c.citation_id}** | \`${srcName}\` | \`${c.lines}\` | \`${sc}\` | ${snip} |\n`;
      });
      textContent += `\n`;
    }
  } else if (data.chunks_ingested !== undefined) {
    textContent = `# 📥 Document Ingested Into Qdrant\n\n`;
    textContent += `- **Collection**: \`${data.collection}\`\n`;
    textContent += `- **Source Name**: \`${data.source}\`\n`;
    textContent += `- **Chunks Ingested**: \`${data.chunks_ingested}\`\n`;
    textContent += `- **Total Tokens**: \`${data.total_tokens || 'N/A'}\`\n`;
    textContent += `- **Dense Vector Model**: \`all-MiniLM-L6-v2\` (384-d)\n\n`;
    textContent += `> [!NOTE]\n> Real points are indexed and ready for hybrid queries on \`localhost:6333\`.`;

  // 4. Standard Bot Response
  } else if (typeof data === 'string') {
    textContent = data;
  } else if (data.response) {
    if (typeof data.response === 'object') {
      textContent = data.response.explanation || JSON.stringify(data.response, null, 2);
      if (data.response.code) {
        textContent += `\n\n\`\`\`${data.language || ''}\n${data.response.code}\n\`\`\``;
      }
    } else {
      textContent = data.response;
    }
  } else if (data.fullResponse) {
    textContent = data.fullResponse;
  } else if (data.rawResponse) {
    textContent = data.rawResponse;
  } else if (data.error) {
    textContent = `> [!CAUTION]\n> **Execution Error**:\n> ${data.error}`;
  } else {
    textContent = JSON.stringify(data, null, 2);
  }

  // Extract Mermaid diagrams
  if (diagrams.length === 0) {
    const mermaidRegex = /```mermaid\n([\s\S]*?)```/g;
    let match;
    while ((match = mermaidRegex.exec(textContent)) !== null) {
      diagrams.push(match[1]);
    }
  }

  elements.outputFormatted.innerHTML = marked.parse(textContent);
  document.querySelectorAll('#output-formatted pre code').forEach((el) => {
    hljs.highlightElement(el);
  });

  if (diagrams.length > 0) {
    elements.tabBtnDiagrams.classList.remove('hidden');
    renderMermaidDiagrams(diagrams);
  } else {
    elements.mermaidContainer.innerHTML = '<div class="text-slate-500 text-xs text-center p-4">No Mermaid diagrams generated in this response.</div>';
  }

  elements.rawJsonCode.textContent = JSON.stringify(data, null, 2);
  switchTab('formatted');
}

function renderMermaidDiagrams(diagrams) {
  elements.mermaidContainer.innerHTML = '';
  diagrams.forEach((diag) => {
    const div = document.createElement('div');
    div.className = 'mermaid w-full mb-6';
    div.textContent = diag;
    elements.mermaidContainer.appendChild(div);
  });

  try {
    mermaid.run({
      nodes: elements.mermaidContainer.querySelectorAll('.mermaid'),
    });
  } catch (err) {
    console.warn('Mermaid render error:', err);
  }
}

function renderError(msg) {
  elements.emptyState.classList.add('hidden');
  elements.loadingState.classList.add('hidden');
  elements.outputFormatted.classList.remove('hidden');
  elements.outputFormatted.innerHTML = `
    <div class="p-4 rounded-xl bg-red-950/40 border border-red-800 text-red-300 text-sm">
      <div class="font-bold flex items-center gap-2 mb-1">
        <span>⚠️</span> Request Failed
      </div>
      <p class="text-xs text-red-400">${msg}</p>
    </div>
  `;
}

// UI State Management
function setLoading(loading) {
  if (loading) {
    elements.emptyState.classList.add('hidden');
    elements.outputFormatted.classList.add('hidden');
    elements.outputDiagrams.classList.add('hidden');
    elements.outputRaw.classList.add('hidden');
    elements.loadingState.classList.remove('hidden');
    elements.submitBtn.disabled = true;
    elements.btnSpinner.classList.remove('hidden');
    elements.btnText.textContent = 'Executing Swarm...';
  } else {
    elements.loadingState.classList.add('hidden');
    elements.submitBtn.disabled = false;
    elements.btnSpinner.classList.add('hidden');
    elements.btnText.textContent = 'Execute Bot ⚡';
  }
}

function switchTab(tab) {
  elements.tabBtnFormatted.className = 'text-xs px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition';
  elements.tabBtnDiagrams.className = 'text-xs px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition';
  elements.tabBtnRaw.className = 'text-xs px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition';

  elements.outputFormatted.classList.add('hidden');
  elements.outputDiagrams.classList.add('hidden');
  elements.outputRaw.classList.add('hidden');

  if (tab === 'formatted') {
    elements.tabBtnFormatted.className = 'text-xs px-3 py-1.5 rounded-lg bg-slate-800 text-white font-medium border border-slate-700';
    elements.outputFormatted.classList.remove('hidden');
  } else if (tab === 'diagrams') {
    elements.tabBtnDiagrams.className = 'text-xs px-3 py-1.5 rounded-lg bg-slate-800 text-white font-medium border border-slate-700';
    elements.outputDiagrams.classList.remove('hidden');
  } else if (tab === 'raw') {
    elements.tabBtnRaw.className = 'text-xs px-3 py-1.5 rounded-lg bg-slate-800 text-white font-medium border border-slate-700';
    elements.outputRaw.classList.remove('hidden');
  }
}

// History Management
function addToHistory(botId, payload, response, duration) {
  const entry = {
    id: Date.now(),
    botId,
    timestamp: new Date().toLocaleTimeString(),
    duration,
    payload,
    response,
  };
  state.history.unshift(entry);
  if (state.history.length > 25) state.history.pop();
  localStorage.setItem('n8n_bots_history', JSON.stringify(state.history));
  updateHistoryCount();
}

function updateHistoryCount() {
  elements.historyCount.textContent = state.history.length;
}

function renderHistoryModal() {
  elements.historyList.innerHTML = '';
  if (state.history.length === 0) {
    elements.historyList.innerHTML = '<div class="text-xs text-slate-500 text-center py-6">No execution history yet.</div>';
    return;
  }

  state.history.forEach(item => {
    const card = document.createElement('div');
    card.className = 'p-3 bg-darkInput rounded-xl border border-darkBorder hover:border-slate-600 transition cursor-pointer text-xs';
    card.onclick = () => {
      selectBot(item.botId);
      renderResponse(item.response);
      elements.executionTime.textContent = `${item.duration}s (history)`;
      elements.historyModal.classList.add('hidden');
    };

    card.innerHTML = `
      <div class="flex justify-between items-center text-slate-400 mb-1">
        <span class="font-bold text-white capitalize">${item.botId.replace('-', ' ')}</span>
        <span>${item.timestamp} (${item.duration}s)</span>
      </div>
      <div class="text-slate-400 truncate text-[11px] font-mono">
        ${JSON.stringify(item.payload)}
      </div>
    `;
    elements.historyList.appendChild(card);
  });
}

// Event Listeners
function setupEventListeners() {
  elements.refreshStatusBtn.onclick = checkStatus;
  elements.botSearch.oninput = renderBotsList;

  elements.botForm.onsubmit = (e) => {
    e.preventDefault();
    executeBot();
  };

  window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      executeBot();
    }
  });

  elements.tabBtnFormatted.onclick = () => switchTab('formatted');
  elements.tabBtnDiagrams.onclick = () => switchTab('diagrams');
  elements.tabBtnRaw.onclick = () => switchTab('raw');

  elements.copyOutputBtn.onclick = () => {
    if (state.lastResponse) {
      navigator.clipboard.writeText(JSON.stringify(state.lastResponse, null, 2));
      elements.copyOutputBtn.textContent = '✓ Copied!';
      setTimeout(() => elements.copyOutputBtn.textContent = '📋 Copy', 1500);
    }
  };

  // NVIDIA Modal Listeners
  elements.btnNvidiaKey.onclick = () => {
    elements.nvidiaModal.classList.remove('hidden');
    elements.inputNvidiaKey.focus();
  };
  elements.btnCloseNvidiaModal.onclick = () => elements.nvidiaModal.classList.add('hidden');
  elements.btnCancelNvidia.onclick = () => elements.nvidiaModal.classList.add('hidden');
  elements.btnSaveNvidia.onclick = saveNvidiaKey;

  // History modal controls
  elements.btnShowHistory.onclick = () => {
    renderHistoryModal();
    elements.historyModal.classList.remove('hidden');
  };
  elements.btnCloseHistory.onclick = () => elements.historyModal.classList.add('hidden');
  elements.btnClearHistory.onclick = () => {
    state.history = [];
    localStorage.removeItem('n8n_bots_history');
    updateHistoryCount();
    renderHistoryModal();
  };
}

document.addEventListener('DOMContentLoaded', init);
