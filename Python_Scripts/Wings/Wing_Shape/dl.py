import pickle

from keras_preprocessing.image import img_to_array
from keras.models import load_model
import cv2
import numpy as np


def dl_model(input_img):
    path = 'Python_Scripts/Wings/Wing_Shape/model.h5'
    model = load_model(path)
    test_image = cv2.resize(input_img, (224, 224))
    test_image = img_to_array(test_image) / 255  # convert image to np array and normalize
    test_image = np.expand_dims(test_image, axis=0)  # change dimention 3D to 4D
    result = model.predict(test_image)  # predict diseased palnt or not
    return result


def k_model(path_img):
    path_model = 'Python_Scripts/Wings/Wing_Shape/model.pkl'
    with open(path_model, 'rb') as file:
        loaded_model = pickle.load(file)

    img = cv2.imread(path_img)
    img = cv2.resize(img, (32, 32))
    n_pixels = img.shape[0] * img.shape[1]
    n_channels = img.shape[2]
    new_image = img.reshape(-1, n_pixels * n_channels)
    return loaded_model.predict(new_image)
