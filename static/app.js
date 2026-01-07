/**
 * Integration Quest - PWA Game Client
 */

const API_BASE = '/api';

// State
let gameState = {
    hasCharacter: false,
    inCombat: false,
    enemies: [],
    exits: [],
    items: [],
    inventory: []
};

// DOM Elements
const createScreen = document.getElementById('create-screen');
const gameScreen = document.getElementById('game-screen');
const gameLog = document.getElementById('game-log');
const actionButtons = document.getElementById('action-buttons');
const modal = document.getElementById('modal');
const loading = document.getElementById('loading');
const heroNameInput = document.getElementById('hero-name-input');

// ==================== //
// API Helpers          //
// ==================== //

async function apiCall(endpoint, method = 'GET', body = null) {
    showLoading(true);
    try {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin'
        };
        if (body) options.body = JSON.stringify(body);

        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        return { error: 'Network error. Please try again.' };
    } finally {
        showLoading(false);
    }
}

function showLoading(show) {
    loading.classList.toggle('hidden', !show);
}

// ==================== //
// UI Helpers           //
// ==================== //

function appendToLog(message, type = 'normal') {
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.innerHTML = formatNarrative(message);
    gameLog.appendChild(entry);
    gameLog.scrollTop = gameLog.scrollHeight;
}

function clearLog() {
    gameLog.innerHTML = '';
}

function formatNarrative(text) {
    if (!text) return '';
    // Convert **bold** to <strong>
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    // Convert newlines to breaks
    text = text.replace(/\n/g, '<br>');
    return text;
}

function updateStats(hero) {
    if (!hero) return;

    document.getElementById('hero-name').textContent = hero.name || 'Hero';
    document.getElementById('hero-level').textContent = `Lv ${hero.level || 1}`;

    const hp = hero.hp || 0;
    const maxHp = hero.max_hp || 100;
    const mp = hero.mp || 0;
    const maxMp = hero.max_mp || 50;

    const hpPercent = (hp / maxHp) * 100;
    const mpPercent = (mp / maxMp) * 100;

    document.getElementById('hp-fill').style.width = `${hpPercent}%`;
    document.getElementById('hp-text').textContent = `HP: ${hp}/${maxHp}`;

    document.getElementById('mp-fill').style.width = `${mpPercent}%`;
    document.getElementById('mp-text').textContent = `MP: ${mp}/${maxMp}`;
}

function showModal(title, content, onConfirm, showConfirm = true) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = content;

    const confirmBtn = document.getElementById('modal-confirm');
    const cancelBtn = document.getElementById('modal-cancel');

    confirmBtn.classList.toggle('hidden', !showConfirm);

    const closeModal = () => {
        modal.classList.add('hidden');
        confirmBtn.onclick = null;
        cancelBtn.onclick = null;
    };

    cancelBtn.onclick = closeModal;
    confirmBtn.onclick = () => {
        closeModal();
        if (onConfirm) onConfirm();
    };

    modal.classList.remove('hidden');
}

function hideModal() {
    modal.classList.add('hidden');
}

// ==================== //
// Action Buttons       //
// ==================== //

function updateActionButtons() {
    actionButtons.innerHTML = '';

    // Show combat buttons if in combat OR if there are enemies in the room
    const hasEnemies = gameState.enemies.length > 0;
    const showCombatUI = gameState.inCombat || hasEnemies;

    if (showCombatUI) {
        // Combat actions
        if (hasEnemies) {
            actionButtons.appendChild(createButton('Attack', () => showAttackTargets()));
        }

        actionButtons.appendChild(createButton('Defend', doDefend));
        actionButtons.appendChild(createButton('Flee', doFlee));

        if (gameState.inventory.some(i => i.type === 'Consumable')) {
            actionButtons.appendChild(createButton('Item', () => showItemSelection()));
        }

        // Also show Status in combat
        actionButtons.appendChild(createButton('Status', doStatus, 'secondary'));
    } else {
        // Exploration actions
        actionButtons.appendChild(createButton('Explore', doExplore));

        // Direction buttons if exits available
        if (gameState.exits.length > 0) {
            gameState.exits.forEach(dir => {
                const btn = createButton(dir.charAt(0).toUpperCase() + dir.slice(1), () => doMove(dir), 'secondary');
                actionButtons.appendChild(btn);
            });
        }

        // Pickup if items in room
        if (gameState.items.length > 0) {
            actionButtons.appendChild(createButton('Pickup', () => showPickupTargets(), 'secondary'));
        }

        // Status and Rest
        actionButtons.appendChild(createButton('Status', doStatus, 'secondary'));
        actionButtons.appendChild(createButton('Rest', doRest, 'secondary'));
        actionButtons.appendChild(createButton('Save', doSave, 'secondary'));
    }
}

function createButton(text, onClick, style = '') {
    const btn = document.createElement('button');
    btn.className = `action-btn ${style}`;
    btn.textContent = text;
    btn.onclick = onClick;
    return btn;
}

// ==================== //
// Game Actions         //
// ==================== //

async function doCreateCharacter(name, role) {
    const result = await apiCall('/create_character', 'POST', { name, role });
    handleResponse(result);

    if (!result.error) {
        createScreen.classList.add('hidden');
        gameScreen.classList.remove('hidden');
        clearLog();
        await refreshGameState();
    }
}

async function doExplore() {
    const result = await apiCall('/explore');
    handleResponse(result);
    await refreshGameState();
}

async function doStatus() {
    const result = await apiCall('/status');
    handleResponse(result);
}

async function doMove(direction) {
    const result = await apiCall('/move', 'POST', { direction });
    handleResponse(result);
    await refreshGameState();
}

