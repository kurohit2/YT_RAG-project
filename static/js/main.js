// Utility to extract Video ID from URL (Frontend client-side check)
function extractVideoId(url) {
    const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/;
    const match = url.match(regex);
    return match ? match[1] : null;
}

// Homepage logic
const ytInput = document.getElementById('ytUrl');
const processBtn = document.getElementById('processBtn');
const urlError = document.getElementById('urlError');

if (processBtn) {
    processBtn.addEventListener('click', async () => {
        const url = ytInput.value.trim();
        const videoId = extractVideoId(url) || url;

        if (!videoId || (url.length > 20 && !extractVideoId(url))) {
            urlError.classList.remove('hidden');
            return;
        }

        urlError.classList.add('hidden');
        setLoading(true);

        try {
            const response = await fetch('/api/process-video', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();

            if (data.status === 'success') {
                window.location.href = '/chat';
            } else {
                alert(data.error || 'Failed to process video');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('A network error occurred');
        } finally {
            setLoading(false);
        }
    });
}

function setLoading(isLoading) {
    const spinner = document.getElementById('loadingSpinner');
    const btnText = document.getElementById('btnText');
    if (!processBtn) return;
    
    processBtn.disabled = isLoading;
    if (isLoading) {
        spinner.classList.remove('hidden');
        btnText.textContent = 'Processing...';
    } else {
        spinner.classList.add('hidden');
        btnText.textContent = 'Process Video';
    }
}

// Chat Page Logic
async function fetchMetadata() {
    try {
        const response = await fetch('/api/video-metadata');
        const data = await response.json();
        if (data.error) return;

        document.getElementById('vTitle').textContent = data.title;
        document.getElementById('vAuthor').textContent = data.author;
        document.getElementById('vThumb').src = data.thumbnail;
    } catch (e) {
        console.error('Failed to fetch metadata');
    }
}

async function sendMessage() {
    const input = document.getElementById('questionInput');
    const chatMessages = document.getElementById('chatMessages');
    const text = input.value.trim();

    if (!text) return;

    // Add User Message
    addMessage(text, 'user');
    input.value = '';

    // Add Loading placeholder for AI
    const loadingId = 'ai-loading-' + Date.now();
    addMessage('...', 'ai', loadingId);

    try {
        const response = await fetch('/api/ask-question', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: text })
        });
        const data = await response.json();

        const loadingEl = document.getElementById(loadingId);
        if (data.answer) {
            updateMessageContent(loadingId, data.answer);
        } else {
            updateMessageContent(loadingId, 'Error: ' + (data.error || 'Unknown error'));
        }
    } catch (e) {
        updateMessageContent(loadingId, 'Failed to connect to server');
    }
}

function addMessage(text, type, id = null) {
    const container = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = 'flex items-start space-x-3';
    if (id) div.id = id;

    const icon = type === 'user' ? '👤' : '🤖';
    const bgColor = type === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-50 text-slate-700 border border-slate-100';
    const alignment = type === 'user' ? 'justify-end' : '';
    const rounded = type === 'user' ? 'rounded-tr-none' : 'rounded-tl-none';

    div.innerHTML = `
        <div class="flex items-start space-x-3 w-full ${alignment}">
            ${type !== 'user' ? `<div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 flex-shrink-0">${icon}</div>` : ''}
            <div class="${bgColor} rounded-2xl ${rounded} p-4 text-sm max-w-[85%] shadow-sm whitespace-pre-wrap">${text}</div>
            ${type === 'user' ? `<div class="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 flex-shrink-0 ml-3">${icon}</div>` : ''}
        </div>
    `;

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function updateMessageContent(id, text) {
    const el = document.getElementById(id);
    if (!el) return;
    const contentDiv = el.querySelector('div > div:nth-child(2)');
    if (contentDiv) {
        contentDiv.textContent = text;
    }
}

function askPreset(q) {
    const input = document.getElementById('questionInput');
    input.value = q;
    sendMessage();
}
