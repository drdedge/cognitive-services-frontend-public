// Simple development server as a fallback
const express = require('express');
const { createServer } = require('vite');

async function startServer() {
  const app = express();
  const vite = await createServer({
    server: { middlewareMode: true },
    appType: 'spa',
  });

  app.use(vite.middlewares);

  app.listen(3000, () => {
    console.log('Server running at http://localhost:3000');
  });
}

startServer().catch(console.error);