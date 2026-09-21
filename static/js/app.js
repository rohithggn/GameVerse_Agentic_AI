// ===== DOM Elements =====
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const chatSendBtn = document.getElementById('chatSendBtn');
const chatClearBtn = document.getElementById('chatClearBtn');
const chatSuggestions = document.getElementById('chatSuggestions');
const gamesGrid = document.getElementById('gamesGrid');
const genreTabs = document.getElementById('genreTabs');
const tutorialsGrid = document.getElementById('tutorialsGrid');
const tutorialFilters = document.getElementById('tutorialFilters');
const navLinks = document.querySelectorAll('.nav-links a');
const navHamburger = document.getElementById('navHamburger');
const navMenu = document.getElementById('navMenu');
const fabChat = document.getElementById('fabChat');

// ===== State =====
let gamesData = {};
let tutorialsData = [];
let activeGenre = 'all';
let activeTutorialFilter = 'all';
let isTyping = false;

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', () => {
    loadGames();
    loadTutorials();
    setupNavigation();
    setupChat();
    addWelcomeMessage();
});

// ===== Navigation =====
function setupNavigation() {
    // Scroll spy for active nav link
    const sections = document.querySelectorAll('section[id]');
    
    window.addEventListener('scroll', () => {
        const scrollY = window.scrollY;

        // Navbar background
        const navbar = document.querySelector('.navbar');
        if (scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        // Active section
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');

            if (scrollY >= sectionTop && scrollY < sectionTop + sectionHeight) {
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    });

    // Hamburger menu
    navHamburger.addEventListener('click', () => {
        navMenu.classList.toggle('open');
    });

    // Close menu on link click
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('open');
        });
    });

    // FAB button
    fabChat.addEventListener('click', () => {
        document.getElementById('chat').scrollIntoView({ behavior: 'smooth' });
        setTimeout(() => chatInput.focus(), 500);
    });
}

// ===== Chat =====
function setupChat() {
    // Send on Enter
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    chatSendBtn.addEventListener('click', sendMessage);

    chatClearBtn.addEventListener('click', clearChat);

    // Suggestion chips
    chatSuggestions.addEventListener('click', (e) => {
        if (e.target.classList.contains('suggestion-chip')) {
            chatInput.value = e.target.textContent;
            sendMessage();
        }
    });
}

function addWelcomeMessage() {
    const welcomeHTML = `
        <p>Hey there, gamer! 🎮 I'm <strong>GameVerse AI</strong>, your personal gaming assistant!</p>
        <p>I can help you discover amazing games, recommend titles based on your taste, and guide you through gaming tutorials. Try asking me:</p>
        <p>• "Recommend me an open world RPG"<br>
        • "What are the best free-to-play games?"<br>
        • "Tips for getting better at FPS games"</p>
    `;
    appendMessage('bot', welcomeHTML, true);
}

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message || isTyping) return;

    // Add user message
    appendMessage('user', escapeHTML(message));
    chatInput.value = '';
    chatInput.focus();

    // Hide suggestions after first message
    if (chatSuggestions) {
        chatSuggestions.style.display = 'none';
    }

    // Show typing indicator
    isTyping = true;
    chatSendBtn.disabled = true;
    const typingEl = showTypingIndicator();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        // Remove typing indicator
        if (typingEl) typingEl.remove();

        if (data.error) {
            appendMessage('bot', `<p style="color: var(--accent-pink);">⚠️ ${escapeHTML(data.error)}</p>`, true);
        } else {
            appendMessage('bot', formatBotResponse(data.response), true);
        }
    } catch (error) {
        if (typingEl) typingEl.remove();
        appendMessage('bot', `<p style="color: var(--accent-pink);">⚠️ Connection error. Please check your internet and try again.</p>`, true);
    }

    isTyping = false;
    chatSendBtn.disabled = false;
}

async function clearChat() {
    try {
        await fetch('/chat/clear', { method: 'POST' });
    } catch (e) { /* ignore */ }
    chatMessages.innerHTML = '';
    if (chatSuggestions) chatSuggestions.style.display = 'flex';
    addWelcomeMessage();
}

function appendMessage(type, content, isHTML = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const avatar = type === 'bot' ? '🤖' : '👤';
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-bubble">${isHTML ? content : `<p>${content}</p>`}</div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="typing-indicator">
            <span></span><span></span><span></span>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return typingDiv;
}

function formatBotResponse(text) {
    // Convert markdown-like formatting to HTML
    let formatted = escapeHTML(text);
    
    // Bold text **text** or __text__
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/__(.*?)__/g, '<strong>$1</strong>');
    
    // Italic text *text* or _text_
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Line breaks
    formatted = formatted.replace(/\n\n/g, '</p><p>');
    formatted = formatted.replace(/\n/g, '<br>');
    
    return `<p>${formatted}</p>`;
}

