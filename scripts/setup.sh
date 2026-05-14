#!/bin/bash

# setup.sh — sets up the library project from scratch
# Run once when you clone or start fresh

# ── Colours for readable output ───────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'    # NC = No Colour — resets back to normal

# ── Helper functions ───────────────────────────────────────────
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_error()   { echo -e "${RED}✗ $1${NC}"; }
print_step()    { echo -e "\n${YELLOW}── $1${NC}"; }

# ── Step 1: Check Python is installed ─────────────────────────

print_step "Checking Python installation"
if ! command -v python &> /dev/null; then
    print_error "Python3 not found"
    exit 1
fi

PYTHON_VER=$(python --version)
print_success "Python is installed: $PYTHON_VER"

# ── Step 2: Create virtual environment ───────────────────────
print_step "Setting up virtual environment"
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists, skipping creation"
else
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# ── Step 3: Install dependencies ────────────────────────────
print_step "Installing dependencies"
source venv/bin/activate

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencies installed"
else
    print_warning "No requirements.txt found, skipping dependency installation"
fi

# ── Step 4: Create folder structure if missing ────────────────
print_step "Checking project folder structure"

FOLDERS=("models" "services" "scripts" "tests")
for FOLDER in "${FOLDERS[@]}"; do
    if [ ! -d "$FOLDER" ]; then
        mkdir "$FOLDER"
        print_success "Created folder: $FOLDER"
    else
        print_warning "Folder already exists: $FOLDER"
    fi
done

# ── Done ──────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}══════════════════════════════════${NC}"
echo -e "${GREEN}  Setup complete! Run ./scripts/run.sh to start${NC}"
echo -e "${GREEN}══════════════════════════════════${NC}"