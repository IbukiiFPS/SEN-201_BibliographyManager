from PIL import Image
import sys
import os
import platform
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

png_path = ASSETS / "app_icon.png"

# --- Windows .ico ---
ico_path = ASSETS / "win.ico"
img = Image.open(png_path)
img.save(ico_path, format="ICO", sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
print(f"Windows icon created → {ico_path}")

# --- macOS .icns ---
if platform.system().lower() == "darwin":
    iconset_dir = ASSETS / "tmp.iconset"
    iconset_dir.mkdir(exist_ok=True)
    
    # Export standard macOS iconset sizes
    for size in [16, 32, 64, 128, 256, 512, 1024]:
        resized = img.resize((size, size))
        resized.save(iconset_dir / f"icon_{size}x{size}.png")
        resized.save(iconset_dir / f"icon_{size}x{size}@2x.png")
    
    icns_path = ASSETS / "mac.icns"
    
    # Use macOS built-in iconutil command
    try:
        subprocess.run(["iconutil", "-c", "icns", str(iconset_dir), "-o", str(icns_path)], check=True)
        print(f"macOS icon created → {icns_path}")
    except Exception as e:
        print(f"macOS icon generation failed: {e}")
    
    # Clean up temporary folder
    for file in iconset_dir.glob("*.png"):
        file.unlink()
    iconset_dir.rmdir()
else:
    print("Skipping macOS .icns creation (not on macOS).")

# --- Linux PNG (copy/resize) ---
linux_path = ASSETS / "linux.png"
img.resize((256, 256)).save(linux_path, format="PNG")
print(f"Linux icon created → {linux_path}")

print("\nAll platform icons generated successfully!")
