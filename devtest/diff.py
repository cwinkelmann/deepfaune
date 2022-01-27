# https://stackoverflow.com/questions/189943/how-can-i-quantify-difference-between-two-images
import sys
from PIL import Image, ImageOps, ImageChops, ImageFilter
im1 = Image.open(sys.argv[1])
im2 = Image.open(sys.argv[2])

im1g = im1.convert("L") # ImageOps.grayscale(im1)
im2g = im2.convert("L") # ImageOps.grayscale(im2)

#diff = ImageChops.difference(im2g, im1g)
diff = ImageChops.difference(im2, im1).convert("L")
#diff.show()

threshold = 100
# https://www.geeksforgeeks.org/python-pil-image-point-method/ 
diffthres = diff.point(lambda p: p > threshold and 255) # point = pixelwise action
# take min value in 3x3 window
diffthres = diffthres.filter(ImageFilter.MedianFilter(3))
diffthres.show()
bbox = diffthres.getbbox()
bbox = (bbox[0]*0.9,bbox[1]*0.9,bbox[2]*1.1,bbox[3]*1.1)

im1crop = im1.crop(bbox)
im1crop.show()
im2crop = im2.crop(bbox)
im2crop.show()
