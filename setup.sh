#!/bin/bash

echo "🚀 Setting up RAG Chatbot Backend API"
echo "======================================"

# Check Python version
echo ""
echo "📌 Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo ""
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if GEMINI_API_KEY is set
echo ""
echo "🔑 Checking for GEMINI_API_KEY..."
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  WARNING: GEMINI_API_KEY is not set!"
    echo ""
    echo "Please set your Gemini API key:"
    echo "  export GEMINI_API_KEY='your-api-key-here'"
    echo ""
    echo "Get your API key from: https://makersuite.google.com/app/apikey"
else
    echo "✅ GEMINI_API_KEY is set"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start the server, run:"
echo "  python main.py"
echo ""
echo "To deactivate the virtual environment, run:"
echo "  deactivate"