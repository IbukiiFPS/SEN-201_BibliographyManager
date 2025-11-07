# BibliographyManager – Linux Installation Guide

## 1. Install Dependencies

### 
Open a terminal and install Tkinter:
```bash
sudo apt update
sudo apt install python3-tk -y
```

(Optional, for image or icon support in the GUI):
```bash
sudo apt install python3-pil python3-pil.imagetk -y
```

---

## 2. Copy the Executable
Place the provided file in a working directory, for example:
```bash
mkdir -p ~/BibliographyManager
cp bibliography_manager ~/BibliographyManager/
cd ~/BibliographyManager
```

Make sure it is executable:
```bash
chmod +x bibliography_manager
```

---

## 3. Run the Application
From the same directory:
```bash
./bibliography_manager
```

If installed system-wide (e.g., copied to `/usr/local/bin`), you can run it from anywhere:
```bash
bibliography_manager
```

---

## 4. (Optional) System-Wide Installation
To make the command globally available:
```bash
sudo install -m 755 bibliography_manager /usr/local/bin/bibliography_manager
```

Now simply type:
```bash
bibliography_manager
```

---

## 5. Troubleshooting

| Issue | Cause | Solution |
|-------|--------|-----------|
| `ModuleNotFoundError: No module named 'tkinter'` | Tkinter not installed | Run `sudo apt install python3-tk -y` |
| `Permission denied` | Missing execute permission | Run `chmod +x bibliography_manager` |
| `command not found: bibliography_manager` | Not in system PATH | Run from the same directory or install to `/usr/local/bin` |
| GUI window does not appear in WSL | No X-server configured | Install & run an X-server (VcXsrv / X410) and set `export DISPLAY=:0` |

---

## Summary
After completing the setup:
- Tkinter is installed  
- `bibliography_manager` is executable  
- The app launches with:  
  ```bash
  ./bibliography_manager
  ```
or, if installed system-wide:
  ```bash
  bibliography_manager
  ```
