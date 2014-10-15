from PIL import Image

# Load the arbitrarily sized image
img = Image.open('images/v1.png')
# Create an image padded to the required size with
# mode 'RGB'
print img.size
width = ((img.size[0] + 31) // 32)
print width
width = width * 32
print width
pad = Image.new('RGB', (
    ((img.size[0] + 31) // 32) * 32,
    ((img.size[1] + 15) // 16) * 16,
    ))

print pad.size
# Paste the original image into the padded one
pad.paste(img, (0, 0))

pad.save('test.png')