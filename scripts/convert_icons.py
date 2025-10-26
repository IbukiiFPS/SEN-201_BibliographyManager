from PIL import Image
import os
import sys
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
try:
    import icnsutil
    icns_path = ASSETS / "mac.icns"
    iconset_dir = ASSETS / "tmp.iconset"
    iconset_dir.mkdir(exist_ok=True)

    # Create multiple PNG sizes for macOS ICNS
    for size in [16, 32, 64, 128, 256, 512, 1024]:
        resized = img.resize((size, size))
        resized.save(iconset_dir / f"icon_{size}x{size}.png")

    icnsutil.create_icns_from_pngs(str(iconset_dir), str(icns_path))
    print(f"macOS icon created → {icns_path}")

    # Clean up temporary files
    for file in iconset_dir.glob("*.png"):
        file.unlink()
    iconset_dir.rmdir()
except ImportError:
    print("Skipped macOS .icns generation (install with: pip install icnsutil)")

# --- Linux PNG (copy/resize) ---
linux_path = ASSETS / "linux.png"
img.resize((256, 256)).save(linux_path, format="PNG")
print(f"Linux icon created → {linux_path}")

print("\nAll platform icons generated successfully!")
