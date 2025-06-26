#!/bin/bash

# Cognitive Services Frontend - Setup Script
# This script sets up the development environment for both backend and frontend

set -e  # Exit on error

echo "🚀 Setting up Cognitive Services Frontend Development Environment"
echo "============================================================="

# Check for required tools
check_requirements() {
    echo "📋 Checking requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
        exit 1
    else
        echo "✅ Python 3 found: $(python3 --version)"
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
        exit 1
    else
        echo "✅ Node.js found: $(node --version)"
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        echo "❌ npm is not installed."
        exit 1
    else
        echo "✅ npm found: $(npm --version)"
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo "⚠️  Docker is not installed. Docker is required for deployment."
    else
        echo "✅ Docker found: $(docker --version)"
    fi
}

# Create Python virtual environment
setup_backend() {
    echo ""
    echo "🐍 Setting up Backend (Python/FastAPI)..."
    echo "----------------------------------------"
    
    cd backend
    
    # Create virtual environment
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate || source venv/Scripts/activate
    
    # Upgrade pip
    echo "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    echo "Installing Python dependencies..."
    pip install fastapi uvicorn python-multipart
    pip install azure-ai-documentintelligence azure-cognitiveservices-speech azure-cognitiveservices-language-translator
    pip install azure-storage-blob
    pip install python-dotenv
    pip install websockets python-socketio
    pip install pytest pytest-asyncio pytest-cov
    pip install httpx  # For testing FastAPI
    
    # Save requirements
    pip freeze > requirements.txt
    
    echo "✅ Backend setup complete!"
    
    # Return to root
    cd ..
}

# Setup frontend
setup_frontend() {
    echo ""
    echo "🎨 Setting up Frontend (Vue/Vite/Tailwind)..."
    echo "-------------------------------------------"
    
    cd frontend
    
    # Initialize package.json if it doesn't exist
    if [ ! -f "package.json" ]; then
        echo "Initializing npm project..."
        npm init -y
    fi
    
    # Install Vue 3 and Vite
    echo "Installing Vue 3 and Vite..."
    npm install vue@latest
    npm install -D vite @vitejs/plugin-vue
    
    # Install Tailwind CSS
    echo "Installing Tailwind CSS..."
    npm install -D tailwindcss postcss autoprefixer
    npx tailwindcss init -p
    
    # Install other dependencies
    echo "Installing additional dependencies..."
    npm install vue-router@4 pinia
    npm install axios socket.io-client
    npm install -D @types/node
    
    # Install testing dependencies
    echo "Installing testing dependencies..."
    npm install -D @vue/test-utils jest @vue/vue3-jest
    npm install -D @testing-library/vue @testing-library/jest-dom
    npm install -D cypress
    
    echo "✅ Frontend setup complete!"
    
    # Return to root
    cd ..
}

# Create environment files
create_env_files() {
    echo ""
    echo "📝 Creating environment files..."
    echo "--------------------------------"
    
    # Create .env.example
    cat > .env.example << 'EOF'
# Azure Cognitive Services
AZURE_DOC_INTELLIGENCE_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
AZURE_DOC_INTELLIGENCE_KEY=your-api-key
AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com/
AZURE_TRANSLATOR_KEY=your-api-key
AZURE_SPEECH_ENDPOINT=https://your-region.api.cognitive.microsoft.com/
AZURE_SPEECH_KEY=your-api-key

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=cogsvcfrontend001;AccountKey=your-key;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER=cognitive-services

# Application Settings
API_BASE_URL=http://localhost:8000
FRONTEND_PORT=3000
BACKEND_PORT=8000

# Security
API_KEY=your-internal-api-key
JWT_SECRET=your-jwt-secret

# Environment
NODE_ENV=development
PYTHON_ENV=development
EOF

    # Copy to .env if it doesn't exist
    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo "✅ Created .env file (please update with your Azure credentials)"
    else
        echo "ℹ️  .env file already exists"
    fi
}

# Create Docker files
create_docker_files() {
    echo ""
    echo "🐳 Creating Docker configuration..."
    echo "----------------------------------"
    
    # Create docker-compose.yml
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - PYTHON_ENV=production
    env_file:
      - .env
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads
    depends_on:
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - API_BASE_URL=http://backend:8000
    depends_on:
      - backend

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend

volumes:
  redis_data:
  uploads:
EOF

    echo "✅ Docker configuration created"
}

