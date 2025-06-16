#!/usr/bin/env python3
"""
Build script for TheLastBlueBook.py
Creates an executable with PyInstaller while implementing techniques to reduce antivirus flags
"""
import os
import sys
import shutil
import subprocess
import time
import hashlib

def main():
    print("Building TheLastBlueBook executable...")
    
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
        print("PyInstaller is installed.")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Clean previous build directories
    for dir_to_clean in ['build', 'dist']:
        if os.path.exists(dir_to_clean):
            print(f"Cleaning {dir_to_clean} directory...")
            shutil.rmtree(dir_to_clean)
    
    # Build the executable
    print("Building executable with PyInstaller...")
    subprocess.run([
        sys.executable, 
        "-m", 
        "PyInstaller", 
        "TheLastBlueBook.spec",
        "--clean"
    ], check=True)
    
    # Verify the build was successful
    exe_path = os.path.join("dist", "TheLastBlueBook.exe")
    if os.path.exists(exe_path):
        print(f"Build successful! Executable created at: {exe_path}")
        
        # Calculate and display file hash for verification
        file_hash = hashlib.sha256()
        with open(exe_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                file_hash.update(chunk)
        print(f"SHA-256 hash: {file_hash.hexdigest()}")
        
        # Get file size
        file_size = os.path.getsize(exe_path) / (1024 * 1024)  # Convert to MB
        print(f"File size: {file_size:.2f} MB")
    else:
        print("Build failed! Executable not found.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
