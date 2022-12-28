from skimage import color, img_as_ubyte
from skimage import exposure
from skimage.filters import unsharp_mask


class EO_PreProcessing:
    def __init__(self):
        pass

    def PreProcessing(self, orig_img):
        img = img_as_ubyte(orig_img)
        rgb_gray = color.rgb2gray(img)
        # bins = 256
        # img_dark = exposure.adjust_gamma(rgb_gray, gamma=3.5, gain=1)
        # = exposure.equalize_hist(img_dark)
        # adaptive_d_img = exposure.equalize_adapthist(img_dark, clip_limit=0.6)
        # result_1 = unsharp_mask(adaptive_d_img, radius=5, amount=2)

        return rgb_gray
