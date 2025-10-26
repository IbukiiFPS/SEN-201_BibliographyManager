from PIL import Image

png_path = "assets/book.png"
ico_path = "assets/win.ico"

# Convert and save multiple sizes (best for Windows executables)
img = Image.open(png_path)
img.save(ico_path, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])

print(f"Converted {png_path} → {ico_path}")
