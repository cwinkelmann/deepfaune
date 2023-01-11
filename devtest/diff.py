# https://stackoverflow.com/questions/189943/how-can-i-quantify-difference-between-two-images
import sys

def sshow(im):
    im.copy().resize((700,600)).show()
    
from PIL import Image, ImageOps, ImageChops, ImageFilter

im1 = Image.open(sys.argv[1])
im2 = Image.open(sys.argv[2])

im1 = Image.open("loup11.JPG")
im2 = Image.open("loup12.JPG")

import numpy as np

RESIZE = True
if RESIZE:
    im1b = im1.resize((700,600)).filter(ImageFilter.GaussianBlur(radius = 2))
    im2b = im2.resize((700,600)).filter(ImageFilter.GaussianBlur(radius = 2))
else:
    im1b = im1.filter(ImageFilter.GaussianBlur(radius = 2))
    im2b = im2.filter(ImageFilter.GaussianBlur(radius = 2))


if False:
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Contrast(im1b)
    im1b = enhancer.enhance(-2)
    enhancer = ImageEnhance.Contrast(im2b)
    im2b = enhancer.enhance(-2)

#sshow(im1b)
#sshow(im2b)
    
#im1g = im1.convert("L") # ImageOps.grayscale(im1)
#im2g = im2.convert("L") # ImageOps.grayscale(im2)

rgbdiff = ImageChops.difference(im2b, im1b).filter(ImageFilter.GaussianBlur(radius = 5))
sshow(rgbdiff)

diff = ImageChops.difference(im1b, im2b).convert("L")
sshow(diff)

diff = diff.point(lambda p: p > 10 and 255) # point = pixelwise action
diff = diff.filter(ImageFilter.MaxFilter(7))
sshow(diff)

import numpy as np
npim1masked = np.array(im1.resize((700,600)))
npim1masked[:,:,0] = np.multiply(npim1masked[:,:,0], np.array(diff)/255)
npim1masked[:,:,1] = np.multiply(npim1masked[:,:,1], np.array(diff)/255)
npim1masked[:,:,2] = np.multiply(npim1masked[:,:,2], np.array(diff)/255)
#im1masked = ImageChops.multiply(im1b, rgbdiff)
im1masked = Image.fromarray(np.uint8(npim1masked))
sshow(im1masked)
im1masked.save("/tmp/im1masked.jpg")

npim2masked = np.array(im2.resize((700,600)))
npim2masked[:,:,0] = np.multiply(npim2masked[:,:,0], np.array(diff)/255)
npim2masked[:,:,1] = np.multiply(npim2masked[:,:,1], np.array(diff)/255)
npim2masked[:,:,2] = np.multiply(npim2masked[:,:,2], np.array(diff)/255)
#im2masked = ImageChops.multiply(im2b, rgbdiff)
im2masked = Image.fromarray(np.uint8(npim2masked))
sshow(im2masked)
im2masked.save("/tmp/im2masked.jpg")

if False:
    import numpy as np
    import matplotlib.pyplot as plt
    plt.hist(np.array(diff))
    plt.show()

threshold = 30
# https://www.geeksforgeeks.org/python-pil-image-point-method/ 
diffthres = diff.point(lambda p: p > threshold and 255) # point = pixelwise action
# take min value in 3x3 window
diffthres = diffthres.filter(ImageFilter.MinFilter(5))
sshow(diffthres)

bbox = diffthres.getbbox()
print(bbox)
if bbox != None:
    #bbox = (bbox[0]*0.9,bbox[1]*0.9,bbox[2]*1.1,bbox[3]*1.1)
    bbox = (max(0,bbox[0]-0.1*diff.size[0]),
            max(0,bbox[1]-0.1*diff.size[1]),
            min(diff.size[0],bbox[2]+0.1*diff.size[0]),
            min(diff.size[1],bbox[3]+0.1*diff.size[1]))
    if RESIZE:
        bbox2 = (int(bbox[0]*im1.size[0]/700),
                 int(bbox[1]*im1.size[1]/600), 
                 int(bbox[2]*im1.size[0]/700),  
                 int(bbox[3]*im1.size[1]/600))
    else:
        bbox2 = bbox
    im1crop = im1.crop(bbox2)
    sshow(im1crop)    
    im2crop = im2.crop(bbox2)
    sshow(im2crop)
