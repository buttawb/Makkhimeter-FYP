# from PIL import Image
import pandas as pd
from skimage.morphology import skeletonize
from skimage.segmentation import clear_border
from skimage.util import img_as_ubyte
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import filters, measure
from skimage.filters import unsharp_mask
from skimage import color, exposure


class WD_PreProcessing:
    def __init__(self, img=None):
        self.img = img

    def PreProcessing_1(self):
        pre = self.PreProcessing_2(self.img)
        adaptive_d_img = pre[0]
        # rgb_gray = pre[1]

        # blur the image
        blur_img = filters.median(adaptive_d_img)
        binary_img = filters.threshold_sauvola(blur_img, window_size=15)
        # binary_file = (rgb_gray < binary_img)

        return binary_img

    def PreProcessing_2(self, img2):
        img = img_as_ubyte(img2)
        rgb_gray = color.rgb2gray(img)
        # bins = 256
        # equalize_img = exposure.equalize_hist(rgb_gray)
        # adaptiv_img = exposure.equalize_adapthist(rgb_gray, clip_limit=0.03)

        # image ko set kr rahy hain
        img_dark = exposure.adjust_gamma(rgb_gray, gamma=3.5, gain=1)
        # equalized_d_img = exposure.equalize_hist(img_dark)
        adaptive_d_img = exposure.equalize_adapthist(img_dark, clip_limit=0.6)
        result_1 = unsharp_mask(adaptive_d_img, radius=5, amount=2)

        return adaptive_d_img, rgb_gray, result_1


