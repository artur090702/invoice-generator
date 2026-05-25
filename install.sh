#!/usr/bin/env bash
set -euo pipefail

INSTALL_BIN="$HOME/.local/bin"
DATA_DIR="$HOME/.local/share/geninvoice"
TEMPLATE_DIR="$DATA_DIR/templates"
CLIENT_DIR="$DATA_DIR/clients"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

NEEDED_DEPS=""

check_deps() {
    local missing=0

    if ! python3 -c "import sys; assert sys.version_info >= (3, 10)" 2>/dev/null; then
        echo "ERROR: Python 3.10 or higher is required."
        NEEDED_DEPS="$NEEDED_DEPS python3"
        missing=1
    fi

    if ! command -v pdflatex &>/dev/null; then
        echo "ERROR: pdflatex is not installed. Install TeX Live:"
        echo "  Arch:   sudo pacman -S texlive-basic texlive-latexrecommended"
        echo "  Debian: sudo apt install texlive-latex-recommended"
        NEEDED_DEPS="$NEEDED_DEPS texlive"
        missing=1
    fi

    if [[ $missing -eq 1 ]]; then
        if [[ -z "${1:-}" ]]; then
            echo "Missing dependencies:$NEEDED_DEPS"
            echo "Re-run with a package installer as the first argument, e.g.:"
            echo "  ./install.sh 'apk add --no-cache'"
            echo "  ./install.sh 'apt-get install -y'"
            exit 1
        fi
        DEP_INSTALLER="$1"
        $DEP_INSTALLER $NEEDED_DEPS
    fi
}

install_python_deps() {
    echo "Installing Python dependencies..."
    python3 -m venv --system-site-packages "$DATA_DIR/venv"
    "$DATA_DIR/venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" -q
}

setup_dirs() {
    mkdir -p "$INSTALL_BIN" "$TEMPLATE_DIR" "$CLIENT_DIR"
}

install_templates() {
    echo "Installing templates..."
    cp "$SCRIPT_DIR/templates/preamble.tex" "$TEMPLATE_DIR/preamble.tex"
    cp "$SCRIPT_DIR/templates/template.tex"  "$TEMPLATE_DIR/template.tex"

    if [[ ! -f "$TEMPLATE_DIR/myinfo.tex" ]]; then
        cp "$SCRIPT_DIR/templates/myinfo.template.tex" "$TEMPLATE_DIR/myinfo.tex"
        echo ""
        echo "  --> Created $TEMPLATE_DIR/myinfo.tex from example."
        echo "      Edit it to add your business details before generating invoices."
        echo ""
    else
        echo "  --> $TEMPLATE_DIR/myinfo.tex already exists, skipping."
    fi
}

install_script() {
    echo "Installing invoice-generator to $INSTALL_BIN..."
    cp "$SCRIPT_DIR/invoice-generator" "$INSTALL_BIN/invoice-generator"
    cp "$SCRIPT_DIR/pick.py"           "$INSTALL_BIN/pick.py"
    cp "$SCRIPT_DIR/invoice.py"        "$INSTALL_BIN/invoice.py"
    chmod +x "$INSTALL_BIN/invoice-generator"
}

check_path() {
    if [[ ":$PATH:" != *":$INSTALL_BIN:"* ]]; then
        echo ""
        echo "NOTE: $INSTALL_BIN is not in your PATH."
        echo "Add this to your ~/.bashrc or ~/.zshrc:"
        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
}

main() {
    echo "=== invoice-generator installer ==="
    check_deps
    install_python_deps
    setup_dirs
    install_templates
    install_script
    check_path
    echo ""
    echo "Done. Run: invoice-generator"
}

main "$@"
