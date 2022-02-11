# https://stackoverflow.com/questions/189943/how-can-i-quantify-difference-between-two-images
import sys

def sshow(im):
    im.copy().resize((700,600)).show()
    
from PIL import Image, ImageOps, ImageChops, ImageFilter
im1 = Image.open(sys.argv[1])
im2 = Image.open(sys.argv[2])

import numpy as np
def normalize(img):
    """
    Linear normalization
    """
    arr = np.array(img)
    arr = arr.astype('float')
    # Do not touch the alpha channel
    for i in range(3):
        minval = np.percentile(arr[...,i], 25) #arr[...,i].min()
        maxval = np.percentile(arr[...,i], 75) #arr[...,i].max()
        print(minval,maxval)
        if minval != maxval:
            arr[...,i] -= minval
            arr[...,i] *= (255.0/(maxval-minval))
    return Image.fromarray(arr.astype('uint8'),'RGB')

RESIZE = True
if RESIZE:
    im1b = im1.resize((700,600)).filter(ImageFilter.GaussianBlur(radius = 2))
    im2b = im2.resize((700,600)).filter(ImageFilter.GaussianBlur(radius = 2))
else:
    im1b = im1.filter(ImageFilter.GaussianBlur(radius = 5))
    im2b = im2.filter(ImageFilter.GaussianBlur(radius = 5))

#im1g = im1.convert("L") # ImageOps.grayscale(im1)
#im2g = im2.convert("L") # ImageOps.grayscale(im2)

#diff = ImageChops.difference(im2g, im1g)
diff = ImageChops.difference(im1b, im2b).convert("L")
sshow(diff)

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
