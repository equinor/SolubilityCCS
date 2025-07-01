# Create venv if it doesn't exist
if [ ! -d "/workspaces/SolubilityCCS/venv" ]; then
    python3 -m venv /workspaces/SolubilityCCS/venv
fi
# Activate venv
source /workspaces/SolubilityCCS/venv/bin/activate
# Upgrade pip
pip install --upgrade pip
# Install requirements
pip install -r /workspaces/SolubilityCCS/requirements.txt