import sys
import cv2
import numpy as np
imagecv = cv2.imread(sys.argv[1])


def resizeaspectratio(imagecv, width = None, inter = cv2.INTER_AREA):
    dim = None
    (h, w) = imagecv.shape[:2]
    if width is None:
        return imagecv
    else:
        if w>=width:
            # calculate the ratio of the width and construct the
            # dimensions
            r = width / float(w)
            dim = (width, int(h * r))
            return cv2.resize(imagecv, dim, interpolation = inter)
        else:
            return imagecv


#cv2.imshow('image' , resizeaspectratio(imagecv, width = int(sys.argv[2])))
#cv2.waitKey(10000)
#cv2.destroyAllWindows()


from PIL import Image
image = Image.fromarray(cv2.cvtColor(imagecv, cv2.COLOR_BGR2RGB))

def resizeaspectratio(image, width = None):
    (w, h) = image.size
    if width is None:
        return image, 1.
    else:
        if w>=width:
            # calculate the ratio of the width and construct the
            # dimensions
            ratio = width / float(w)
            newsize = (width, int(h * ratio))
            return image.resize(size=newsize), ratio 
        else:
            return image, 1.
        
image2, ratio = resizeaspectratio(image, width = 512)
print(ratio)
image2.show()