function escapeHTML(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ===== Games =====
async function loadGames() {
    try {
        const response = await fetch('/games');
        gamesData = await response.json();
        renderGenreTabs();
        renderGames('all');
    } catch (error) {
        gamesGrid.innerHTML = '<div class="empty-state"><div class="empty-state-icon">😵</div><p class="empty-state-text">Failed to load games. Please refresh.</p></div>';
    }
}

function renderGenreTabs() {
    let tabsHTML = `<button class="genre-tab active" data-genre="all"><span class="tab-icon">🎮</span> All</button>`;
    
    for (const [key, genre] of Object.entries(gamesData)) {
        tabsHTML += `<button class="genre-tab" data-genre="${key}"><span class="tab-icon">${genre.icon}</span> ${genre.name}</button>`;
    }
    
    genreTabs.innerHTML = tabsHTML;

    // Tab click handlers
    genreTabs.addEventListener('click', (e) => {
        const tab = e.target.closest('.genre-tab');
        if (!tab) return;

        genreTabs.querySelectorAll('.genre-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        activeGenre = tab.dataset.genre;
        renderGames(activeGenre);
    });
}

function renderGames(genre) {
    let html = '';

    const genresToRender = genre === 'all' ? Object.keys(gamesData) : [genre];

    genresToRender.forEach(genreKey => {
        const genreData = gamesData[genreKey];
        if (!genreData) return;

        if (genre === 'all') {
            html += `
                <div class="genre-header-accent" style="grid-column: 1 / -1;">
                    <span class="genre-emoji">${genreData.icon}</span>
                    <div>
                        <h3>${genreData.name}</h3>
                        <p>${genreData.description}</p>
                    </div>
                </div>
            `;
        }

        genreData.games.forEach(game => {
            const stars = '★'.repeat(Math.floor(game.rating)) + (game.rating % 1 >= 0.5 ? '½' : '');
            html += `
                <div class="game-card">
                    <div class="game-card-header" style="background-image: url('${game.image_url}'); border-bottom: 1px solid var(--border-glass);">
                    </div>
                    <div class="game-card-body">
                        <h4 class="game-card-title">${escapeHTML(game.title)}</h4>
                        <p class="game-card-desc">${escapeHTML(game.description)}</p>
                        <div class="game-card-meta">
                            <span class="game-card-platform">${escapeHTML(game.platform)}</span>
                            <span class="game-card-rating">${stars} ${game.rating}</span>
                        </div>
                        <a href="${game.link}" target="_blank" rel="noopener noreferrer" class="game-card-link">
                            <button class="btn btn-download btn-sm">⬇ Download / Play</button>
                        </a>
                    </div>
                </div>
            `;
        });
    });

    gamesGrid.innerHTML = html;
}

// ===== Tutorials =====
async function loadTutorials() {
    try {
        const response = await fetch('/tutorials');
        tutorialsData = await response.json();
        renderTutorialFilters();
        renderTutorials('all');
    } catch (error) {
        tutorialsGrid.innerHTML = '<div class="empty-state"><div class="empty-state-icon">😵</div><p class="empty-state-text">Failed to load tutorials. Please refresh.</p></div>';
    }
}

function renderTutorialFilters() {
    const categories = ['all', ...new Set(tutorialsData.map(t => t.category))];
    
    let html = '';
    categories.forEach(cat => {
        html += `<button class="tutorial-filter ${cat === 'all' ? 'active' : ''}" data-category="${cat}">${cat === 'all' ? '📋 All' : cat}</button>`;
    });
    
    tutorialFilters.innerHTML = html;

    tutorialFilters.addEventListener('click', (e) => {
        const filter = e.target.closest('.tutorial-filter');
        if (!filter) return;

        tutorialFilters.querySelectorAll('.tutorial-filter').forEach(f => f.classList.remove('active'));
        filter.classList.add('active');

        activeTutorialFilter = filter.dataset.category;
        renderTutorials(activeTutorialFilter);
    });
}

function renderTutorials(category) {
    const filtered = category === 'all' ? tutorialsData : tutorialsData.filter(t => t.category === category);

    let html = '';
    filtered.forEach(tutorial => {
        const stepsHTML = tutorial.steps.map(step => `<li>${escapeHTML(step)}</li>`).join('');
        html += `
            <div class="tutorial-card" data-id="${tutorial.id}">
                <div class="tutorial-card-header" onclick="toggleTutorial(${tutorial.id})">
                    <div class="tutorial-icon">${tutorial.icon}</div>
                    <div class="tutorial-header-text">
                        <h3>${escapeHTML(tutorial.title)}</h3>
                        <span class="tutorial-category-badge ${tutorial.category}">${tutorial.category}</span>
                    </div>
                    <div class="tutorial-toggle">▼</div>
                </div>
                <div class="tutorial-card-body">
                    <p class="tutorial-desc">${escapeHTML(tutorial.description)}</p>
                </div>
                <div class="tutorial-steps">
                    <ol>${stepsHTML}</ol>
                </div>
            </div>
        `;
    });

    if (filtered.length === 0) {
        html = '<div class="empty-state"><div class="empty-state-icon">📭</div><p class="empty-state-text">No tutorials found for this category.</p></div>';
    }

    tutorialsGrid.innerHTML = html;
}

function toggleTutorial(id) {
    const card = document.querySelector(`.tutorial-card[data-id="${id}"]`);
    if (card) {
        card.classList.toggle('expanded');
    }
}
