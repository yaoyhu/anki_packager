#!/bin/bash

# Clean up previous builds
rm -rf build/ dist/ *.egg-info/

# Build source and wheel distributions
python -m build

# Upload to PyPI
# Uncomment when ready to publish:
# twine upload dist/*

echo -e "Build completed. To publish to PyPI, run: twine upload dist/*"
