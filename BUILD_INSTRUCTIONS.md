# Building TheLastBlueBook Executable

This document provides instructions for building TheLastBlueBook game into an executable file using PyInstaller.

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)
- Required Python packages:
  - pygame
  - numpy
  - pyinstaller

## Installation of Dependencies

```bash
pip install pygame numpy pyinstaller
```

## Building the Executable

### Option 1: Using the build script (Recommended)

1. Run the build script:
   ```bash
   python build_exe.py
   ```

2. The executable will be created in the `dist` directory.

### Option 2: Manual build with PyInstaller

1. Run PyInstaller with the improved spec file:
   ```bash
   pyinstaller TheLastBlueBook_improved.spec --clean
   ```

2. The executable will be created in the `dist` directory.

## Running the Game

After building, you can run the game by:

1. Navigating to the `dist` directory
2. Double-clicking on `TheLastBlueBook.exe`

## Troubleshooting

If you encounter any issues:

1. Make sure all dependencies are installed
2. Verify that the `images` and `sounds` directories contain all required files
3. Check that `highscore.json` exists (even if it's empty)
4. Try rebuilding with the `--clean` flag

## Notes

- The executable includes all necessary data files (images, sounds, highscore)
- The build has been configured to minimize antivirus false positives
- If you modify the game code, you'll need to rebuild the executable
