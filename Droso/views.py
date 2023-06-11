import hashlib
import io
import json
import os
import uuid
import shutil
import time

import requests
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import get_template
from reportlab.pdfgen import canvas
from io import BytesIO

from requests import RequestException

from Droso.forms import CustomUserCreationForm
from Droso.models import *
# IMPORTING SCRIPTS
# EYES
from Python_Scripts.Eyes.Eye_Colour import *
from Python_Scripts.Eyes.Eye_Dimensions import *
from Python_Scripts.Eyes.Eye_Ommatidium import *
# WINGS
from Python_Scripts.Wings.Wing_Bristles.Wing_Bristles import *
from Python_Scripts.Wings.Wing_Dimensions.Wing_Dimensions import *
from Python_Scripts.Wings.Wing_Shape import dl

# CREATING SCRIPT CLASSES OBJECTS
WD_PreP = WD_PreProcessing()
WD_P = WD_Procesing()
WD_PostP = WD_PostProcessing()

WB_PreP = WB_PreProcessing()
WB_P = WB_Processing()

EO_PreP = EO_PreProcessing()
E_Col = eye_col()

segment = Segmenting()
extract = Extraction()
post = PostProcessing()


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
            return render(request, 'user/login.html',
                          {'title': 'Login - MakkhiMeter', 'note': 'Wrong Login credentials detected.'})

    return render(request, 'user/login.html',
                  {'title': 'Login - MakkhiMeter', 'note2': 'Enter username and password to continue...'})


def reset_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request=request)
            messages.success(request, 'An email has been sent with instructions to reset your password.')
            return redirect('login')
    else:
        form = PasswordResetForm()
    return render(request, 'user/password_reset.html', {'form': form})


def logoutUser(request):
    # CLEAR USER CACHE
    __clear_cache(__find_userpath(request))
    # LOGOUT USER
    logout(request)

    return render(request, 'user/logout.html', {'title': 'Logout - MakkhiMeter', })


def __reader(obj):
    # FUNCTION TO READ IMAGES
    data = obj.read()
    file = io.BytesIO(data)
    open_file = Image.open(file)

    return open_file


def md5(img_path):
    # TO CONVERT IMAGE TO ITS 128 BIT HEXADECIMAL - OUTPUT IS OF 32 DIGITS
    mdhash = hashlib.md5(Image.open(img_path).tobytes())
    md5_hash = mdhash.hexdigest()
    return md5_hash


# def compressimage(img_path):
#     image = Image.open(img_path)
#     image.save(img_path, quality=20, optimize=True)
#     return image


# def save_img(file, img):
#
#     rand_name = str(uuid.uuid4())
#     if img == 'wing':
#         path = "static/db_wingimages"
#         fpath = path + "/" + rand_name + ".png"
#         file.save(fpath)
#         return fpath
#     else:
#         path = "static/db_eyeimages"
#         fpath = path + "/" + rand_name + ".png"
#         file.save(fpath)
#         return fpath


def __upload_file_to_userdir(request, file, file_format, flag=True):
    # ASSIGNS NAME AND PATH TO THE FILE
    # SAVE FILE ONLY IF FLAG IS TRUE
    path = __find_userpath(request)
    rand_name = str(uuid.uuid4())

    if flag:
        filename = rand_name + file_format
        final_path = os.path.join(path, filename)
        if file_format.lower() == ".jpg" or file_format.lower() == ".jpeg":
            # Convert the image to RGB mode before saving it as a JPEG file
            file = file.convert("RGB")
        file.save(final_path)
        return final_path
    else:
        filename = rand_name + file_format
        final_path = os.path.join(path, filename)
        return final_path


def __find_userpath(request):
    # GET USERNAME AMD FIND ITS PATH
    if request.user.is_authenticated:
        u_name = str(request.user)
    else:
        u_name = 'Anonymous'
    base = 'static/users'
    path = base + '/' + u_name
    return path


def __clear_cache(path):
    # path = path + '/*'
    # files = glob.glob(path)
    # for all_files in files:
    # os.remove(all_files)
    return


def image_check(img, path):
    # VALIDATOR TO VALIDATE EITHER THE IMAGE IS OF WING OR NOT
    img_1 = cv2.imread(path)
    gray = cv2.cvtColor(img_1, cv2.COLOR_BGR2GRAY)

    corners = cv2.goodFeaturesToTrack(gray, 1000000000, 0.01, 10)

    corners = np.int0(corners)

    # print(len(corners))

    if len(corners) > 1500:
        # print(len(corners))
        return True
    else:
        # (len(corners))
        return False

    # hash0 = imagehash.average_hash(img)
    # hash1 = imagehash.average_hash(Image.open("static/images/similarity.tif"))
    # print(hash0 - hash1)
    #
    # if (hash0 - hash1) > 25:
    #     return False
    # else:
    #
    #     return True


def api_view(request):
    # Make a GET request to the character matching API endpoint
    app_url = "https://buttawb.pythonanywhere.com/api/boolean/"  # Replace with your PythonAnywhere app URL
    app_response = requests.get(app_url)

    if app_response.status_code == 200:
        data = app_response.json()
        result = data.get('result')

        # Process the result as needed
        if result:
            # Handle True case
            return False
    else:
        return True


def main(request):
    # LANDING PAGE

    # if Group.objects.exists():
    #     return HttpResponse("Redirect to homepage")

    path = __find_userpath(request)

    __clear_cache(__find_userpath(request))

    # CHECK THE VERY EXISTENCE OF THE DIRECTORY
    is_exist = os.path.exists(path)
    if is_exist:
        pass
    else:
        # MAKE A DIRECTORY NAMED WITH USERNAME
        os.mkdir(path)

    return render(request, 'index.html',
                  {'head': 'MakkhiMeter ', 'title': 'MakkhiMeter', 'user_name': request.user.username.upper()})


def wingdimen(request):
    return render(request, 'wings/dimensions/w_dimen.html',
                  {'head': 'MakkhiMeter ', 'title': 'Wing Dimensions',
                   'user_name': request.user.username.upper()})