class WD_Procesing:
    def __init__(self, preprocess_img=None, e_img=None, proc=None):
        self.preprocess_img = preprocess_img
        self.e_img = e_img
        self.proc = proc

    def Dilation(self, val1=7, val2=12):
        _, thresh = cv2.threshold(self.preprocess_img, 80, 255, cv2.THRESH_BINARY_INV)

        kernel = np.ones((int(val1), int(val2)), np.uint8)
        d_im = cv2.dilate(thresh, kernel, iterations=5)
        self.e_img = cv2.erode(d_im, kernel, iterations=4)
        return self.e_img

    def Skelatonize(self, path1, path2, outimg, outimg2):
        _, thresh2 = cv2.threshold(self.e_img, 75, 255, cv2.THRESH_BINARY)
        nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh2, None, None, None, 8, cv2.CV_32S)

        # get CC_STAT_AREA component as stats[label, COLUMN]
        areas = stats[1:, cv2.CC_STAT_AREA]

        result = np.zeros((labels.shape), np.uint8)

        for i in range(0, nlabels - 1):
            if areas[i] >= 11000:  # keep
                result[labels == i + 1] = 255
        # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25,25))
        # morph = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
        morph = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)
        # invert morp image
        mask = 0 - morph
        edge_touching_removed = clear_border(mask)

        skeleton = skeletonize(edge_touching_removed)
        plt.imsave(path1, skeleton, cmap='gray')
        skeleton = cv2.imread(path1, 0)
        kernel = np.ones((20, 2), np.uint8)
        dil = cv2.dilate(skeleton, kernel, iterations=2)

        plt.imsave(path2, dil, cmap='gray')

        img = cv2.imread(path2)
        # Extract only blue channel as DAPI / nuclear (blue) staining is the best
        # channel to perform cell count.
        self.proc = img
        result = self.Processing(edge_touching_removed, outimg, outimg2)
        # result = contours(img, edge_touching_removed, outimg, outimg2)
        return result[0], result[1]

    def Processing(self, edge_touching_removed, outimg, outimg2, flag=False):
        cells = self.proc[:, :, 0]  # Blue channel. Image equivalent to grey image.
        # cells=cv2.resize(img,(386,500))

        adj_img = np.zeros(cells.shape, cells.dtype)

        # Defining alpha and beta:
        alpha = 1.9  # Contrast Control [1.0-3.0]
        beta = 0  # Brightness Control [0-100]

        # Scaling and converting the image contrast and brightness
        adj_img = cv2.convertScaleAbs(cells, alpha=alpha, beta=beta)

        # Blur the image for better edge detection
        img_blur = cv2.medianBlur(adj_img, 3)
        # sharpness apply on images
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        image_sharp = cv2.filter2D(src=img_blur, ddepth=-1, kernel=kernel)
        # cv2.imshow('sharp_img',image_sharp)
        # cv2.imwrite('sharpimage_upd.tif',image_sharp)
        # cv2.waitKey(0)

        ret, thresh = cv2.threshold(image_sharp, 90, 255, cv2.THRESH_BINARY_INV)

        pixels_to_um = 0.5  # 1 pixel = 454 nm (got this from the metadata of original image)

        # Threshold image to binary using OTSU. ALl thresholded pixels will be set to 255
        # ret1, thresh = cv2.threshold(cells, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

        # cv2.imwrite('newthresh.tif',thresh)

        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

        opening = clear_border(opening)

        # cv2.imwrite('opening.tif',opening)

        sure_bg = cv2.dilate(opening, kernel, iterations=3)

        # cv2.imwrite('opening.tif',sure_bg)
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 0)

        # cv2.imwrite('opening.tif',dist_transform)

        ret2, sure_fg = cv2.threshold(dist_transform, 0.001 * dist_transform.max(), 255, 90)

        sure_fg = np.uint8(sure_fg)
        # cv2.imwrite('opening.tif',sure_bg)

        unknown = cv2.subtract(sure_bg, sure_fg)

        ret3, markers = cv2.connectedComponents(thresh)

        markers = markers + 1

        markers = cv2.watershed(self.proc, markers)

        self.proc[markers == -1] = [0, 255, 255]

        if flag:
            result = WD_PostProcessing.RegionProp_FloodFill(self.proc, edge_touching_removed, outimg, outimg2, ret3,
                                                            markers,
                                                            cells)
            df = result[0]
            data = result[1]
            return df, data
        else:
            result = WD_PostProcessing.RegionProp_Skeleton(self.proc, edge_touching_removed, outimg, outimg2, ret3,
                                                           markers,
                                                           cells)
            df = result[0]
            data = result[1]
            return df, data

    def FloodFill(self, path1, path2, outimg, outimg2):

        import cv2
        import numpy as np
        _, thresh2 = cv2.threshold(self.e_img, 75, 255, cv2.THRESH_BINARY)
        nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh2, None, None, None, 8, cv2.CV_32S)

        # get CC_STAT_AREA component as stats[label, COLUMN]
        areas = stats[1:, cv2.CC_STAT_AREA]

        result = np.zeros((labels.shape), np.uint8)

        for i in range(0, nlabels - 1):
            if areas[i] >= 11000:  # keep
                result[labels == i + 1] = 255
        # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25,25))
        # morph = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
        morph = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)
        # invert morp image
        mask = 0 - morph
        # edge_touching_removed = clear_border(mask)

        # cv2.imwrite('result.png', result)

        h, w = result.shape[:2]

        # create zeros mask 2 pixels larger in each dimension
        mask = np.zeros([h + 2, w + 2], np.uint8)

        # floodfill outer white border with black
        img_floodfill = cv2.floodFill(result, mask, (0, 0), 0, (5), (0), flags=8)[1]

        # remove border
        img_floodfill = img_floodfill[1:h - 1, 1:w - 1]

        cv2.imwrite(path1, img_floodfill)

        from skimage import measure, color, io
        from skimage.segmentation import clear_border
        import pandas as pd

        img = cv2.imread(path1)
        self.proc = img
        # Extract only blue channel as DAPI / nuclear (blue) staining is the best
        # channel to perform cell count.
        result = self.Processing(img_floodfill, outimg, outimg2, flag=True)
        # result = contours(img, img_floodfill, outimg, outimg2)
        return result[0], result[1]