# Create Makefiles for easy commands
create_makefiles() {
    echo ""
    echo "🛠️  Creating Makefiles..."
    echo "------------------------"
    
    # Root Makefile
    cat > Makefile << 'EOF'
.PHONY: help setup install dev test build deploy clean

help:
	@echo "Available commands:"
	@echo "  make setup    - Initial project setup"
	@echo "  make install  - Install all dependencies"
	@echo "  make dev      - Run development servers"
	@echo "  make test     - Run all tests"
	@echo "  make build    - Build for production"
	@echo "  make deploy   - Deploy with Docker"
	@echo "  make clean    - Clean generated files"

setup: install
	@echo "✅ Setup complete! Run 'make dev' to start development servers."

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev:
	@echo "Starting development servers..."
	@trap 'kill %1; kill %2' SIGINT; \
	cd backend && uvicorn main:app --reload --port 8000 & \
	cd frontend && npm run dev & \
	wait

test:
	cd backend && pytest
	cd frontend && npm test

build:
	cd frontend && npm run build
	docker-compose build

deploy:
	docker-compose up -d

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
EOF

    echo "✅ Makefiles created"
}

# Create VS Code configuration
create_vscode_config() {
    echo ""
    echo "📁 Creating VS Code configuration..."
    echo "-----------------------------------"
    
    mkdir -p .vscode
    
    # Create settings.json
    cat > .vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "./backend/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll.eslint": true
    },
    "eslint.validate": [
        "javascript",
        "javascriptreact",
        "vue"
    ],
    "files.exclude": {
        "**/__pycache__": true,
        "**/node_modules": true,
        "**/.pytest_cache": true
    }
}
EOF

    # Create launch.json for debugging
    cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "main:app",
                "--reload",
                "--port",
                "8000"
            ],
            "cwd": "${workspaceFolder}/backend",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/backend"
            }
        },
        {
            "name": "Vue: Dev Server",
            "type": "chrome",
            "request": "launch",
            "url": "http://localhost:3000",
            "webRoot": "${workspaceFolder}/frontend/src"
        }
    ]
}
EOF

    echo "✅ VS Code configuration created"
}

# Create initial directory structure
create_initial_files() {
    echo ""
    echo "📄 Creating initial files..."
    echo "---------------------------"
    
    # Create backend main.py
    cat > backend/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Cognitive Services API",
    description="Azure Cognitive Services Frontend API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Cognitive Services API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

    # Create frontend entry files
    cat > frontend/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Azure Cognitive Services</title>
</head>
<body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
</body>
</html>
EOF

    cat > frontend/src/main.js << 'EOF'
import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

const app = createApp(App)
app.mount('#app')
EOF

    cat > frontend/src/App.vue << 'EOF'
<template>
  <div class="min-h-screen bg-background">
    <header class="bg-header-bg text-white p-4">
      <h1 class="text-2xl font-bold">Azure Cognitive Services</h1>
    </header>
    <main class="container mx-auto p-4">
      <p class="text-text-color">Welcome to Cognitive Services Frontend</p>
    </main>
  </div>
</template>

<script setup>
// Component logic here
</script>
EOF

    cat > frontend/src/style.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --background: #F5F9FA;
  --header-bg: #283857;
  --primary-action: #4F78AB;
  --text-color: #3B5781;
  --highlight: #4F78AB;
  --success: #28a745;
  --warning: #ffc107;
}
EOF

    # Update tailwind.config.js
    cat > frontend/tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'background': 'var(--background)',
        'header-bg': 'var(--header-bg)',
        'primary-action': 'var(--primary-action)',
        'text-color': 'var(--text-color)',
        'highlight': 'var(--highlight)',
        'success': 'var(--success)',
        'warning': 'var(--warning)',
      }
    },
  },
  plugins: [],
}
EOF

    # Create vite.config.js
    cat > frontend/vite.config.js << 'EOF'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
})
EOF

    # Update frontend package.json scripts
    cat > frontend/package.json << 'EOF'
{
  "name": "cognitive-services-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "jest",
    "test:e2e": "cypress open",
    "lint": "eslint src --ext .js,.vue"
  },
  "dependencies": {
    "vue": "^3.3.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "axios": "^1.6.0",
    "socket.io-client": "^4.7.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-vue": "^4.5.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "@types/node": "^20.0.0",
    "@vue/test-utils": "^2.4.0",
    "jest": "^29.7.0",
    "@vue/vue3-jest": "^29.2.0",
    "@testing-library/vue": "^8.0.0",
    "@testing-library/jest-dom": "^6.1.0",
    "cypress": "^13.6.0"
  }
}
EOF

    echo "✅ Initial files created"
}

# Main setup flow
main() {
    check_requirements
    setup_backend
    setup_frontend
    create_env_files
    create_docker_files
    create_makefiles
    create_vscode_config
    create_initial_files
    
    echo ""
    echo "🎉 Setup Complete!"
    echo "=================="
    echo ""
    echo "Next steps:"
    echo "1. Update .env with your Azure credentials"
    echo "2. Run 'make dev' to start development servers"
    echo "3. Backend will be at http://localhost:8000"
    echo "4. Frontend will be at http://localhost:3000"
    echo ""
    echo "Available commands:"
    echo "  make dev     - Start development servers"
    echo "  make test    - Run tests"
    echo "  make build   - Build for production"
    echo "  make deploy  - Deploy with Docker"
    echo ""
}

# Run main function
main