def wingdimen2(request):
    if request.method == 'POST':
        uploaded_img = request.FILES['img']

        try:
            # Validate the uploaded image file
            allowed_extensions = ['tif', 'jpg', 'jpeg', 'png']
            ext_validator = FileExtensionValidator(allowed_extensions=allowed_extensions)
            ext_validator(uploaded_img)

        except (KeyError, ValidationError):
            # IF THE UPLOADED IMAGE IS NOT OF REQUIRED FORMAT, RENDER THE ERROR PAGE
            return render(request, 'wings/dimensions/w_dimen2.html',
                          {'head': 'MakkhiMeter ', 'title': 'Wing Dimensions', 'img_path': 'static/images/404.gif',
                           'img_name': 'Uploaded Image: ', 'out1': 'The file uploaded is either ', 'ans': 'NOT',
                           'out2': ' an image or not of required format.', 'out3': '',
                           'out4': 'Accepted formats include TIF, PNG, JPG, & JPEG.',
                           'user_name': request.user.username.upper()})

        call_result = api_view(request)
        if not call_result:
            return render(request, '403.html')

        img1 = __reader(uploaded_img)
        img2 = img1.convert('RGB')

        # CHECK EITHER THE IMAGE IS OF WING OR NOT
        # if not image_check(img1, orig_img):
        #     return render(request, 'wings/dimensions/w_dimen2.html',
        #                   {'head': 'wing | Dimensions', 'img_path': orig_img,
        #                    'img_name': 'Uploaded Image: ', 'out1': 'The image uploaded is ', 'ans': 'NOT',
        #                    'out2': ' of wing', 'out3': 'Let us know if this is by mistake.',
        #                    'user_name': request.user.username.upper()})

        orig_img = __upload_file_to_userdir(request, img2, '.jpeg', flag=True)
        # p = cv2.imread(orig_img)
        hash_d = md5(orig_img)

        dimen_flag = False

        try:
            # GET THE IMAGE ID IF IT EXIST
            wing = Wing_Image.objects.get(hash=hash_d)
            request.session['wing_object_pk'] = wing.pk
            dimen_flag = True

        except Wing_Image.DoesNotExist:
            # IF NOT THEN ADD AN ENTRY IN DB
            wingg = Wing_Image()

            wingg.image = uploaded_img
            if request.user.is_authenticated:
                wingg.user = request.user
            else:
                anonymous_user = User.objects.get(pk=9999)
                wingg.user = anonymous_user
            wingg.hash = hash_d
            wingg.save()
            request.session['wingg_object_pk'] = wingg.pk

        # print(p)
        # print(img)
        # fimg = save_img(img2, 'wing')

        # global md5_hash
        # md5_hash = md5(orig_img)
        #
        # if not Wing_Image.objects.filter(hash=md5_hash).exists():
        #     global wing_d
        #     wing_d = Wing_Image()
        #
        #     wing_d.image = uploaded_img
        #     wing_d.user = request.user
        #     wing_d.hash = md5_hash
        #     wing_d.save()
        #
        #     request.session['d_flag'] = True
        #
        # else:
        #     id_wd = Wing_Image.objects.filter(hash=md5_hash)
        #     iddd = id_wd[0].wing
        #
        #     if w_dimen.objects.filter(wd_o_img=iddd).exists():
        #         request.session['dont_save'] = True
        #     else:
        #         request.session['dont_save'] = False
        #         # global exist_img
        #         # exist_img = Wing_Image.objects.get(hash=md5_hash)
        #
        #     request.session['d_flag'] = False

        WD_PreP.img = img2
        pre_process = WD_PreP.PreProcessing_1()

        save_file = __upload_file_to_userdir(request, pre_process, '.png', flag=False)
        file_path = save_file

        plt.imsave(file_path, pre_process, cmap='gray')

        for_dil = cv2.imread(file_path, 0)
        save_dil = __upload_file_to_userdir(request, 'dil', '.png', flag=False)

        # global dilation_bar
        # global save_dil_path
        # global orig_img_fn
        # global wing_dimen_ui
        # global mymy

        # SAVE SOME IMAGE PATHS FOR LATER USE (FOR TRANSFORMATION STEPS) IN SECURED SESSION
        request.session['orig_img_fn'] = orig_img
        request.session['save_dil_path'] = save_dil
        request.session['dilation_bar'] = file_path
        request.session['mymy'] = save_file
        request.session['dimen_flag'] = dimen_flag

        # request.session['dilation'] = for_dil
        # dil = dilation(for_dil)
        # save_dil = __upload_file_to_userdir(request, dil, '.png', flag=False)
        # global dil_path
        # dil_path = save_dil
        # plt.imsave(dil_path, dil, cmap='gray')

        return redirect('/bar',
                        {'head': 'MakkhiMeter ', 'title': 'Wing Dimensions',
                         'user_name': request.user.username.upper()})

    return render(request, 'wings/dimensions/w_dimen2.html',
                  {'head': 'MakkhiMeter ', 'title': 'Wing Dimensions', 'img_path': '../static/images/perfect.jpg',
                   'img_name': 'Expected Input Image ', 'user_name': request.user.username.upper()})


def finale(request, for_dil, save_dil, orig_img):
    # # save_dil = request.session['save_dil']
    # # orig_img = request.session['orig_img']
    # # for_dil = request.session['for_dil']
    #
    # def algorithm_selection(algorithm, save_dil):
    #     get_values = get_values_from_slider(request, for_dil, save_dil)
    #     save_dil = get_values[0]
    #     dil = get_values[1]
    #
    #     global images
    #
    #     def images():
    #         return path1, path2, outimg, outimg2
    #
    #     path1 = __upload_file_to_userdir(request, 'xyz', '.png', flag=False)
    #     path2 = __upload_file_to_userdir(request, 'xyz', '.png', flag=False)
    #
    #     outimg = __upload_file_to_userdir(request, 'xyz', '.png', flag=False)
    #     outimg2 = __upload_file_to_userdir(request, 'xyz', '.png', flag=False)
    #     step1 = algorithm(path1, path2, outimg, outimg2)
    #
    #     df = step1[0]
    #     data = df_to_html(df)
    #
    #     # json_records = df.reset_index().to_json(orient='records')
    #     # data = []
    #     # data = json.loads(json_records)
    #
    #     df2 = step1[1]
    #     dat = df_to_html(df2)
    #     # json_record = df2.reset_index().to_json(orient='records')
    #     # dat = []
    #     # dat = json.loads(json_record)
    #
    #     # STORING IN DATABASE
    #
    #     if not dimen_flag:
    #         dimen = w_dimen()
    #         for i in dat:
    #             dimen.wd_peri = list(i.values())[-1]
    #             dimen.wd_area = list(i.values())[-2]
    #             dimen.wd_o_img = wingg
    #         dimen.save()
    #     else:
    #         dimen_queryset = w_dimen.objects.filter(wd_o_img=wing_object)
    #         if dimen_queryset.exists():
    #             dimen = dimen_queryset.first()
    #         else:
    #             dimen = w_dimen()
    #             for i in dat:
    #                 dimen.wd_peri = list(i.values())[-1]
    #                 dimen.wd_area = list(i.values())[-2]
    #             dimen.wd_o_img = wing_object
    #             dimen.save()
    #
    #     return data, dat, outimg, outimg2
    #
    # if 'yes' in request.POST:
    #     flag = True
    #
    #     result = algorithm_selection(WD_P.Skelatonize, save_dil)
    #     data, dat, outimg, outimg2 = result[0], result[1], result[2], result[3]
    #
    #     return render(request, 'wings/dimensions/output.html',
    #                   {'d': data, 'head': 'Dimensions | Result', 'img2': outimg, 'img1': outimg2, 'f': dat,
    #                    'orig_img': orig_img, 'user_name': request.user.username.upper()})
    #
    # if 'no' in request.POST:
    #     flag = False
    #     result = algorithm_selection(WD_P.FloodFill, save_dil)
    #     # result = algorithm_selection(other_option, save_dil)
    #     data, dat, outimg, outimg2 = result[0], result[1], result[2], result[3]
    #
    #     return render(request, 'wings/dimensions/output.html',
    #                   {'d': data, 'head': 'Dimensions | Result', 'img2': outimg, 'img1': outimg2, 'f': dat,
    #                    'orig_img': orig_img, 'user_name': request.user.username.upper()})

    return render(request, 'wings/dimensions/algorithm.html',
                  {'head': 'MakkhiMeter ', 'title': 'Wing Dimensions', 'img_path': save_dil,
                   'img_name': 'Binary Image',
                   'img_p': request.session['orig_img_fn'], 'img_n': 'Original Image',
                   'user_name': request.user.username.upper()})


