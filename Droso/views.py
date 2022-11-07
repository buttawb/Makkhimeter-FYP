import os

import matplotlib.pyplot as plt
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
import io
from django.shortcuts import render, redirect
from Droso.models import *

from PIL import Image
import numpy as np
from Python_Scripts.DIP.Image_Processing import *
from Python_Scripts.DL import dl
import pandas as pd
import uuid


def loginUser(request):
    if request.method == "POST":
        # GET AND AUTHENTICATE USERNAME AND PASSWORD
        username = request.POST.get('username')
        password = request.POST.get('password')
        # print(username, password)
        user = authenticate(username=username, password=password)

        if user is not None:
            # IF LOGIN CREDENTIALS ARE CORRECT.
            login(request, user)
            return redirect("/")
        else:
            # IF LOGIN CREDENTIALS ARE WRONG.
            return render(request, 'user/login.html', {'note': 'Wrong Login credentials detected.'})

    return render(request, 'user/login.html', {'note2': 'Enter username and password to continue...'})


def logoutUser(request):
    # LOGOUT USER
    logout(request)

    return render(request, 'user/logout.html')


def __find_userpath(request):
    # GET USERNAME AMD FIND ITS PATH
    u_name = str(request.user)
    base = 'static/users'
    path = base + '/' + u_name
    return path


