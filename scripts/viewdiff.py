from PIL import Image
import matplotlib.pyplot as plt

img = Image.open("diff.ppm")

plt.imshow(img)
plt.axis('off')
plt.show()
