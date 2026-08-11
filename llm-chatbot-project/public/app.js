const chatWindow = document.getElementById('chatWindow');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

const messages = [
  { role: 'system', content: 'You are a helpful assistant.' }
];

function appendMessage(role, text) {
  const wrapper = document.createElement('div');
  wrapper.className = `message ${role}`;
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;
  wrapper.appendChild(bubble);
  chatWindow.appendChild(wrapper);
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
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages }),
    });

    const data = await response.json();
    if (!response.ok) {
      appendMessage('assistant', `Error: ${data.error || response.statusText}`);
      return;
    }

    const assistantMessage = data.assistant || 'No response received';
    messages.push({ role: 'assistant', content: assistantMessage });
    appendMessage('assistant', assistantMessage);
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
