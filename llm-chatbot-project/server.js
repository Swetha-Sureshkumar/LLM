const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const OLLAMA_HOST = process.env.OLLAMA_HOST || 'http://127.0.0.1:11434';
const OLLAMA_MODEL = process.env.OLLAMA_MODEL || 'llama2';

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

app.post('/api/chat', async (req, res) => {
  const { messages } = req.body;

  if (!Array.isArray(messages) || messages.length === 0) {
    return res.status(400).json({ error: 'messages must be a non-empty array' });
  }

  try {
    const response = await fetch(`${OLLAMA_HOST}/v1/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: OLLAMA_MODEL,
        messages,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      return res.status(response.status).json({ error: errorText });
    }

    const data = await response.json();
    return res.json(data);
  } catch (error) {
    console.error('Ollama request failed:', error);
    return res.status(500).json({ error: 'Failed to contact Ollama server' });
  }
});

app.listen(PORT, () => {
  console.log(`Chatbot server running at http://localhost:${PORT}`);
  console.log(`Ollama host: ${OLLAMA_HOST}`);
  console.log(`Using Ollama model: ${OLLAMA_MODEL}`);
});
