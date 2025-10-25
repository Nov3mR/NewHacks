#!/bin/bash
# setup-deployment.sh - Run this to prepare for deployment

echo "🚀 Setting up Travel Buddy API for deployment..."

# Create Procfile for Railway/Render
cat > Procfile << 'EOF'
web: uvicorn main:app --host 0.0.0.0 --port $PORT
EOF
echo "✅ Created Procfile"

# Create runtime.txt for Python version
cat > runtime.txt << 'EOF'
python-3.11.0
EOF
echo "✅ Created runtime.txt"

# Create .env.example
cat > .env.example << 'EOF'
GEMINI_API_KEY=your_gemini_api_key_here
EOF
echo "✅ Created .env.example"

# Create Dockerfile (optional - for containerized deployment)
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY .env .

ENV PORT=8080

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
EOF
echo "✅ Created Dockerfile"

# Create .dockerignore
cat > .dockerignore << 'EOF'
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.gitignore
.mypy_cache
.pytest_cache
.hypothesis
*.db
*.sqlite
storage/
data/
EOF
echo "✅ Created .dockerignore"

echo ""
echo "✨ Setup complete! Next steps:"
echo ""
echo "1. Make sure your .env file has your GEMINI_API_KEY"
echo "2. Test locally:"
echo "   python main.py"
echo ""
echo "3. Deploy to Railway:"
echo "   - Go to railway.app"
echo "   - New Project → Deploy from GitHub"
echo "   - Add GEMINI_API_KEY in environment variables"
echo "   - Deploy!"
echo ""
echo "4. Or deploy to Render:"
echo "   - Go to render.com"
echo "   - New Web Service → Connect your repo"
echo "   - Build: pip install -r requirements.txt"
echo "   - Start: uvicorn main:app --host 0.0.0.0 --port \$PORT"
echo "   - Add GEMINI_API_KEY in environment"
echo ""
echo "📦 Your app will use ~150MB RAM (instead of 2GB+)"