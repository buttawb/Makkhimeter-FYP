import cv2
import numpy as np
from skimage import measure, color
import matplotlib.pyplot as plt
import pandas as pd


class Segmenting:
    def __init__(self, img=None):
        self.img = img
        pass

    def Segmentation(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pixel_values = image.reshape((-1, 3))
        pixel_values = np.float32(pixel_values)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        k = 4
        _, labels, (centers) = cv2.kmeans(pixel_values, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        labels = labels.flatten()
        segmented_image = centers[labels.flatten()]
        segmented_image = segmented_image.reshape(image.shape)
        masked_image = np.copy(image)
        masked_image = masked_image.reshape((-1, 3))
        cluster = 4
        masked_image[labels == cluster] = [0, 0, 0]
        masked_image = masked_image.reshape(image.shape)
        return masked_image


class Extraction:
    def __init__(self):
        pass

    def Processing(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower = np.array([118, 76, 0])
        upper = np.array([179, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(image, image, mask=mask)

        _, thresh2 = cv2.threshold(result, 0, 255, cv2.THRESH_BINARY)
        kernel = np.ones((3, 3), np.uint8)
        d_im = cv2.dilate(thresh2, kernel, iterations=2)
        d_im = cv2.cvtColor(d_im, cv2.COLOR_BGR2GRAY)
        contours = cv2.findContours(d_im, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        big_contour = max(contours, key=cv2.contourArea)
        result = np.zeros_like(d_im)
        cv2.drawContours(result, [big_contour], 0, (255, 255, 255), cv2.FILLED)
        return result, d_im


class PostProcessing:

    def __init__(self):
        pass

    def Tables(self, result, d_im):
        props = measure.regionprops_table(result, d_im,
                                          properties=['label',
                                                      'area', 'perimeter'])

        data = pd.DataFrame(props)
        data['Area in mm^2'] = data['area'] * (100 / 413)
        data['Permiter in mm'] = data['perimeter'] * (100 / 413)
        data.drop(columns='area', inplace=True)
        data.drop(columns='perimeter', inplace=True)
        return data