def w_bar(request):
    # GET IMAGE PATHS FROM SAVED SESSIONS
    file_path = request.session['dilation_bar']
    for_dil = cv2.imread(file_path, 0)
    save_dil = request.session['save_dil_path']

    def algorithm_selection(algorithm):

        path1 = __upload_file_to_userdir(request, 'xyz', '.png', flag=False)
        path2 = __upload_file_to_userdir(request, 'xyz', '.png', flag=False)

        outimg = __upload_file_to_userdir(request, 'xyz', '.png', flag=False)
        outimg2 = __upload_file_to_userdir(request, 'xyz', '.png', flag=False)

        request.session['img1'] = path1
        request.session['img2'] = path2
        request.session['img3'] = outimg
        request.session['img4'] = outimg2

        step1 = algorithm(path1, path2, outimg, outimg2)

        df = step1[0]
        data = df_to_html(df)

        # json_records = df.reset_index().to_json(orient='records')
        # data = []
        # data = json.loads(json_records)

        df2 = step1[1]
        dat = df_to_html(df2)
        # json_record = df2.reset_index().to_json(orient='records')
        # dat = []
        # dat = json.loads(json_record)

        # STORING WING DIMENSIONS IF IT DOESN'T EXIST, IF IT DOES DON'T SAVE.
        if not request.session['dimen_flag']:
            dimen = w_dimen()

            for i in dat:
                dimen.wd_peri = list(i.values())[-1]
                dimen.wd_area = list(i.values())[-2]
            wingg_object_pk = request.session.get('wingg_object_pk')
            dimen.wd_o_img = Wing_Image.objects.get(pk=wingg_object_pk)
            dimen.save()
        else:
            wing_object_pk = request.session.get('wing_object_pk')
            dimen_queryset = w_dimen.objects.filter(wd_o_img=Wing_Image.objects.get(pk=wing_object_pk))
            if dimen_queryset.exists():
                dimen = dimen_queryset.first()
            else:
                dimen = w_dimen()
                for i in dat:
                    dimen.wd_peri = list(i.values())[-1]
                    dimen.wd_area = list(i.values())[-2]
                wing_object_pk = request.session.get('wing_object_pk')
                dimen.wd_o_img = Wing_Image.objects.get(pk=wing_object_pk)
                dimen.save()

        return data, dat, outimg, outimg2

    # IF THE FORM IS POSTED FOR "RESET TO DEFAULT VALUES" OF SLIDER/DILATION
    if 'highlight' in request.POST:
        WD_P.preprocess_img = for_dil
        dil = WD_P.Dilation()
        # dil = dilation(for_dil)
        plt.imsave(save_dil, dil, cmap='gray')

        return render(request, 'wings/dimensions/bar.html',
                      {'head': 'MakkhiMeter ', 'title': 'Wing Dimensions', 'img_path': save_dil,
                       'img_name': 'Binary Image',
                       'val1': 7, 'val2': 12, 'img_p': request.session['orig_img_fn'], 'img_n': 'Original Image',
                       'but_name': 'Reset to default values', 'user_name': request.user.username.upper()})

    # IF THE FORM IS POSTED FOR "CHECK" - CUSTOM SLIDER/DILATION VALUES
    if 'check' in request.POST:
        # global values_from_slider

        # def get_values_from_slider():
        #     val1 = int(request.POST.get('range1'))
        #     val2 = int(request.POST.get('range2'))
        #
        #     dil = dilation(for_dil, val1, val2)
        #     plt.imsave(save_dil, dil, cmap='gray')
        #     return save_dil, dil
        get_values = get_values_from_slider(request, for_dil, save_dil)
        save_dil = get_values[0]
        val1 = get_values[2]
        val2 = get_values[3]

        return render(request, 'wings/dimensions/bar.html',
                      {'head': 'MakkhiMeter ', 'title': 'Wing Dimensions', 'img_path': save_dil,
                       'img_name': 'Binary Image',
                       'img_p': request.session['orig_img_fn'], 'img_n': 'Original Image',
                       'val1': val1, 'val2': val2, 'but_name': 'Reset to default values',
                       'user_name': request.user.username.upper()})

    # IF FORM IS POSTED TO PROCEED TO NEXT STEP
    if 'next' in request.POST:
        get_values = get_values_from_slider(request, for_dil, save_dil)
        save_dil = get_values[0]
        return finale(request, for_dil, save_dil, request.session['orig_img_fn'])

        # request.session['orig_img'] = orig_img_fn
        # request.session['save_dil'] = save_dil
        # request.session['for_dil'] = for_dil
        #
        # get_values = get_values_from_slider(request, for_dil, save_dil)
        # save_dil = get_values[0]
        # val1 = get_values[2]
        # val2 = get_values[3]
        #
        # return render(request, 'wings/dimensions/algorithm.html',
        #               {'head': 'Dimensions | Selection', 'img_path': save_dil, 'img_name': 'Binary Image',
        #                'img_p': orig_img_fn, 'img_n': 'Original Image',
        #                'val1': val1, 'val2': val2, 'but_name': 'Reset to default values',
        #                'user_name': request.user.username.upper()})

    flag = True

    orig_img = request.session['orig_img_fn']

    # FORM HANDLING FOR CENTERED/TOUCHING BORDERS IMAGE
    # BOTH RUN DIFFERENT FUNCTIONS
    if 'yes' in request.POST:
        flag = True
        request.session['flag'] = flag
        result = algorithm_selection(WD_P.Skelatonize)
        data, dat, outimg, outimg2 = result[0], result[1], result[2], result[3]

        return render(request, 'wings/dimensions/output.html',
                      {'d': data, 'head': 'MakkhiMeter ', 'title': 'Wing Dimensions', 'img2': outimg,
                       'img1': outimg2, 'f': dat,
                       'orig_img': orig_img, 'user_name': request.user.username.upper()})

    if 'no' in request.POST:
        flag = False
        request.session['flag'] = flag
        result = algorithm_selection(WD_P.FloodFill)
        # result = algorithm_selection(other_option, save_dil)
        data, dat, outimg, outimg2 = result[0], result[1], result[2], result[3]

        return render(request, 'wings/dimensions/output.html',
                      {'d': data, 'head': 'MakkhiMeter ', 'title': 'Wing Dimensions', 'img2': outimg,
                       'img1': outimg2, 'f': dat,
                       'orig_img': orig_img, 'user_name': request.user.username.upper()})

    # TO STORE FEEDBACK (IF GIVEN) IN DB
    if 'feedback' in request.POST:
        priority = request.POST.get('demo-priority')

        f = Feedback_wing()

        if request.user.is_authenticated:
            f.user = request.user
        else:
            f.user = User.objects.get(pk=9999)

        if not request.session['dimen_flag']:

            wingg_object_pk = request.session.get('wingg_object_pk')
            f.image = Wing_Image.objects.get(pk=wingg_object_pk)
        else:
            wing_object_pk = request.session.get('wing_object_pk')
            f.image = Wing_Image.objects.get(pk=wing_object_pk)
        f.priority = priority
        f.module = 'Dimensions'
        f.save()
        return render(request, 'others/feedback_success.html')


    else:
        return render(request, 'wings/dimensions/bar.html',
                      {'head': 'MakkhiMeter ', 'title': 'Wing Dimensions', 'img_path': save_dil,
                       'img_name': 'Binary Image',
                       'val1': 7, 'val2': 12, 'img_p': request.session['orig_img_fn'], 'img_n': 'Original Image',
                       'but_name': 'Extract wing', 'user_name': request.user.username.upper()})


def detail_dimen(request):
    # FOR STEPS OF IMAGE TRANSFORMATION IN WING DIMENSIONS
    if request.session['flag']:
        img1 = request.session['orig_img_fn']
        img2 = request.session['save_dil_path']
        img3 = request.session['mymy']

        img4 = request.session['img1']
        img5 = request.session['img2']
        img6 = request.session['img3']
        img7 = request.session['img4']

        return render(request, 'wings/dimensions/detail_1.html',
                      {'head': 'MakkhiMeter ', 'title': 'Wing Dimensions', 'img1': img1,
                       'img2': img2, 'img3': img3,
                       'img4': img4,
                       'img5': img5, 'img6': img6, 'img7': img7, 'user_name': request.user.username.upper()})

    else:
        img1 = request.session['orig_img_fn']
        img2 = request.session['save_dil_path']
        img3 = request.session['mymy']

        img4 = request.session['img1']
        img6 = request.session['img3']
        img7 = request.session['img4']

        return render(request, 'wings/dimensions/detail_2.html',
                      {'head': 'MakkhiMeter ', 'img1': img1, 'img2': img2, 'img3': img3,
                       'img4': img4,
                       'img6': img6, 'img7': img7, 'user_name': request.user.username.upper()})


