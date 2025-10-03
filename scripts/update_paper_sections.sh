#!/usr/bin/env bash
# Script to replace stub sections with publication-ready content
# Run from repo root: bash scripts/update_paper_sections.sh

set -e

PAPER_DIR="paper/sections"
BACKUP_DIR="paper/sections_backup_$(date +%Y%m%d_%H%M%S)"

echo "Creating backup of current sections..."
mkdir -p "$BACKUP_DIR"
cp -r "$PAPER_DIR"/*.tex "$BACKUP_DIR/" 2>/dev/null || echo "No existing .tex files to backup"

echo "Updating sections with publication-ready content..."

# Use introduction_v2 if introduction_full exists, otherwise use introduction_full
if [ -f "$PAPER_DIR/introduction_v2.tex" ]; then
    echo "  - Using introduction_v2.tex"
    cp "$PAPER_DIR/introduction_v2.tex" "$PAPER_DIR/introduction.tex"
elif [ -f "$PAPER_DIR/introduction_full.tex" ]; then
    echo "  - Using introduction_full.tex"
    cp "$PAPER_DIR/introduction_full.tex" "$PAPER_DIR/introduction.tex"
fi

echo ""
echo "Section status:"
python scripts/expand_paper_sections.py --check

echo ""
echo "Backup saved to: $BACKUP_DIR"
echo ""
echo "NEXT STEPS:"
echo "1. Review updated sections in $PAPER_DIR"
echo "2. Add theory_full.tex, data_likelihood_full.tex, etc. using templates"
echo "3. Run: python scripts/expand_paper_sections.py --template theory > $PAPER_DIR/theory_full.tex"
echo "4. Copy content from feedback email to remaining sections"
echo "5. Compile paper: cd paper && pdflatex lgpd_cosmo_paper.tex"
