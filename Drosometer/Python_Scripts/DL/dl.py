from keras_preprocessing.image import img_to_array
from keras.models import load_model
import cv2
import numpy as np


def dl_model(input_img):
    path = 'D:\Projects\Django\Loyola Application\wel\model.h5'
    model = load_model(path)
    test_image = cv2.resize(input_img, (224, 224))
    test_image = img_to_array(test_image) / 255  # convert image to np array and normalize
    test_image = np.expand_dims(test_image, axis=0)  # change dimention 3D to 4D
    result = model.predict(test_image)  # predict diseased palnt or not
    return result