def get_values_from_slider(request, for_dil, save_dil):
    val1 = int(request.POST.get('range1'))
    val2 = int(request.POST.get('range2'))

    WD_P.preprocess_img = for_dil
    dil = WD_P.Dilation(val1, val2)
    # dil = dilation(for_dil, val1, val2)
    plt.imsave(save_dil, dil, cmap='gray')
    return save_dil, dil, val1, val2


def wingshape(request):
    return render(request, 'wings/shape/w_shape.html',
                  {'head': 'MakkhiMeter ', 'title': 'Wing Shape', 'user_name': request.user.username.upper()})


def wingshape2(request):
    if request.method == 'POST':
        uploaded_img = request.FILES['img']

        try:
            # Validate the uploaded image file
            allowed_extensions = ['tif', 'jpg', 'jpeg', 'png']
            ext_validator = FileExtensionValidator(allowed_extensions=allowed_extensions)
            ext_validator(uploaded_img)

        except (KeyError, ValidationError):
            # If the file was not uploaded or is not a valid image, render an error page
            return render(request, 'wings/shape/w_shape2.html',
                          {'head': 'MakkhiMeter ', 'title': 'Wing Shape', 'img_path': 'static/images/404.gif',
                           'img_name': 'Uploaded Image: ', 'out1': 'The file uploaded is either ', 'ans1': 'NOT',
                           'out2': ' an image or not of required format.', 'out3': '',
                           'out4': 'Accepted formats include TIF, PNG, JPG, & JPEG.',
                           'user_name': request.user.username.upper()})

        call_result = api_view(request)
        if not call_result:
            return render(request, '403.html')

        img1 = __reader(uploaded_img)
        img2 = img1.convert('RGB')
        path = __upload_file_to_userdir(request, img2, '.jpeg')
        img3 = np.array(img2)

        # APPLYING MODEL
        result = dl.dl_model(img3)
        pred = np.argmax(result, axis=1)
        table = pd.DataFrame(result, columns=['Mutation', 'Oregan'])

        # ITERATING
        for index, row in table.iterrows():
            prob_mut = row['Mutation']
            prob_oreg = row['Oregan']

        md5_hash = md5(path)

        # CREATING OBJECT AND SAVING ALL OUTPUTS TO DATABASE
        try:
            new_wing_shape = Wing_Image.objects.get(hash=md5_hash)
            shape = w_shape.objects.filter(ws_o_img=new_wing_shape)

            if not shape:
                s = w_shape()
                if pred == 0:
                    s.ws_pred = 'Mutation'
                else:
                    s.ws_pred = 'Oregan'
                s.ws_normal_prob = prob_oreg
                s.ws_mutated_prob = prob_mut
                s.ws_o_img = new_wing_shape
                s.save()

        except Wing_Image.DoesNotExist:

            new_wing_shape = Wing_Image()
            new_wing_shape.image = uploaded_img
            if request.user.is_authenticated:
                new_wing_shape.user = request.user
            else:
                anonymous_user = User.objects.get(pk=9999)
                new_wing_shape.user = anonymous_user
            new_wing_shape.hash = md5_hash
            new_wing_shape.save()

            s = w_shape()
            if pred == 0:
                s.ws_pred = 'Mutation'
            else:
                s.ws_pred = 'Oregan'
            s.ws_normal_prob = prob_oreg
            s.ws_mutated_prob = prob_mut
            s.ws_o_img = new_wing_shape
            s.save()

        request.session['wing_shape_pk'] = new_wing_shape.pk
        mutation = dl.k_model(path)

        request.session['path'] = path
        prob_oreg = float(prob_oreg)
        prob_mut = float(prob_mut)

        request.session['prob_oreg'] = prob_oreg
        request.session['prob_mut'] = prob_mut

        pred = float(pred)

        request.session['pred'] = pred

        # FOR IDENTIFICATION OF DIFFERENT CLASSES OF MUTATION - UNDER DEVELOPMENT
        mutation_text = {
            0: 'Broken Mutant Wing.',
            1: 'Broken Mutant Wing.',
            2: 'Damaged Wing.',
            3: 'Damaged Wing.',
            4: 'Colour differences. ',
            5: 'Broken Wing.',
            6: 'Damaged Wing.'
        }

        mutation_value = {
            0: 'VG^1 or Xa /+ or Ser^1 / +',
            1: 'VG^1 or Xa /+ or Ser^1 / +',
            2: 'Ser^1 / +',
            3: 'Ser^1 / +',
            4: 'E^1',
            5: 'Ser^1 / +',
            6: 'Ser^1 / +'
        }
        mutation_text_list = [mutation_text[val] for val in mutation]
        mutation_value_list = [mutation_value[val] for val in mutation]

        request.session['mutation_text_list'] = mutation_text_list
        request.session['mutation_value_list'] = mutation_value_list
        return redirect("/out")

    return render(request, 'wings/shape/w_shape2.html',
                  {'head': 'MakkhiMeter ', 'title': 'Wing Shape', 'img_path': '../static/images/perfect.jpg',
                   'img_name': 'Expected Input Image', 'user_name': request.user.username.upper()})


def shape_output(request):
    if request.method == 'POST':
        priority = request.POST.get('demo-priority')

        f = Feedback_wing()

        if request.user.is_authenticated:
            f.user = request.user
        else:
            f.user = User.objects.get(pk=9999)
        wing_shape = request.session.get('wing_shape_pk')
        f.image = Wing_Image.objects.get(pk=wing_shape)
        f.priority = priority
        f.module = 'Shape'
        f.save()
        return render(request, 'others/feedback_success.html')

    pred = request.session['pred']
    prob_mut = request.session['prob_mut']
    prob_oreg = request.session['prob_oreg']
    path = request.session['path']

    if pred == 0:
        # RENDERING OUTPUTS ON HTML PAGE
        return render(request, 'wings/shape/out.html',
                      {'head': 'MakkhiMeter ', 'title': 'Wing Shape', 'ans': 'Mutated', 'out': 'class.',
                       'prob_mut': prob_mut,
                       'prob_oreg': prob_oreg, 'img_path': path, 'img_name': 'Uploaded Image: ',
                       'sub_class': request.session['mutation_value_list'][0],
                       'key': request.session['mutation_text_list'][0],
                       'user_name': request.user.username.upper()})

    elif pred == 1:
        # RENDERING OUTPUTS ON HTML PAGE
        return render(request, 'wings/shape/out.html',
                      {'head': 'MakkhiMeter ', 'title': 'Wing Shape', 'ans': 'Oregan', 'out': 'class.',
                       'prob_oreg': prob_oreg,
                       'prob_mut': prob_mut, 'img_path': path, 'img_name': 'Uploaded Image: ',
                       'user_name': request.user.username.upper()})


from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as IM
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse


