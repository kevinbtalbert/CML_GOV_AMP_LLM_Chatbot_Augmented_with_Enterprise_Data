#!/bin/bash

VENV_DIR="$HOME/chroma_venv"

echo "🚀 Setting up an isolated ChromaDB environment in $VENV_DIR..."

# Ensure Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found! Please install Python 3 before proceeding."
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "🔹 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "✅ Virtual environment already exists at $VENV_DIR."
fi

# Activate the virtual environment
echo "🔹 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip to the latest version
echo "🔹 Upgrading pip..."
pip install --no-user --upgrade pip

# Install ChromaDB and core dependencies
echo "📦 Installing ChromaDB and dependencies..."
pip install --no-user chromadb gradio sentence-transformers requests torch bitsandbytes transformers huggingface_hub accelerate beautifulsoup4 pysqlite3-binary

echo "🔹 Patch Chroma DB..."
python $HOME/3_session-make-chroma-venv/setup-chromadb.py
pip install --no-user pysqlite3-binary

# Verify installation
echo "✅ Installed packages in the virtual environment:"
pip list

# Provide usage instructions
echo -e "\n🚀 You can now use this environment by running:"
echo "    source $VENV_DIR/bin/activate"

echo -e "\n📝 If you have scripts that need this environment, run them with:"
echo "    python your_script.py"

echo -e "\n🎉 All done! The environment is fully set up."

