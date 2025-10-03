#!/bin/bash
# Prepare Overleaf upload package for LGPD paper
#
# This script collects all necessary files for compiling the paper on Overleaf,
# which has LaTeX installed (unlike local machine).
#
# Usage: bash scripts/prepare_overleaf_package.sh
#
# Output: Creates overleaf_upload/ directory with all needed files

set -e

REPO_ROOT="/Users/leonardspeiser/Projects/lpgd"
OUTPUT_DIR="$REPO_ROOT/overleaf_upload"

echo "=========================================="
echo "Preparing Overleaf upload package"
echo "=========================================="

# Clean and create output directory
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/sections"
mkdir -p "$OUTPUT_DIR/figures"

echo "✓ Created output directory structure"

# Copy LaTeX source files
echo "Copying LaTeX sources..."
cp "$REPO_ROOT/paper/lgpd_cosmo_paper.tex" "$OUTPUT_DIR/"
cp "$REPO_ROOT/paper/supplement_theory.tex" "$OUTPUT_DIR/"
cp "$REPO_ROOT/paper/refs.bib" "$OUTPUT_DIR/"
cp "$REPO_ROOT/paper/sections"/*.tex "$OUTPUT_DIR/sections/"

echo "✓ Copied LaTeX sources"

# Copy figures
echo "Copying figures..."
cp "$REPO_ROOT/outputs/figures/fig"*.png "$OUTPUT_DIR/figures/"
cp "$REPO_ROOT/outputs/convergence"/*.png "$OUTPUT_DIR/figures/"

# Copy tables (if they exist)
if [ -f "$REPO_ROOT/outputs/convergence/diagnostics_table.tex" ]; then
    cp "$REPO_ROOT/outputs/convergence/diagnostics_table.tex" "$OUTPUT_DIR/sections/"
fi

if [ -f "$REPO_ROOT/outputs/robustness/summary_table.tex" ]; then
    cp "$REPO_ROOT/outputs/robustness/summary_table.tex" "$OUTPUT_DIR/sections/"
fi

echo "✓ Copied figures and tables"

# Copy documentation
echo "Copying documentation..."
cp "$REPO_ROOT/paper/PRD_cover_letter.txt" "$OUTPUT_DIR/"
cp "$REPO_ROOT/REPRODUCIBILITY.md" "$OUTPUT_DIR/"
cp "$REPO_ROOT/paper/PRD_SUBMISSION_CHECKLIST.md" "$OUTPUT_DIR/"

echo "✓ Copied documentation"

# Create README for Overleaf
cat > "$OUTPUT_DIR/README_OVERLEAF.txt" << 'EOF'
LGPD COSMOLOGY PAPER - OVERLEAF PACKAGE
========================================

This directory contains all files needed to compile the paper on Overleaf.

COMPILATION INSTRUCTIONS:
------------------------

1. Upload this entire directory to Overleaf as a new project
   (use "New Project" -> "Upload Project" -> select ZIP of this folder)

2. Set main document to: lgpd_cosmo_paper.tex

3. Compile with: pdflatex (default)

4. For bibliography: 
   - First run: pdflatex
   - Second run: bibtex
   - Third run: pdflatex (2x)

5. To compile supplement:
   - Change main document to: supplement_theory.tex
   - Repeat compilation steps

DIRECTORY STRUCTURE:
-------------------

lgpd_cosmo_paper.tex    - Main manuscript
supplement_theory.tex   - Theory supplement
refs.bib                - Bibliography
sections/               - Individual paper sections
figures/                - All figures (PNG format, 300 dpi)
PRD_cover_letter.txt    - Cover letter for PRD submission

EXPECTED OUTPUT:
---------------

Main paper: ~20 pages (including references)
Supplement: ~10 pages

TROUBLESHOOTING:
---------------

If figures don't show:
- Verify figures/ directory is present
- Check figure paths in .tex files (should be figures/figX_*.png)

If citations undefined:
- Run bibtex step
- Verify refs.bib is in root directory

If sections missing:
- Check sections/ directory has all .tex files
- Verify \input{sections/...} paths in main .tex

CONTACT:
--------

For questions about compilation or content:
Leonard Speiser
[email from PRD_cover_letter.txt]

Generated: $(date)
EOF

echo "✓ Created README"

# Create file list
echo "Creating file manifest..."
find "$OUTPUT_DIR" -type f | sed "s|$OUTPUT_DIR/||" | sort > "$OUTPUT_DIR/FILE_MANIFEST.txt"

echo "✓ Created file manifest"

# Count files and size
NUM_FILES=$(find "$OUTPUT_DIR" -type f | wc -l | tr -d ' ')
TOTAL_SIZE=$(du -sh "$OUTPUT_DIR" | cut -f1)

echo ""
echo "=========================================="
echo "Package prepared successfully!"
echo "=========================================="
echo "Location: $OUTPUT_DIR"
echo "Files: $NUM_FILES"
echo "Total size: $TOTAL_SIZE"
echo ""
echo "Contents:"
echo "  - LaTeX sources (main + supplement)"
echo "  - Bibliography (42 references)"
echo "  - Figures (7 total: 4 main + 3 supplement)"
echo "  - All section files"
echo "  - Documentation and cover letter"
echo ""
echo "Next steps:"
echo "  1. Create ZIP archive:"
echo "     cd $OUTPUT_DIR && zip -r ../lgpd_paper_overleaf.zip ."
echo ""
echo "  2. Upload to Overleaf:"
echo "     - Go to overleaf.com"
echo "     - New Project -> Upload Project"
echo "     - Select lgpd_paper_overleaf.zip"
echo ""
echo "  3. Compile and generate PDFs"
echo ""
echo "  4. Download PDFs for PRD submission"
echo ""
echo "=========================================="
