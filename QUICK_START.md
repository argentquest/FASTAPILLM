# FASTAPILLM Quick Start Guide

## 🔍 Check Your Setup First

Run this to verify everything is ready:
```bash
python check-setup.py
```
This will tell you exactly what you need to install.

## 🚀 Running FASTAPILLM

You now have a modern React frontend with the backend. Here's how to run them:

### Option 1: Backend Only (Recommended)
```bash
# Run the backend application with embedded MCP server
python backend/main.py

# Access at: http://localhost:8000
# MCP endpoint: http://localhost:8000/mcp
```

### Option 2: Backend with React Frontend
```bash
# Terminal 1 - Backend API
python backend/main.py

# Terminal 2 - React Frontend
cd frontendReact
npm install  # First time only
npm run dev

# Access:
# - Backend API: http://localhost:8000 (helpful landing page)
# - API Docs: http://localhost:8000/api/docs
# - React Frontend: http://localhost:3001
# - MCP Server: http://localhost:8000/mcp
```

### Option 3: Docker Deployment
```bash
# Run with Docker (React frontend + backend)
docker-compose -f docker-compose.separated.yml up --build

# Access:
# - Backend API: http://localhost:8000
# - React Frontend: http://localhost:3001
# - MCP Server: http://localhost:8000/mcp
```

**Note**: The Alpine.js frontend has been removed from the codebase. Only React frontend is available now.

## 🔧 VSCode Integration

### Using Tasks (Recommended)
1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Choose:
   - **"Run Backend Only"** - Backend with MCP server
   - **"Run All (React)"** - Backend + React frontend

### Using Debug/Launch
1. Go to Run & Debug (`Ctrl+Shift+D`)
2. Select "Backend" and click play
3. Manually start your preferred frontend

## 🐳 Docker Option

```bash
# Run all services with Docker
docker-compose -f docker-compose.separated.yml up --build

# Access:
# - Backend: http://localhost:8000
# - React Frontend: http://localhost:3001
# - MCP Server: http://localhost:8000/mcp
```

## ❗ Important Notes

### Prerequisites

1. **Python Virtual Environment**: Make sure you're in your virtual environment:
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux  
   source .venv/bin/activate
   ```

2. **Node.js (for React frontend only)**:
   - Install Node.js 18+ from [nodejs.org](https://nodejs.org/)
   - Verify: `node --version` and `npm --version`

3. **Dependencies**:
   ```bash
   # Python dependencies (required)
   pip install -r requirements.txt
   
   # React frontend dependencies (only if using React)
   cd frontendReact
   npm install  # Installs Vite, React, TypeScript, Tailwind CSS, etc.
   ```

4. **Environment Variables**: Make sure you have:
   - `AZURE_OPENAI_KEY` and `AZURE_OPENAI_ENDPOINT`, or
   - `OPENROUTER_API_KEY`, or
   - Your custom OpenAI-compatible API settings

5. **MCP Integration**: The platform includes built-in MCP server support:
   - Automatically starts with the backend
   - Exposes story generation as MCP tools
   - Compatible with Claude Desktop app

## 🎯 Why React?

The platform now uses React as the primary frontend for these benefits:
- ✅ Modern TypeScript development
- ✅ Component reusability and maintainability  
- ✅ Rich client-side features and interactivity
- ✅ Better developer experience with hot reloading
- ✅ Excellent tooling ecosystem (Vite, Tailwind CSS)
- ✅ Mobile-responsive design out of the box

## 🆘 Troubleshooting

### Backend won't start?
```bash
# Check if in virtual environment
python -c "import sys; print(sys.prefix)"

# Install requirements
pip install -r requirements.txt

# Check for port conflicts
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

### Frontend won't connect to backend?
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify environment variables

### React frontend issues?
```bash
# Install Node.js first if not installed
node --version  # Should show v18+ 
npm --version   # Should show npm version

# Clear cache and reinstall
cd frontendReact
rm -rf node_modules package-lock.json
npm install

# Common fixes
npm run build  # Test if build works
npm run dev    # Start development server
```

### Don't have Node.js?
1. **Install Node.js**: Download from [nodejs.org](https://nodejs.org/) (LTS version recommended)
2. **Verify installation**: `node --version` should show v18 or higher
3. **Install dependencies**: `cd frontendReact && npm install`

## 🚀 Happy Coding!

You now have a flexible, scalable architecture with multiple frontend options. Start with whichever feels most comfortable to you!