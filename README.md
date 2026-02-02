# Notempo-ConuhacksX
Give it a music_sheet.mxl file, this displays the sheet with notes names. Functional, just barely, maybe.

## TLDR if you don't care and just want to run it: 
- open windows powershell 
- go to folder location/enter it

FYI if you're really new, `***` see stars
- run `.\start.ps1`
- open a web browser
- copy paste in the address >>  http://127.0.0.1:5000/

*Note: you have to manually delete files from the upload folder because I(AI) didn't make an automatic thing to do that. Yet

`***` (do not run the >> arrows or the ==, they're there for separators)
- run >>  `ls`                == you want to see folder list of where you are right now
- run >>  `cd FolderName`     == you will enter the folder FolderName. Tip: you can start writing FolderName, ex: Fol, then hit the tab button. Multiple times. See what happens
- run >>  `cd ..`             == you want to go back one folder layer, you return to the previous folder you were in

`##################
Manual oversharing
##################`

This is currently (First updated Feb 2026) free to steal (you host the site code locally on your own machine anyway), the code isn't mine, it's fully AI coded (with some attempts from me to read it, but since it's not academically tied, can't stop me). Code credits to free version of chatgpt from internet and my free credits on VScode with whatever AI chatbot they autoselected. You probably can do the same, if not better than me too.

Name comes from note-tempo, but because the ai wasnt great at generation (at first) notempo ended up being funnier & more accurate. I take credit for coming up with this name without asking AI

Solo repo because many dependencies scares me (I couldn't run our og repo). OG repo link: https://github.com/m88deng/notempo/tree/y-ai (this is my branch, I never managed to ship anything, you guys go use main)

Anyway this started as vibecoding part of a hackathon, and it still remains vibecoded to this day. Keep your trust levels low and remember where downloaded files are because you must manually clean up the files after

`##########################
Below was fully AI written
##########################`

Overview
--------
This small app accepts a .mxl or .musicxml upload, processes it with `mxlTOnames.py` to add letter/solfege lyrics, and serves the resulting `*_annotated.musicxml` to the browser where OpenSheetMusicDisplay renders it.

Quick prerequisites
-------------------
- Python 3.8+ installed and on PATH
- On Windows: PowerShell (administrator rights may be required to change execution policy)

Files of interest
-----------------
- `app.py` — Flask web server; endpoints: `/` (index), `/upload` (POST file), `/files/<filename>` (serve generated file)
- `index.html` — UI; upload control and OpenSheetMusicDisplay viewer
- `mxlTOnames.py` — core processor; call `process_file(input_path, output_dir)`
- `requirements.txt` — Python packages required
- `uploads/` — created automatically; uploaded files and outputs are stored here
- `start.ps1` — PowerShell helper to create venv, install deps and run server (optional)

PowerShell (one-flow commands)
--------------------------------
Below is a single sequence of commands you can copy and paste into PowerShell. It will create and activate a virtual environment, install dependencies, and start the server. Run this from any PowerShell window (make sure you have Python 3.8+ installed).

1) Open PowerShell, then paste and press Enter (one flow):

   cd "C:\Users\HP\Documents\dev_workspaces\python notempo\noteconvert"
   python -m venv .venv
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   python app.py

Notes about the block above:
- `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` temporarily allows running the activation script for this PowerShell session only (safer than changing system policy). If you are prompted for permission, type Y and press Enter.
- If you already have a `.venv`, you can skip the `python -m venv .venv` step. To use the convenience helper instead, run: `.\start.ps1` (it does the same sequence for you).

Manual flow (step-by-step for beginners)
---------------------------------------
If you want to run each step manually and understand what happens, follow these numbered steps and type the commands one by one.

1) Open PowerShell
   - Click Start, type "PowerShell", and open "Windows PowerShell".

2) Change to the project folder:
   - Type (replace with your path if different) and press Enter:
     cd "C:\Users\HP\Documents\dev_workspaces\python notempo\noteconvert"

3) Create a virtual environment (a clean Python environment for the project):
   - Type and press Enter:
     python -m venv .venv
   - This creates a new folder called `.venv` with a private Python install for this project.

4) Allow scripts for this session and activate the venv:
   - If your system prevents running scripts, run (type and press Enter):
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
     (If prompted, type Y and press Enter.)
   - Activate the venv by running:
     .\.venv\Scripts\Activate.ps1
   - After activation, your prompt will usually show `(.venv)` at the start. That means the venv is active.

5) Upgrade pip and install project dependencies:
   - Type and press Enter:
     python -m pip install --upgrade pip
     python -m pip install -r requirements.txt
   - This installs `Flask`, `music21`, and any other required packages.

6) Start the server:
   - Run:
     python app.py
   - The console should show Flask starting up and listening on http://127.0.0.1:5000/ (or similar). Leave this window open while using the app.

7) Open the app in your web browser:
   - Open a browser and go to:
     http://127.0.0.1:5000/
   - Use the file chooser in the page to upload a `.mxl` or `.musicxml` file. The app will process it and display the annotated sheet.

8) Stop the server when done:
   - Click the PowerShell window and press Ctrl+C to stop the Flask server.

Troubleshooting tips for beginners
---------------------------------
- If `python` isn't recognized, make sure Python is installed and added to your PATH. Reinstall Python from python.org and check "Add Python to PATH".
- If activation fails, ensure you ran the `Set-ExecutionPolicy` command and confirmed with Y when prompted.
- If pip install fails, try running `python -m pip install --upgrade pip` first and then the `-r requirements.txt` command again.

This should get you running locally. If anything errors, copy the terminal output and I can help diagnose it.

Quick test via curl (optional)
-----------------------------
curl -F "file=@C:\path\to\file.mxl" http://127.0.0.1:5000/upload

Notes & security
----------------
- The server is intentionally minimal and intended for local use. Do not expose it publicly without adding authentication, sanitization and rate limiting.
- Uploaded files and generated outputs are left in `uploads/` and are not automatically deleted. Remove them manually if needed.

Support
-------
If something fails, check the terminal running `python app.py` for stack traces, then open an issue or ask me to add more detailed logs or error handling.