async function doAttack(target, skill = 'basic_attack') {
    const result = await apiCall('/attack', 'POST', { target, skill });
    handleResponse(result, 'combat');
    await refreshGameState();

    if (result.state?.game_over) {
        setTimeout(() => {
            appendToLog('Game Over! Refresh to start again.', 'error');
        }, 1000);
    }
}

async function doDefend() {
    const result = await apiCall('/defend', 'POST');
    handleResponse(result, 'combat');
    await refreshGameState();
}

async function doFlee() {
    const result = await apiCall('/flee', 'POST');
    handleResponse(result, 'combat');
    await refreshGameState();
}

async function doRest() {
    const result = await apiCall('/rest', 'POST');
    handleResponse(result);
    await refreshGameState();
}

async function doPickup(item) {
    const result = await apiCall('/pickup', 'POST', { item });
    handleResponse(result, 'success');
    await refreshGameState();
}

async function doUseItem(item) {
    const result = await apiCall('/use_item', 'POST', { item });
    handleResponse(result, 'success');
    await refreshGameState();
}

async function doSave() {
    const result = await apiCall('/save', 'POST');
    handleResponse(result, 'success');
}

// ==================== //
// Response Handler     //
// ==================== //

function handleResponse(result, type = 'normal') {
    if (result.error) {
        appendToLog(result.error, 'error');
        return;
    }
    if (result.narrative) {
        appendToLog(result.narrative, type);
    }
}

async function refreshGameState() {
    const result = await apiCall('/game_state');

    if (result.error) {
        console.error('Failed to refresh game state:', result.error);
        return;
    }

    gameState.hasCharacter = result.has_character;
    gameState.inCombat = result.in_combat;
    gameState.enemies = result.room?.enemies || [];
    gameState.exits = result.room?.exits || [];
    gameState.items = result.room?.items || [];
    gameState.inventory = result.hero ? [] : []; // We'd need to add inventory to game_state API

    if (result.hero) {
        updateStats(result.hero);
    }

    updateActionButtons();
}

// ==================== //
// Target Selection     //
// ==================== //

function showAttackTargets() {
    if (gameState.enemies.length === 0) {
        appendToLog('No enemies to attack!', 'error');
        return;
    }

    if (gameState.enemies.length === 1) {
        doAttack(gameState.enemies[0].name);
        return;
    }

    let content = '<div class="target-list">';
    gameState.enemies.forEach(enemy => {
        content += `<button class="target-btn" data-target="${enemy.name}">
            ${enemy.emoji} ${enemy.name} (${enemy.hp}/${enemy.max_hp} HP)
        </button>`;
    });
    content += '</div>';

    showModal('Select Target', content, null, false);

    // Add click handlers to target buttons
    document.querySelectorAll('.target-btn').forEach(btn => {
        btn.onclick = () => {
            hideModal();
            doAttack(btn.dataset.target);
        };
    });
}

function showPickupTargets() {
    if (gameState.items.length === 0) {
        appendToLog('No items to pick up!', 'error');
        return;
    }

    if (gameState.items.length === 1) {
        doPickup(gameState.items[0].name);
        return;
    }

    let content = '<div class="target-list">';
    gameState.items.forEach(item => {
        content += `<button class="target-btn" data-target="${item.name}">
            ${item.name} (${item.tier})
        </button>`;
    });
    content += '</div>';

    showModal('Select Item', content, null, false);

    document.querySelectorAll('.target-btn').forEach(btn => {
        btn.onclick = () => {
            hideModal();
            doPickup(btn.dataset.target);
        };
    });
}

function showItemSelection() {
    const consumables = gameState.inventory.filter(i => i.type === 'Consumable');

    if (consumables.length === 0) {
        appendToLog('No usable items!', 'error');
        return;
    }

    let content = '<div class="target-list">';
    consumables.forEach(item => {
        content += `<button class="target-btn" data-target="${item.name}">
            ${item.name} x${item.quantity}
        </button>`;
    });
    content += '</div>';

    showModal('Use Item', content, null, false);

    document.querySelectorAll('.target-btn').forEach(btn => {
        btn.onclick = () => {
            hideModal();
            doUseItem(btn.dataset.target);
        };
    });
}

// ==================== //
// Initialization       //
// ==================== //

async function init() {
    // Check if we have an existing game
    const result = await apiCall('/game_state');

    if (result.has_character) {
        // Resume existing game
        createScreen.classList.add('hidden');
        gameScreen.classList.remove('hidden');
        clearLog();
        appendToLog(`Welcome back, ${result.hero.name}! Your adventure continues...`);
        gameState.hasCharacter = true;
        gameState.inCombat = result.in_combat;
        gameState.enemies = result.room?.enemies || [];
        gameState.exits = result.room?.exits || [];
        gameState.items = result.room?.items || [];
        updateStats(result.hero);
        updateActionButtons();
    } else {
        // Show character creation
        createScreen.classList.remove('hidden');
        gameScreen.classList.add('hidden');
    }

    // Setup character creation
    setupCharacterCreation();

    // Register service worker for PWA
    if ('serviceWorker' in navigator) {
        try {
            await navigator.serviceWorker.register('/static/sw.js');
            console.log('Service worker registered');
        } catch (error) {
            console.log('Service worker registration failed:', error);
        }
    }
}

function setupCharacterCreation() {
    const roleButtons = document.querySelectorAll('.role-btn');

    roleButtons.forEach(btn => {
        btn.onclick = () => {
            const name = heroNameInput.value.trim() || 'Hero';
            const role = btn.dataset.role;
            doCreateCharacter(name, role);
        };
    });

    // Allow Enter key to select first role
    heroNameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            roleButtons[0].click();
        }
    });
}

// Start the app
document.addEventListener('DOMContentLoaded', init);