def main(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    path = __find_userpath(request)
    # CHECK THE VERY EXISTENCE OF THE DIRECTORY
    is_exist = os.path.exists(path)
    if is_exist:
        pass
    else:
        # MAKE A DIRECTORY NAMED WITH USERNAME
        os.mkdir(path)

    return render(request, 'index.html', {'head': 'Drosometer | DOW-UIT'})


def wingdimen(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    return render(request, 'wings/dimensions/w_dimen.html', {'head': 'Drosometer | Wings'})


def wingdimen2(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    if request.method == 'POST':
        uploaded_img = request.FILES['img']
        img1 = __reader(uploaded_img)
        img2 = img1.convert('RGB')
        pre_process = preprocess(img2)

        save_file = __upload_file_to_userdir(request, pre_process, '.png', flag=False)
        file_path = save_file
        plt.imsave(file_path, pre_process, cmap='gray')

        for_dil = cv2.imread(file_path, 0)
        dil = dilation(for_dil)
        save_dil = __upload_file_to_userdir(request, dil, '.png', flag=False)
        global dil_path
        dil_path = save_dil
        plt.imsave(dil_path, dil, cmap='gray')

        return redirect('/bar',
                        {'head': 'Drosometer | Wings', 'img_path': dil_path, 'img_name': 'Uploaded Image'})

    return render(request, 'wings/dimensions/w_dimen2.html',
                  {'head': 'Wings | Dimensions', 'img_path': '../static/images/perfect.png',
                   'img_name': 'Like this: '})


def wingshape(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    return render(request, 'wings/shape/w_shape.html', {'head': 'Drosometer | Wings'})


def __reader(obj):
    # FUNCTION TO READ IMAGES
    data = obj.read()
    file = io.BytesIO(data)
    open_file = Image.open(file)

    return open_file


def __upload_file_to_userdir(request, file, file_format, flag=True):
    # ASSIGNS NAME AND PATH TO THE FILE
    # SAVE FILE ONLY IF FLAG IS TRUE
    path = __find_userpath(request)
    rand_name = str(uuid.uuid4())
    final_path = path + "/" + rand_name + file_format
    if flag:
        # UPLOADS USER FILES TO THEIR DIRECTORY
        file.save(final_path)
        return final_path
    else:
        return final_path


def wingshape2(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    if request.method == 'POST':
        uploaded_img = request.FILES['img']
        img1 = __reader(uploaded_img)
        # yeh ubyte ko dena hai wind dimension
        # IMAGE CONVERSIONS FOR THE DL MODEL.
        img2 = img1.convert('RGB')
        path = __upload_file_to_userdir(request, img2, '.png')
        img3 = np.array(img2)

        # APPLYING MODEL
        result = dl.dl_model(img3)
        pred = np.argmax(result, axis=1)
        table = pd.DataFrame(result, columns=['Mutation', 'Oregan'])

        # ITERATING
        for index, row in table.iterrows():
            prob_mut = row['Mutation']
            prob_oreg = row['Oregan']

        # CREATING OBJECT AND SAVING ALL OUTPUTS TO DATABASE THROUGH MODEL
        shape = w_shape()
        shape.ws_o_img = path
        if pred == 0:
            shape.ws_pred = 'Mutation'
        else:
            shape.ws_pred = 'Oregan'
        shape.ws_normal_prob = prob_oreg
        shape.ws_mutated_prob = prob_mut
        shape.save()

        if pred == 0:
            # RENDERING OUTPUTS ON HTML PAGE
            return render(request, 'wings/shape/w_shape2.html',
                          {'head': 'Wings | Shape', 'ans': 'Mutated', 'out': 'class.', 'prob_mut': prob_mut,
                           'prob_oreg': prob_oreg, 'img_path': path, 'img_name': 'Uploaded Image: '})

        elif pred == 1:
            # RENDERING OUTPUTS ON HTML PAGE
            return render(request, 'wings/shape/w_shape2.html',
                          {'head': 'Wings | Shape', 'ans': 'Oregan', 'out': 'class.', 'prob_oreg': prob_oreg,
                           'prob_mut': prob_mut, 'img_path': path, 'img_name': 'Uploaded Image: '})

    else:
        return render(request, 'wings/shape/w_shape2.html',
                      {'head': 'Wings | Shape', 'img_path': '../static/images/perfect.png',
                       'img_name': 'Like this: '})


def wingbristles(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    return render(request, 'wings/bristles/w_bristles.html', {'head': 'Drosometer | Wings'})


def wingbristles2(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    if request.method == "POST":
        uploaded_img = request.FILES['img']
        img1 = __reader(uploaded_img)

        global crop_img
        crop_img = __upload_file_to_userdir(request, img1, ".png")
        print(crop_img)

        img = Image.open(crop_img)
        img1 = prepreprocess(img)
        plt.imsave(crop_img, img1[2], cmap='gray')

        return redirect("/cropper_wing", {'head': 'Bristles | Finder', 'img': crop_img})

    return render(request, 'wings/bristles/w_bristles2.html',
                  {'head': 'Wings | Bristles', 'img_path': '../static/images/perfect.png',
                   'img_name': 'Like this: '})


def cropper_bristles(request):
    if request.user.is_anonymous:
        return redirect("/login")

    return render(request, 'wings/bristles/cropper.html', {'head': 'Bristles | Finder', 'img': crop_img})


def cropper_eye(request):
    if request.user.is_anonymous:
        return redirect("/login")

    return render(request, 'wings/bristles/cropper.html', {'head': 'Ommatidium | Finder', 'img': img2})


def c_us(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    return render(request, 'others/contactus.html', {'head': 'Drosometer | Contact Us'})


def a_us(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    return render(request, 'others/aboutus.html', {'head': 'Drosometer | About Us'})


def f_b(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    return render(request, 'others/feedback.html', {'head': 'Drosometer | Give Feedback'})


def wing_f(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")
    return render(request, 'f_w.html', {'head': 'Drosometer | Wings'})


def eye_f(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    return render(request, 'f_e.html', {'head': 'Drosometer | Eyes'})


# def thorax_f(request):
#     if request.user.is_anonymous:
#         return redirect("/login")
#     return render(request, 'f_t.html', {'head': 'Drosometer | Thorax'})
#

def w_option(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    return render(request, 'wings/dimensions/opt.html', {'head': 'Drosometer | Wings'})


def w_bar(request):
    if request.user.is_anonymous:
        return redirect("/login")
    # es image pr kaam karna hai
    print(dil_path)
    val1 = 0
    if request.method == 'POST':
        # VALUE GET NAI HORAI
        val1 = float(request.GET['range'])
        print(val1)
        return HttpResponse("VALUE GOT", val1)

    # dil = dilation(dil_path, val1, val2=5)
    # save_dil = __upload_file_to_userdir(request, dil, '.png', flag=False)
    #
    # dil_path1 = save_dil[1]
    #
    # plt.imsave(dil_path1, dil, cmap='gray')
    #
    # return render(request, 'wings/dimensions/bar.html',
    #               {'head': 'Drosometer | Wings', 'img_path': dil_path1, 'img_name': 'Uploaded Image'})
    else:
        return render(request, 'wings/dimensions/bar.html',
                      {'head': 'Dimensions | Exposure', 'img_path': dil_path, 'img_name': 'Uploaded Image'})


def eye_omat(request):
    if request.user.is_anonymous:
        return redirect("/login")

    return render(request, 'eyes/ommatidum/omat_count.html',
                  {'head': 'Drosometer | Eyes'})


def eye_omat2(request):
    if request.user.is_anonymous:
        return redirect("/login")

    if request.method == 'POST':
        uploaded_img = request.FILES['img']
        img1 = __reader(uploaded_img)

        global img2
        img2 = __upload_file_to_userdir(request, img1, '.png')

        img = Image.open(img2)
        img = prepreprocess(img)

        plt.imsave(img2, img[2], cmap='gray')

        return redirect('/cropper_eye', {'head': 'Ommatidium | Count', 'img': img2})

    return render(request, 'eyes/ommatidum/omat_2.html',
                  {'head': 'Eyes | Ommatidium Count', 'img_path': '../static/images/eye_front.png',
                   'img_name': 'Like this: '})
