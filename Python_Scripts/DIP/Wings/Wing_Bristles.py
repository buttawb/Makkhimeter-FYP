import cv2
from matplotlib import pyplot as plt
from skimage import color, img_as_ubyte
from skimage import exposure
from skimage.filters import unsharp_mask


class WB_PreProcessing:
    def __init__(self):
        pass

    def PreProcessing(self, orig_img):
        img = img_as_ubyte(orig_img)
        rgb_gray = color.rgb2gray(img)
        bins = 256
        # equalize_img = exposure.equalize_hist(rgb_gray)
        # adaptiv_img = exposure.equalize_adapthist(rgb_gray, clip_limit=0.03)
        # image ko set kr rahy hain
        img_dark = exposure.adjust_gamma(rgb_gray, gamma=3.5, gain=1)
        equalized_d_img = exposure.equalize_hist(img_dark)
        adaptive_d_img = exposure.equalize_adapthist(img_dark, clip_limit=0.6)
        result_1 = unsharp_mask(adaptive_d_img, radius=5, amount=2)

        return adaptive_d_img, rgb_gray, result_1


class WB_Processing:
    def __init__(self, prep=None):
        self.prep = prep

    def overallbristles(self):
        self.prep = cv2.imread(self.prep, 0)
        th, threshed = cv2.threshold(self.prep, 100, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

        ## findcontours
        cnts = cv2.findContours(threshed, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2]

        ## filter by area
        xcnts = []
        for cnt in cnts:
            if cv2.contourArea(cnt):
                xcnts.append(cnt)

        return len(xcnts)