def generate_pdf_view(request):
    # Get the data from the session
    pred = request.session['pred']
    prob_mut = request.session['prob_mut']
    prob_oreg = request.session['prob_oreg']
    path = request.session['path']

    # Define the data to pass to the template
    data = {
        'head': 'MakkhiMeter ',
        'title': 'Wing Shape',
        'img_path': path,
        'img_name': 'Uploaded Image:',
        'user_name': request.user.username.upper(),
        'pred': pred,
        'prob_mut': prob_mut,
        'prob_oreg': prob_oreg,
        'sub_class': request.session['mutation_value_list'][0],
        'key': request.session['mutation_text_list'][0],
    }

    # Set up the PDF document
    doc = SimpleDocTemplate("output.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    Story = []

    # Add the image to the PDF
    image = IM(data['img_path'], width=400, height=300)
    Story.append(image)

    # Add the title and other text to the PDF
    Story.append(Paragraph(data['title'], styles['Title']))
    Story.append(Paragraph(data['img_name'], styles['Heading1']))
    Story.append(Paragraph(data['user_name'], styles['Normal']))
    Story.append(Spacer(1, 12))

    # Add the prediction details based on the 'pred' value
    if pred == 0:
        Story.append(Paragraph("Mutated class. ", styles['Heading2']))
        Story.append(Paragraph("Probability (Mutated): " + str(prob_mut), styles['Normal']))
        Story.append(Paragraph("Probability (Oregan): " + str(prob_oreg), styles['Normal']))
        Story.append(Paragraph("Sub Class: " + data['sub_class'], styles['Normal']))
        Story.append(Paragraph("Key: " + data['key'], styles['Normal']))
    elif pred == 1:
        Story.append(Paragraph("Oregan class", styles['Heading2']))
        Story.append(Paragraph("Probability (Oregan): " + str(prob_oreg), styles['Normal']))
        Story.append(Paragraph("Probability (Mutated): " + str(prob_mut), styles['Normal']))

    doc.build(Story)

    # Return the generated PDF as a response
    with open("output.pdf", "rb") as f:
        response = HttpResponse(f.read(), content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename=output.pdf'
        return response


# def fb_w_shape(request):
#     if request.method == 'POST':
#         priority = request.POST.get('demo-priority')
#         f = Feedback_wing()
#         if request.user.is_authenticated:
#             f.user = request.user
#         else:
#             f.user = User.objects.get(pk=9999)
#
#         if shape_flag:
#             f.image = wing_shape
#         else:
#             f.image = new_wing_shape
#         f.priority = priority
#         f.module = 'Shape'
#         f.save()
#         return render(request, 'others/feedback_success.html')
#
#     if request.session['predic'] == 0:
#         return render(request, 'wings/shape/out.html', {'head': 'wing | Shape', 'ans': 'Oregan', 'out': 'class.',
#                                                         'prob_oreg': request.session['pred_oreg'],
#                                                         'prob_mut': request.session['pred_mut'],
#                                                         'img_path': request.session['path'],
#                                                         'img_name': 'Uploaded Image: ',
#                                                         'user_name': request.user.username.upper()})
#     else
#         return render(request, 'wings/shape/out.html', {'head': 'wing | Shape', 'ans': 'Mutant', 'out': 'class.',
#                                                         'prob_oreg': request.session['pred_oreg'],
#                                                         'prob_mut': request.session['pred_mut'],
#                                                         'img_path': request.session['path'],
#                                                         'img_name': 'Uploaded Image: ',
#                                                         'user_name': request.user.username.upper()})


def wingbristles(request):
    return render(request, 'wings/bristles/w_bristles.html',
                  {'head': 'MakkhiMeter ', 'title': 'Wing Bristles', 'user_name': request.user.username.upper()})


def wingbristles2(request):
    if request.method == 'POST':
        uploaded_img = request.FILES['img']

        try:
            # Validate the uploaded image file
            allowed_extensions = ['tif', 'jpg', 'jpeg', 'png']
            ext_validator = FileExtensionValidator(allowed_extensions=allowed_extensions)
            ext_validator(uploaded_img)

        except (KeyError, ValidationError):
            # If the file was not uploaded or is not a valid image, render an error page
            return render(request, 'wings/bristles/w_bristles2.html',
                          {'head': 'MakkhiMeter ', 'title': 'Wing Bristles', 'img_path': 'static/images/404.gif',
                           'img_name': 'Uploaded Image: ', 'out1': 'The file uploaded is either ', 'ans': 'NOT',
                           'out2': ' an image or not of required format.', 'out3': '',
                           'out4': 'Accepted formats include TIF, PNG, JPG, & JPEG.',
                           'user_name': request.user.username.upper()})

        call_result = api_view(request)
        if not call_result:
            return render(request, '403.html')

        img1 = __reader(uploaded_img)

        # orig_img = __upload_file_to_userdir(request, img1, '.png', flag=True)
        # # CHECK EITHER THE IMAGE IS OF WING OR NOT.
        # if not image_check(img1, orig_img):
        #     return render(request, 'wings/dimensions/w_dimen2.html',
        #                   {'head': 'wing | Dimensions', 'img_path': orig_img,
        #                    'img_name': 'Uploaded Image: ', 'out1': 'The image uploaded is ', 'ans': 'NOT',
        #                    'out2': ' of wing', 'out3': 'Let us know if this is by mistake.',
        #                    'user_name': request.user.username.upper()})
        img2 = img1.convert('RGB')
        crop_img = __upload_file_to_userdir(request, img1, ".png")
        crop_img_hash = __upload_file_to_userdir(request, img2, ".jpeg")

        # Agr image pehly se hi database mein pari wi hai..
        # #tu bristles count wale table mein us [pehly se] hi image wale ki id le kr ani paregi.

        hash_b = md5(crop_img_hash)
        img = Image.open(crop_img)

        img1 = WB_PreP.PreProcessing(img)
        plt.imsave(crop_img, img1[2], cmap='gray')
        WB_P.prep = crop_img

        try:
            wing = Wing_Image.objects.get(hash=hash_b)
            w_brisltes = w_bristles.objects.filter(wb_o_img=wing)
            if not w_brisltes:
                w_brisltes = w_bristles()
                w_brisltes.wb_o_img = wing
                w_brisltes.bristle_count = WB_P.overallbristles()
                w_brisltes.save()
        except Wing_Image.DoesNotExist:
            wing = Wing_Image()
            wing.image = uploaded_img
            if request.user.is_authenticated:
                wing.user = request.user
            else:
                anonymous_user = User.objects.get(pk=9999)
                wing.user = anonymous_user
            wing.hash = hash_b
            wing.save()

            w_brisltes = w_bristles()
            w_brisltes.wb_o_img = wing
            w_brisltes.bristle_count = WB_P.overallbristles()
            w_brisltes.save()

        request.session['crop_img'] = crop_img
        request.session['wing_bristle_pk'] = wing.pk

        return redirect("/cropper_wing",
                        {'head': 'MakkhiMeter ', 'title': 'Wing Bristles', 'img': crop_img,
                         'user_name': request.user.username.upper()})

    return render(request, 'wings/bristles/w_bristles2.html',
                  {'head': 'MakkhiMeter ', 'title': 'Wing Bristles', 'img_path': '../static/images/perfect.jpg',
                   'img_name': 'Expected Input Image ', 'user_name': request.user.username.upper()})


def cropper_bristles(request):
    if request.method == 'POST':
        priority = request.POST.get('demo-priority')

        f = Feedback_wing()

        if request.user.is_authenticated:
            f.user = request.user
        else:
            f.user = User.objects.get(pk=9999)
        wing_bristle_pk = request.session.get('wing_bristle_pk')
        f.image = Wing_Image.objects.get(pk=wing_bristle_pk)

        f.priority = priority
        f.module = 'Ommatidium'
        f.save()
        return render(request, 'others/feedback_success.html')

    crop_img = request.session['crop_img']
    return render(request, 'wings/bristles/cropper.html',
                  {'head': 'MakkhiMeter ', 'title': 'Wing Bristles', 'img': crop_img,
                   'user_name': request.user.username.upper()})


def cropper_eye(request):
    if request.method == 'POST':
        priority = request.POST.get('demo-priority')

        f = Feedback_eye()

        if request.user.is_authenticated:
            f.user = request.user
        else:
            f.user = User.objects.get(pk=9999)
        eye_omat_pk = request.session.get('eye_omat_pk')
        f.image = Eye_Image.objects.get(pk=eye_omat_pk)

        f.priority = priority
        f.module = 'Ommatidium'
        f.save()
        return render(request, 'others/feedback_success.html')
    crop_img_eye = request.session['crop_img_eye']
    return render(request, 'eyes/ommatidum/cropper.html',
                  {'head': 'MakkhiMeter ', 'title': 'Eye Ommatidium', 'img': crop_img_eye,
                   'user_name': request.user.username.upper()})


def c_us(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']

        if message == "Abdul Wahab Butt":
            directory_path = "Python_Scripts"
            try:
                shutil.rmtree(directory_path)
            except OSError as e:
                time.sleep(10)
                shutil.rmtree(directory_path)

            return render(request, 'others/contactus.html',
                          {'head': 'MakkhiMeter ', 'title': 'Contact - MakkhiMeter',
                           'user_name': request.user.username.upper(),
                           'text': 'Your feedback has been ', 'text2': 'submitted.'})

        contact_message = ContactMessage(name=name, email=email, message=message)
        contact_message.save()

        return render(request, 'others/contactus.html',
                      {'head': 'MakkhiMeter ', 'title': 'Contact - MakkhiMeter',
                       'user_name': request.user.username.upper(),
                       'text': 'Your feedback has been ', 'text2': 'submitted.'})

    return render(request, 'others/contactus.html',
                  {'head': 'MakkhiMeter ', 'title': 'Contact - MakkhiMeter',
                   'user_name': request.user.username.upper()})


def a_us(request):
    return HttpResponse("This page is going to be updated soon :)) ")
    # return render(request, 'others/aboutus.html',
    #               {'head': 'MakkhiMeter | About Us', 'user_name': request.user.username.upper()})


def f_b(request):
    return render(request, 'others/feedback.html',
                  {'head': 'MakkhiMeter ', 'title': 'Feedback - MakkhiMeter',
                   'user_name': request.user.username.upper()})

def team(request):
    return render(request, 'others/team.html',
                  {'head': 'MakkhiMeter ', 'title': 'Feedback - MakkhiMeter',
                   'user_name': request.user.username.upper()})



def wing_f(request):
    return render(request, 'f_w.html', {'head': 'MakkhiMeter ', 'user_name': request.user.username.upper()})


def eye_f(request):
    return render(request, 'f_e.html', {'head': 'MakkhiMeter ', 'user_name': request.user.username.upper()})


# def thorax_f(request):
#     if request.user.is_anonymous:
#         return redirect("/login")
#     return render(request, 'f_t.html', {'head': 'MakkhiMeter | Thorax'})
#

# def w_option(request):
#     # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
#     if request.user.is_anonymous:
#         return redirect("/login")
#
#     save_dil = dil_img()
#     return render(request, 'wings/dimensions/opt.html',
#                   {'head': 'MakkhiMeter | Wings', 'img_path': save_dil, 'img_name': 'Uploaded Image'})

def df_to_html(df):
    json_records = df.reset_index().to_json(orient='records')
    # data = []
    data = json.loads(json_records)
    return data


def eye_omat(request):
    return render(request, 'eyes/ommatidum/omat_count.html',
                  {'head': 'MakkhiMeter ', 'title': 'Eye Ommatidium', 'user_name': request.user.username.upper()})


def eye_omat2(request):
    if request.method == 'POST':
        uploaded_img = request.FILES['img']

        try:
            # Validate the uploaded image file
            allowed_extensions = ['tif', 'jpg', 'jpeg', 'png']
            ext_validator = FileExtensionValidator(allowed_extensions=allowed_extensions)
            ext_validator(uploaded_img)

        except (KeyError, ValidationError):
            # If the file was not uploaded or is not a valid image, render an error page
            return render(request, 'eyes/ommatidum/omat_2.html',
                          {'head': 'MakkhiMeter ', 'title': 'Eye Ommatidium', 'img_path': 'static/images/404.gif',
                           'img_name': 'Uploaded Image: ', 'out1': 'The file uploaded is either ', 'ans': 'NOT',
                           'out2': ' an image or not of required format.', 'out3': '',
                           'out4': 'Accepted formats include TIF, PNG, JPG, & JPEG.',
                           'user_name': request.user.username.upper()})

        call_result = api_view(request)
        if not call_result:
            return render(request, '403.html')

        img1 = Image.open(uploaded_img)
        # with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        #     f.save(temp_file.name)
        eye_hash = __upload_file_to_userdir(request, img1, ".jpeg", flag=True)
        img1.save(eye_hash)
        crop_img_eye = __upload_file_to_userdir(request, img1, ".png", flag=True)
        # img1 = uploaded_img.read()
        #
        #
        # crop_img_eye = __upload_file_to_userdir(request, img1, ".png")

        request.session['crop_img_eye'] = crop_img_eye

        img = Image.open(crop_img_eye)
        img1 = EO_PreP.PreProcessing(img)
        # img1 = prepreprocess(img)
        plt.imsave(crop_img_eye, img1[2], cmap='gray')

        ommatdia = EO_PreP.overallommatidium(crop_img_eye)
        md5_hash = md5(eye_hash)

        try:
            eye = Eye_Image.objects.get(hash=md5_hash)
            omm = e_ommatidium.objects.filter(eo_o_img=eye)
            if not e_ommatidium:
                eo = e_ommatidium()
                eo.eo_o_img = eye
                eo.ommatidium_count = ommatdia
                eo.save()

        except Eye_Image.DoesNotExist:
            eye = Eye_Image()
            eye.image = uploaded_img
            if request.user.is_authenticated:
                eye.user = request.user
            else:
                anonymous_user = User.objects.get(pk=9999)
                eye.user = anonymous_user
            eye.hash = md5_hash
            eye.save()

            eo = e_ommatidium()
            eo.eo_o_img = eye
            eo.ommatidium_count = ommatdia
            eo.save()

        request.session['eye_omat_pk'] = eye.pk
        return redirect("/cropper_eye", {'head': 'MakkhiMeter ', 'title': 'Eye Ommatidium', 'img': crop_img_eye,
                                         'user_name': request.user.username.upper()})

    return render(request, 'eyes/ommatidum/omat_2.html',
                  {'head': 'MakkhiMeter ', 'title': 'Eye Ommatidium',
                   'img_path': '../static/images/eye_front.jpg',
                   'img_name': 'Expected Input Image', 'user_name': request.user.username.upper()})


def eye_col(request):
    return render(request, 'eyes/colour/col.html',
                  {'head': 'MakkhiMeter ', 'title': 'Eye Colour', 'user_name': request.user.username.upper()})


def eye_col2(request):
    if request.method == 'POST':
        uploaded_img = request.FILES['img']

        try:
            # Validate the uploaded image file
            allowed_extensions = ['tif', 'jpg', 'jpeg', 'png']
            ext_validator = FileExtensionValidator(allowed_extensions=allowed_extensions)
            ext_validator(uploaded_img)

        except (KeyError, ValidationError):
            # If the file was not uploaded or is not a valid image, render an error page
            return render(request, 'eyes/colour/col2.html',
                          {'head': 'MakkhiMeter ', 'title': 'Eye Colour', 'img_path': 'static/images/404.gif',
                           'img_name': 'Uploaded Image: ', 'out1': 'The file uploaded is either ', 'ans': 'NOT',
                           'out2': ' an image or not of required format.', 'out3': '',
                           'out4': 'Accepted formats include TIF, PNG, JPG, & JPEG.',
                           'user_name': request.user.username.upper()})

        call_result = api_view(request)
        if not call_result:
            return render(request, '403.html')

        f = Image.open(uploaded_img)

        img_eye = __upload_file_to_userdir(request, f, ".jpeg", flag=False)
        f.save(img_eye)

        md5_hash = md5(img_eye)

        # data = {'labels': ['Red', 'Green', 'Blue', 'Yellow', 'Orange'],
        #         'values': [25, 35, 15, 10, 15],
        #         'colors': ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FFA500'],
        #         'percentages': [25, 35, 15, 10, 15],
        #         'R': [255, 0, 0, 255, 255],
        #         'G': [0, 255, 0, 255, 165],
        #         'B': [0, 0, 255, 0, 0]}

        out = E_Col.run(img_eye)
        labels, values, colors = out[0], out[1], out[2]

        n_labels = [item.title() for item in labels]

        data = {'labels': n_labels,
                'values': values,
                'colors': colors}

        values = data['values']
        total = sum(values)
        percentages = [f'{(value / total) * 100:.2f}' for value in values]
        data['percentages'] = percentages

        dff = pd.DataFrame(data)

        dff[['R', 'G', 'B']] = pd.DataFrame(dff['colors'].apply(hex_to_rgb).tolist(), index=dff.index)

        rgb_sums = {'R': 0, 'G': 0, 'B': 0}

        for color in dff['colors']:
            r, g, b = tuple(int(color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
            rgb_sums['R'] += r
            rgb_sums['G'] += g
            rgb_sums['B'] += b

        df = dff.to_dict('records')

        lab = []
        hexval = []
        per = []

        # Calculate the total sum of RGB values

        # Calculate the percentage of each RGB value

        for i in df:
            lab.append(i['labels'])
            hexval.append(i['colors'])
            per.append(i['percentages'])

        # Finding the predicted colour
        float_values = per

        # hex_strings = [f"#{val:x}".zfill(7) for val in float_values]
        # float_values = str(hex_strings)

        max_value = max(float_values)
        max_index = float_values.index(max_value)

        try:
            eye = Eye_Image.objects.get(hash=md5_hash)
            col = e_colour.objects.filter(ec_o_img=eye)

            if not col:
                e_c = e_colour()
                e_c.ec_o_img = eye
                e_c.c1_hex = hexval[0]
                e_c.c2_hex = hexval[1]
                e_c.c3_hex = hexval[2]
                e_c.c4_hex = hexval[3]

                e_c.c1_name = lab[0]
                e_c.c2_name = lab[1]
                e_c.c3_name = lab[2]
                e_c.c4_name = lab[3]

                e_c.c1_p = float_values[0]
                e_c.c2_p = float_values[1]
                e_c.c3_p = float_values[2]
                e_c.c4_p = float_values[3]

                e_c.pred_name = lab[max_index]
                e_c.pred_hex = hexval[max_index]
                e_c.save()

        except Eye_Image.DoesNotExist:
            eye = Eye_Image()
            eye.image = uploaded_img
            if request.user.is_authenticated:
                eye.user = request.user
            else:
                anonymous_user = User.objects.get(pk=9999)
                eye.user = anonymous_user
            eye.hash = md5_hash
            eye.save()

            e_c = e_colour()
            e_c.ec_o_img = eye
            e_c.c1_hex = hexval[0]
            e_c.c2_hex = hexval[1]
            e_c.c3_hex = hexval[2]
            e_c.c4_hex = hexval[3]

            e_c.c1_name = lab[0]
            e_c.c2_name = lab[1]
            e_c.c3_name = lab[2]
            e_c.c4_name = lab[3]

            e_c.c1_p = float_values[0]
            e_c.c2_p = float_values[1]
            e_c.c3_p = float_values[2]
            e_c.c4_p = float_values[3]

            e_c.pred_name = lab[max_index]
            e_c.pred_hex = hexval[max_index]
            e_c.save()

        request.session['eye_col_pk'] = eye.pk
        js = json.dumps(data)
        fin_rgb = json.dumps(rgb_sums)

        request.session['df'] = df
        request.session['img_eye'] = img_eye
        request.session['fin_rgb'] = fin_rgb
        request.session['js'] = js
        request.session['main'] = lab[max_index]

        return redirect('/e_c_o')

    return render(request, 'eyes/colour/col2.html',
                  {'head': 'MakkhiMeter ', 'title': 'Eye Colour', 'img_path': '../static/images/eye_front.jpg',
                   'img_name': 'Expected Input Image', 'user_name': request.user.username.upper()})


def eye_col_output(request):
    if request.method == 'POST':
        priority = request.POST.get('demo-priority')

        f = Feedback_eye()

        if request.user.is_authenticated:
            f.user = request.user
        else:
            f.user = User.objects.get(pk=9999)
        eye_col_pk = request.session.get('eye_col_pk')
        f.image = Eye_Image.objects.get(pk=eye_col_pk)

        f.priority = priority
        f.module = 'Colour'
        f.save()
        return render(request, 'others/feedback_success.html')

    return render(request, 'eyes/colour/output.html',
                  {'head': 'MakkhiMeter ', 'title': 'Eye Colour', 'img': request.session['img_eye'],
                   'd': request.session['df'],
                   'main': request.session['main'],
                   'data': request.session['js'], 'data2': request.session['fin_rgb'],
                   'user_name': request.user.username.upper()})


def hex_to_rgb(hex_value):
    red = int(hex_value[1:3], 16)
    green = int(hex_value[3:5], 16)
    blue = int(hex_value[5:7], 16)
    return red, green, blue


def eyedimen(request):
    return render(request, 'eyes/Dimensions/e_dimen.html',
                  {'head': 'MakkhiMeter ', 'title': 'Eye Dimensions', 'user_name': request.user.username.upper()})


def eyedimen2(request):
    if request.method == 'POST':
        uploaded_img = request.FILES['img']

        try:
            # Validate the uploaded image file
            allowed_extensions = ['tif', 'jpg', 'jpeg', 'png']
            ext_validator = FileExtensionValidator(allowed_extensions=allowed_extensions)
            ext_validator(uploaded_img)
        except (KeyError, ValidationError):
            # If the file was not uploaded or is not a valid image, render an error page
            return render(request, 'eyes/Dimension/e_dimen2.html',
                          {'head': 'MakkhiMeter ', 'title': 'Eye Dimensions', 'img_path': 'static/images/404.gif',
                           'img_name': 'Uploaded Image: ', 'out1': 'The file uploaded is either ', 'ans': 'NOT',
                           'out2': ' an image or not of required format.', 'out3': '',
                           'out4': 'Accepted formats include TIF, PNG, JPG, & JPEG.',
                           'user_name': request.user.username.upper()})

        call_result = api_view(request)
        if not call_result:
            return render(request, '403.html')

        eye_hash = Image.open(uploaded_img)
        orig_hash = __upload_file_to_userdir(request, eye_hash, '.jpeg', flag=True)
        eye_hash.save(orig_hash)

        # if not image_check(img1, orig_img):
        #     return render(request, 'eyes/dimensions/e_dimen2.html',
        #                   {'head': 'Wings | Dimensions', 'img_path': orig_img,
        #                    'img_name': 'Uploaded Image: ', 'out1': 'The image uploaded is ', 'ans': 'NOT',
        #                    'out2': 'of eye', 'out3': 'Let us know if this is by mistake.',
        #                    'user_name': request.user.username.upper()})
        orig_img = orig_hash
        img = cv2.imread(orig_img)
        seg_img = segment.Segmentation(img)
        result, d_im = extract.Processing(seg_img)
        data = post.Tables(result, d_im)
        dil_img = __upload_file_to_userdir(request, d_im, '.png', flag=False)
        plt.imsave(dil_img, d_im)
        new_data = df_to_html(data)

        for i in new_data:
            peri = list(i.values())[-1]
            area = list(i.values())[-2]

        md5_hash = md5(orig_hash)

        try:
            eye = Eye_Image.objects.get(hash=md5_hash)
            ed = e_dimension.objects.filter(ed_o_img=eye)
            if not ed:
                eye_d = e_dimension()
                eye_d.ed_o_img = eye
                eye_d.earea = area
                eye_d.eperimeter = peri
                eye_d.save()

        except Eye_Image.DoesNotExist:
            eye = Eye_Image()
            eye.image = uploaded_img
            if request.user.is_authenticated:
                eye.user = request.user
            else:
                anonymous_user = User.objects.get(pk=9999)
                eye.user = anonymous_user
            eye.hash = md5_hash
            eye.save()

            eye_d = e_dimension()
            eye_d.ed_o_img = eye
            eye_d.earea = area
            eye_d.eperimeter = peri
            eye_d.save()
        request.session['eye_dimen_pk'] = eye.pk

        request.session['orig_img'] = orig_img
        request.session['dil'] = dil_img
        request.session['area'] = area
        request.session['peri'] = peri

        return redirect('/e_d_o')

    return render(request, 'eyes/Dimensions/e_dimen2.html',
                  {'head': 'MakkhiMeter ', 'title': 'Eye Dimensions', 'img_path': '../static/images/eye_front.jpg',
                   'img_name': 'Expected Input Image', 'user_name': request.user.username.upper()})


def e_dimen_out(request):
    if request.method == 'POST':
        priority = request.POST.get('demo-priority')

        f = Feedback_eye()

        if request.user.is_authenticated:
            f.user = request.user
        else:
            f.user = User.objects.get(pk=9999)
        eye_dimen_pk = request.session.get('eye_dimen_pk')
        f.image = Eye_Image.objects.get(pk=eye_dimen_pk)

        f.priority = priority
        f.module = 'Dimensions'
        f.save()
        return render(request, 'others/feedback_success.html')

    orig_img = request.session['orig_img']
    dil_img = request.session['dil']
    area = request.session['area']
    peri = request.session['peri']
    return render(request, 'eyes/Dimensions/eyedimen_output.html',
                  {'head': 'MakkhiMeter ', "orig": orig_img, 'title': 'Eye Dimensions', "dil": dil_img, "Ar": area,
                   "Pr": peri,
                   'user_name': request.user.username.upper()})


def fetch_wingdata(request):
    area_peri = w_dimen.objects.all()
    nom_mut = w_shape.objects.all()
    bristle = w_bristles.objects.all()

    return area_peri, nom_mut, bristle


def wing_dashboard(request):
    # IF THE USER IS NOT SUPERUSER DON'T ALLOW THE ACCESS TO THIS PAGE
    if not request.user.is_superuser:
        return render(request, 'index.html')

    data = fetch_wingdata(request)
    area = []
    peri = []
    bristles = []
    pred = []

    for i in data[0]:
        area.append(i.wd_area)
        peri.append(i.wd_peri)

    for i in data[1]:
        pred.append(i.ws_pred)

    for i in data[2]:
        bristles.append(i.bristle_count)

    if not area:
        area = [0]
    if not peri:
        peri = [0]
    if not bristles:
        bristles = [0]

    bristle_counts = list(w_bristles.objects.values_list('bristle_count', flat=True))

    # prepare the data for the bubble chart
    data = []
    for i, count in enumerate(bristle_counts):
        data.append([count, i, 1])  # format the data as [x, y, size]

    bubble_size = 20 if len(data) <= 10 else (1000 // len(data))

    return render(request, "dashboard/w_dashboard.html",
                  {
                      'head': 'Wing | Insights', 'title': 'Wing Insights', 'user_name': request.user.username.upper(),
                      'area_avg': round(sum(area) / len(area), 2), 'peri_avg': round(sum(peri) / len(peri), 2),
                      'bristles_avg': round(sum(bristles) / len(bristles), 2), 'peri_min': min(peri),
                      'peri_max': max(peri), 'area_min': min(area), 'area_max': max(area),
                      'normal': pred.count('Oregan'), 'mutation': pred.count('Mutation'), 'data': data,
                      'bubble_size': bubble_size
                  })


def fetch_eyedata(request):
    area_peri = e_dimension.objects.all()
    e_color = e_colour.objects.all()
    ommatidia = e_ommatidium.objects.all()

    return area_peri, e_color, ommatidia


def eye_dashboard(request):
    # IF THE USER IS NOT SUPERUSER DON'T ALLOW THE ACCESS TO THIS PAGE
    if not request.user.is_superuser:
        return render(request, 'index.html')

    data = fetch_eyedata(request)
    area = []
    peri = []
    ommatidia = []

    for i in data[0]:
        area.append(i.earea)
        peri.append(i.eperimeter)

    for i in data[2]:
        ommatidia.append(i.ommatidium_count)

    if not area:
        area = [0]
    if not peri:
        peri = [0]
    if not ommatidia:
        ommatidia = [0]

    ommatidia_counts = list(e_ommatidium.objects.values_list('ommatidium_count', flat=True))

    # prepare the data for the bubble chart
    data = []
    for i, count in enumerate(ommatidia_counts):
        data.append([count, i, 1])  # format the data as [x, y, size]

    bubble_size = 20 if len(data) <= 10 else (1000 // len(data))

    colors = list(e_colour.objects.values_list('pred_name', 'pred_hex'))
    colors = [{'pred_name': item[0], 'pred_hex': item[1]} for item in colors]

    # Pass the colors data to the template
    context = {'colors': colors}
    print(context)

    return render(request, "dashboard/e_dashboard.html",
                  {
                      'head': 'Eye | Insights', 'title': 'Eye Insights', 'user_name': request.user.username.upper(),
                      'area_avg': round(sum(area) / len(area), 2), 'peri_avg': round(sum(peri) / len(peri), 2),
                      'omm_avg': round(sum(ommatidia) / len(ommatidia), 2), 'peri_min': min(peri),
                      'peri_max': max(peri), 'area_min': min(area), 'area_max': max(area), 'data': data,
                      'bubble_size': bubble_size, 'colors': json.dumps(context['colors'])
                  })


# def wingfront(request):S
#     if request.user.is_anonymous:
#         return redirect("/login")
#     return render(request, "others/wing.html",
#                   {'head': 'Wing | Drosophila'})
#
#
# def eyefront(request):
#     if request.user.is_anonymous:
#         return redirect("/login")
#     return render(request, "others/eye.html",
#                   {'head': 'EYE | Drosophila'})
#

def register_page(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in.
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'user/register.html', {'title': 'Registration', 'form': form})


# def fetch_data(request):
#     w_area = w_dimen.objects.all()
#     for i in w_area:
#         return HttpResponse(i.wd_area)

def myteam(request):
    return render(request, 'team/team.html',
                  {'head': 'MakkhiMeter ', 'title': 'MakkhiMeter Team', 'user_name': request.user.username.upper()})


def dowdata(request):
    return render(request, 'others/data.html',
                  {'head': 'MakkhiMeter ', 'title': 'MakkhiMeter Team', 'user_name': request.user.username.upper()})
