const chatWindow = document.getElementById('chatWindow');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

const messages = [
  { role: 'system', content: 'You are a helpful assistant.' }
];

function appendMessage(role, text, id) {
  let wrapper;
  if (id) {
    wrapper = document.getElementById(id);
    if (!wrapper) {
      wrapper = document.createElement('div');
      wrapper.id = id;
      wrapper.className = `message ${role}`;
      const bubble = document.createElement('div');
      bubble.className = 'bubble';
      wrapper.appendChild(bubble);
      chatWindow.appendChild(wrapper);
    }
    wrapper.querySelector('.bubble').textContent = text;
  } else {
    wrapper = document.createElement('div');
    wrapper.className = `message ${role}`;
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;
    wrapper.appendChild(bubble);
    chatWindow.appendChild(wrapper);
  }
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage() {
  const text = messageInput.value.trim();
  if (!text) return;

  appendMessage('user', text);
  messages.push({ role: 'user', content: text });
  messageInput.value = '';
  sendButton.disabled = true;

  try {
    const resp = await fetch('/api/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages }),
    });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      appendMessage('assistant', `Error: ${err.error || resp.statusText}`);
      return;
    }

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let assistantId = `assistant-${Date.now()}`;
    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      appendMessage('assistant', buffer, assistantId);
    }

    // finalize
    appendMessage('assistant', buffer, assistantId);
    messages.push({ role: 'assistant', content: buffer });
  } catch (error) {
    appendMessage('assistant', `Request failed: ${error.message}`);
  } finally {
    sendButton.disabled = false;
    messageInput.focus();
  }
}

sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    event.preventDefault();
    sendMessage();
  }
});

messageInput.focus();