class WD_PostProcessing(WD_Procesing):
    def __init__(self):
        WD_Procesing.__init__(self)

    @staticmethod
    def RegionProp_Skeleton(img, edge_touching_removed, outimg, outimg2, ret3, markers, cells):
        regions = measure.regionprops_table(markers, cells,
                                            properties=['label',
                                                        'area',
                                                        'perimeter', 'centroid'])
        df = pd.DataFrame(regions)
        df['Ar'] = df['area'] * (100 / 413)
        df['Pr'] = df['perimeter'] * (100 / 413)
        # length=df[2:]
        # if length<4:
        #     raise 'Error'

        # cv2.imwrite('wshseg_colors.png', output)
        # cv2.imwrite('wshseg_boxes.png', output2)

        df = df.drop(columns='perimeter', axis=1)
        df = df.drop(columns='area', axis=1)
        
        n_df = df[df['Ar'] > 200]
        n_df = n_df.reset_index()
        print(n_df)

        # st.write(df)

        output = np.zeros_like(img)
        output2 = img.copy()
        center1 = n_df['centroid-0']
        center2 = n_df['centroid-1']

        n_df.rename(columns={'centroid-0': 'centroid0'}, inplace=True)
        n_df.rename(columns={'centroid-1': 'centroid1'}, inplace=True)

        from skimage import color
        img2 = color.label2rgb(markers, bg_label=0)

        # Iterate over all non-background labels
        for i in range(2, len(n_df)):
            a = 0
            b = 0
            mask = np.where(markers == i, np.uint8(255), np.uint8(0))
            x, y, w, h = cv2.boundingRect(mask)
            area = cv2.countNonZero(mask[y:y + h, x:x + w])

            # Visualize
            color = np.uint8(np.random.random_integers(0, 0, 3)).tolist()
            output[mask != 0] = color
            Y = center1[i]
            X = center2[i]
            l = i + 1
            cv2.putText(img2, '%d' % l, (int(X), int(Y)), cv2.FONT_HERSHEY_SIMPLEX, 3.9, color, 15, cv2.LINE_AA)

        # plt.imshow(img2, cmap='jet')
        # plt.show()
        # print(df)
        # st.image(img2,width=400)

        # area=sum(df['Area in mm^2'].iloc[2:13])

        contours = cv2.findContours(edge_touching_removed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        big_contour = max(contours, key=cv2.contourArea)

        # draw white filled contour on black background
        result = np.zeros_like(edge_touching_removed)
        cv2.drawContours(result, [big_contour], 0, (255, 255, 255), cv2.FILLED)

        # plt.imshow(result,cmap='gray')
        # st.image(result, width=400)
        # --------------------------------------------------------------------------------------
        props = measure.regionprops_table(result, edge_touching_removed,
                                          properties=['label',
                                                      'area', 'perimeter'])
        data = pd.DataFrame(props)
        data['Ar'] = data['area'] * (100 / 413)
        data['Pr'] = data['perimeter'] * (100 / 413)
        data.drop(columns='area', inplace=True)
        data.drop(columns='perimeter', inplace=True)
        plt.imsave(outimg, img2)
        plt.imsave(outimg2, result)

        return n_df, data

    @staticmethod
    def RegionProp_FloodFill(img, img_floodfill, outimg, outimg2, ret3, markers, cells):
        regions = measure.regionprops_table(markers, cells,
                                            properties=['label',
                                                        'area',
                                                        'perimeter', 'centroid'])
        df = pd.DataFrame(regions)
        df['Ar'] = df['area'] * (100 / 413)
        df['Pr'] = df['perimeter'] * (100 / 413)

        # cv2.imwrite('wshseg_colors.png', output)
        # cv2.imwrite('wshseg_boxes.png', output2)

        df = df.drop(columns='perimeter', axis=1)
        df = df.drop(columns='area', axis=1)
        print(df)

        n_df = df[df['Ar'] > 200]
        n_df = n_df.reset_index()
        print(n_df)

        # st.write(df)

        # output = np.zeros_like(img)

        center1 = n_df['centroid-0']
        center2 = n_df['centroid-1']

        from skimage import color
        img2 = color.label2rgb(markers, bg_label=0)
        output = img2.copy()

        # Iterate over all non-background labels
        for i in range(2, len(n_df)):
            a = 0
            b = 0
            mask = np.where(markers == i, np.uint8(255), np.uint8(0))
            x, y, w, h = cv2.boundingRect(mask)
            area = cv2.countNonZero(mask[y:y + h, x:x + w])

            # Visualize
            color = np.uint8(np.random.random_integers(0, 0, 3)).tolist()
            output[mask != 0] = color
            Y = center1[i]
            X = center2[i]
            l = i + 1

            cv2.putText(img2, '%d' % l, (int(X), int(Y)), cv2.FONT_HERSHEY_SIMPLEX, 3.9, color, 15, cv2.LINE_AA)



        # plt.imshow(img2, cmap='jet')
        # plt.show()
        # print(df)
        # st.image(img2,width=400)

        # area=sum(df['Area in mm^2'].iloc[2:13])

        contours = cv2.findContours(img_floodfill, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        big_contour = max(contours, key=cv2.contourArea)

        # draw white filled contour on black background
        result = np.zeros_like(img_floodfill)
        cv2.drawContours(result, [big_contour], 0, (255, 255, 255), cv2.FILLED)

        # plt.imshow(result,cmap='gray')
        # st.image(result, width=400)
        # --------------------------------------------------------------------------------------
        props = measure.regionprops_table(result, img_floodfill,
                                          properties=['label',
                                                      'area', 'perimeter'])
        data = pd.DataFrame(props)
        data['Ar'] = data['area'] * (100 / 413)
        data['Pr'] = data['perimeter'] * (100 / 413)
        data.drop(columns='area', inplace=True)
        data.drop(columns='perimeter', inplace=True)
        plt.imsave(outimg, img2)
        plt.imsave(outimg2, result)

        return n_df, data

# def prepreprocess(orig_img):
#     img = img_as_ubyte(orig_img)
#     rgb_gray = color.rgb2gray(img)
# #     bins = 256
# #     # equalize_img = exposure.equalize_hist(rgb_gray)
# #     # adaptiv_img = exposure.equalize_adapthist(rgb_gray, clip_limit=0.03)
# #     # image ko set kr rahy hain
# #     img_dark = exposure.adjust_gamma(rgb_gray, gamma=3.5, gain=1)
# #     equalized_d_img = exposure.equalize_hist(img_dark)
# #     adaptive_d_img = exposure.equalize_adapthist(img_dark, clip_limit=0.6)
# #     result_1 = unsharp_mask(adaptive_d_img, radius=5, amount=2)
# #
# #     return adaptive_d_img, rgb_gray, result_1

#
# def preprocess(orig_img):
#     pre = prepreprocess(orig_img)
#     adaptive_d_img = pre[0]
#     rgb_gray = pre[1]
#     # blur the image
#     blur_img = filters.median(adaptive_d_img)
#     binary_img = filters.threshold_sauvola(blur_img, window_size=15)
#     binary_file = (rgb_gray < binary_img)
#     return binary_img
#
#
# def dilation(img, val1=7, val2=12):
#     # img = cv2.imread('./skimage_binary_result.png', 0)
#     _, thresh = cv2.threshold(img, 80, 255, cv2.THRESH_BINARY_INV)
#
#     kernel = np.ones((int(val1), int(val2)), np.uint8)
#     d_im = cv2.dilate(thresh, kernel, iterations=5)
#     e_im = cv2.erode(d_im, kernel, iterations=4)
#     return e_im
#
#
# def skeleton(e_im, path1, path2, outimg, outimg2):
#     _, thresh2 = cv2.threshold(e_im, 75, 255, cv2.THRESH_BINARY)
#     nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh2, None, None, None, 8, cv2.CV_32S)
#
#     # get CC_STAT_AREA component as stats[label, COLUMN]
#     areas = stats[1:, cv2.CC_STAT_AREA]
#
#     result = np.zeros((labels.shape), np.uint8)
#
#     for i in range(0, nlabels - 1):
#         if areas[i] >= 11000:  # keep
#             result[labels == i + 1] = 255
#     # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25,25))
#     # morph = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)
#     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
#     morph = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)
#     # invert morp image
#     mask = 0 - morph
#     edge_touching_removed = clear_border(mask)
#
#     skeleton = skeletonize(edge_touching_removed)
#     plt.imsave(path1, skeleton, cmap='gray')
#     skeleton = cv2.imread(path1, 0)
#     kernel = np.ones((20, 2), np.uint8)
#     dil = cv2.dilate(skeleton, kernel, iterations=2)
#
#     plt.imsave(path2, dil, cmap='gray')
#
#     img = cv2.imread(path2)
#     # Extract only blue channel as DAPI / nuclear (blue) staining is the best
#     # channel to perform cell count.
#     result = contours(img, edge_touching_removed, outimg, outimg2)
#     return result[0], result[1]
#
#
# def contours(img, edge_touching_removed, outimg, outimg2):
#     cells = img[:, :, 0]  # Blue channel. Image equivalent to grey image.
#     # cells=cv2.resize(img,(386,500))
#
#     adj_img = np.zeros(cells.shape, cells.dtype)
#
#     # Defining alpha and beta:
#     alpha = 1.9  # Contrast Control [1.0-3.0]
#     beta = 0  # Brightness Control [0-100]
#
#     # Scaling and converting the image contrast and brightness
#     adj_img = cv2.convertScaleAbs(cells, alpha=alpha, beta=beta)
#
#     # Blur the image for better edge detection
#     img_blur = cv2.medianBlur(adj_img, 3)
#     # sharpness apply on images
#     kernel = np.array([[0, -1, 0],
#                        [-1, 5, -1],
#                        [0, -1, 0]])
#     image_sharp = cv2.filter2D(src=img_blur, ddepth=-1, kernel=kernel)
#     # cv2.imshow('sharp_img',image_sharp)
#     # cv2.imwrite('sharpimage_upd.tif',image_sharp)
#     # cv2.waitKey(0)
#
#     ret, thresh = cv2.threshold(image_sharp, 90, 255, cv2.THRESH_BINARY_INV)
#
#     pixels_to_um = 0.5  # 1 pixel = 454 nm (got this from the metadata of original image)
#
#     # Threshold image to binary using OTSU. ALl thresholded pixels will be set to 255
#     # ret1, thresh = cv2.threshold(cells, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
#
#     # cv2.imwrite('newthresh.tif',thresh)
#
#     kernel = np.ones((3, 3), np.uint8)
#     opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
#
#     opening = clear_border(opening)
#
#     # cv2.imwrite('opening.tif',opening)
#
#     sure_bg = cv2.dilate(opening, kernel, iterations=3)
#
#     # cv2.imwrite('opening.tif',sure_bg)
#     dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 0)
#
#     # cv2.imwrite('opening.tif',dist_transform)
#
#     ret2, sure_fg = cv2.threshold(dist_transform, 0.001 * dist_transform.max(), 255, 90)
#
#     sure_fg = np.uint8(sure_fg)
#     # cv2.imwrite('opening.tif',sure_bg)
#
#     unknown = cv2.subtract(sure_bg, sure_fg)
#
#     ret3, markers = cv2.connectedComponents(thresh)
#
#     markers = markers + 1
#
#     markers = cv2.watershed(img, markers)
#
#     img[markers == -1] = [0, 255, 255]
#
#     from skimage import color
#     img2 = color.label2rgb(markers, bg_label=0)
#
#     regions = measure.regionprops_table(markers, cells,
#                                         properties=['label',
#                                                     'area',
#                                                     'perimeter', 'centroid'])
#     df = pd.DataFrame(regions)
#     df['Ar'] = df['area'] * (100 / 413)
#     df['Pr'] = df['perimeter'] * (100 / 413)
#     # length=df[2:]
#     # if length<4:
#     #     raise 'Error'
#
#     # cv2.imwrite('wshseg_colors.png', output)
#     # cv2.imwrite('wshseg_boxes.png', output2)
#
#     df = df.drop(columns='perimeter', axis=1)
#     df = df.drop(columns='area', axis=1)
#
#     # st.write(df)
#
#     output = np.zeros_like(img)
#     output2 = img.copy()
#     center1 = df['centroid-0']
#     center2 = df['centroid-1']
#
#     df.rename(columns={'centroid-0': 'centroid0'}, inplace=True)
#     df.rename(columns={'centroid-1': 'centroid1'}, inplace=True)
#
#     # Iterate over all non-background labels
#     for i in range(2, ret3):
#         a = 0
#         b = 0
#         mask = np.where(markers == i, np.uint8(255), np.uint8(0))
#         x, y, w, h = cv2.boundingRect(mask)
#         area = cv2.countNonZero(mask[y:y + h, x:x + w])
#
#         # Visualize
#         color = np.uint8(np.random.random_integers(0, 0, 3)).tolist()
#         output[mask != 0] = color
#         Y = center1[i]
#         X = center2[i]
#         l = i + 1
#         cv2.putText(img2, '%d' % l, (int(X), int(Y)), cv2.FONT_HERSHEY_SIMPLEX, 3.9, color, 15, cv2.LINE_AA)
#
#     # plt.imshow(img2, cmap='jet')
#     # plt.show()
#     # print(df)
#     # st.image(img2,width=400)
#
#     # area=sum(df['Area in mm^2'].iloc[2:13])
#
#     contours = cv2.findContours(edge_touching_removed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     contours = contours[0] if len(contours) == 2 else contours[1]
#     big_contour = max(contours, key=cv2.contourArea)
#
#     # draw white filled contour on black background
#     result = np.zeros_like(edge_touching_removed)
#     cv2.drawContours(result, [big_contour], 0, (255, 255, 255), cv2.FILLED)
#
#     # plt.imshow(result,cmap='gray')
#     # st.image(result, width=400)
#     # --------------------------------------------------------------------------------------
#     props = measure.regionprops_table(result, edge_touching_removed,
#                                       properties=['label',
#                                                   'area', 'perimeter'])
#     data = pd.DataFrame(props)
#     data['Ar'] = data['area'] * (100 / 413)
#     data['Pr'] = data['perimeter'] * (100 / 413)
#     data.drop(columns='area', inplace=True)
#     data.drop(columns='perimeter', inplace=True)
#     plt.imsave(outimg, img2)
#     plt.imsave(outimg2, result)
#
#     return df, data
#
#
# # def region_props(param1, param2, properties=None):
# #     if properties is None:
# #         properties = ['label', 'area', 'perimeter']
# #     props = measure.regionprops_table(param1, param2, properties)
# #     df = pd.DataFrame(props)
# #     df['Area in µm²'] = df['area'] * (100 / 413)
# #     df['Perimeter in µm'] = df['perimeter'] * (100 / 413)
# #     return df
#
#
# def other_option(e_im, path1, path2, outimg, outimg2):
#     import cv2
#     import numpy as np
#     _, thresh2 = cv2.threshold(e_im, 75, 255, cv2.THRESH_BINARY)
#     nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh2, None, None, None, 8, cv2.CV_32S)
#
#     # get CC_STAT_AREA component as stats[label, COLUMN]
#     areas = stats[1:, cv2.CC_STAT_AREA]
#
#     result = np.zeros((labels.shape), np.uint8)
#
#     for i in range(0, nlabels - 1):
#         if areas[i] >= 11000:  # keep
#             result[labels == i + 1] = 255
#     # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25,25))
#     # morph = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)
#     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
#     morph = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)
#     # invert morp image
#     mask = 0 - morph
#     # edge_touching_removed = clear_border(mask)
#
#     # cv2.imwrite('result.png', result)
#
#     h, w = result.shape[:2]
#
#     # create zeros mask 2 pixels larger in each dimension
#     mask = np.zeros([h + 2, w + 2], np.uint8)
#
#     # floodfill outer white border with black
#     img_floodfill = cv2.floodFill(result, mask, (0, 0), 0, (5), (0), flags=8)[1]
#
#     # remove border
#     img_floodfill = img_floodfill[1:h - 1, 1:w - 1]
#
#     cv2.imwrite(path1, img_floodfill)
#
#     from skimage import measure, color, io
#     from skimage.segmentation import clear_border
#     import pandas as pd
#
#     img = cv2.imread(path1)
#     # Extract only blue channel as DAPI / nuclear (blue) staining is the best
#     # channel to perform cell count.
#     result = contours(img, img_floodfill, outimg, outimg2)
#     return result[0], result[1]
