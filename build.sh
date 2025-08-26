#!/bin/bash
set -e

# Define build output directory
BUILD_DIR="build"

# 1. Check if /build folder exists, if not create it
if [ ! -d "$BUILD_DIR" ]; then
    echo "[INFO] Creating $BUILD_DIR directory..."
    mkdir -p "$BUILD_DIR"
else
    echo "[INFO] Using existing $BUILD_DIR directory."
fi

# 2. Compile .py files into .mpy format
# Usage: ./build.sh <source_file_or_folder>

if [ -z "$1" ]; then
    echo "Usage: $0 <source_file_or_folder>"
    exit 1
fi

SOURCE="$1"

# Check if mpy-cross exists in PATH
if ! command -v mpy-cross &> /dev/null; then
    echo "[ERROR] mpy-cross not found. Make sure it's installed and in your PATH."
    exit 1
fi

compile_file() {
    local file="$1"
    local rel_path="${file#./}"                     # Remove leading './'
    local out_path="$BUILD_DIR/${rel_path%.py}.mpy" # Change extension

    mkdir -p "$(dirname "$out_path")"
    echo "[BUILD] $file -> $out_path"
    mpy-cross "$file" -o "$out_path"
}

if [ -f "$SOURCE" ]; then
    # If input is a single file
    compile_file "$SOURCE"
elif [ -d "$SOURCE" ]; then
    # If input is a directory, find all .py files
    find "$SOURCE" -type f -name "*.py" | while read -r file; do
        compile_file "$file"
    done
else
    echo "[ERROR] Source $SOURCE not found."
    exit 1
fi

echo "[DONE] All .py files compiled to $BUILD_DIR/"
