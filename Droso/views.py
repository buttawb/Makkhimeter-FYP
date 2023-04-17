import glob
import hashlib
import io
import json
import os
import uuid

from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from Droso.forms import CustomUserCreationForm
from Droso.models import *

from Python_Scripts.DIP.Eyes.Eye_Colour import *
from Python_Scripts.DIP.Eyes.Eye_Dimensions import *
from Python_Scripts.DIP.Eyes.Eye_Ommatidium import *

# IMPORTING SCRIPTS
from Python_Scripts.DIP.Wings.Wing_Bristles import *
from Python_Scripts.DIP.Wings.Wing_Dimensions import *
from Python_Scripts.DL import dl

# CREATING OBJECTS
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
            return render(request, 'user/login.html', {'note': 'Wrong Login credentials detected.'})

    return render(request, 'user/login.html', {'note2': 'Enter username and password to continue...'})


def logoutUser(request):
    # CLEAR USER CACHE
    __clear_cache(__find_userpath(request))
    # LOGOUT USER
    logout(request)

    return render(request, 'user/logout.html')


def __reader(obj):
    # FUNCTION TO READ IMAGES
    data = obj.read()
    file = io.BytesIO(data)
    open_file = Image.open(file)

    return open_file


def md5(img_path):
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
    u_name = str(request.user)
    base = 'static/users'
    path = base + '/' + u_name
    return path


def __clear_cache(path):
    path = path + '/*'
    files = glob.glob(path)
    for all_files in files:
        os.remove(all_files)
    return


def image_check(img, path):
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


def main(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    path = __find_userpath(request)

    __clear_cache(__find_userpath(request))

    # CHECK THE VERY EXISTENCE OF THE DIRECTORY
    is_exist = os.path.exists(path)
    if is_exist:
        pass
    else:
        # MAKE A DIRECTORY NAMED WITH USERNAME
        os.mkdir(path)

    return render(request, 'index.html', {'head': 'Makkhimeter | DOW-UIT', 'user_name': request.user.username.upper()})


def wingdimen(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    return render(request, 'wings/dimensions/w_dimen.html',
                  {'head': 'Makkhimeter | wing', 'user_name': request.user.username.upper()})


def wingdimen2(request):
    # If the user tries to access any page with URL without signing in, redirect to login page.
    if request.user.is_anonymous:
        return redirect("/login")

    if request.method == 'POST':
        uploaded_img = request.FILES['img']

        try:
            # Validate the uploaded image file
            allowed_extensions = ['png', 'tif', 'jpg', 'jpeg']
            ext_validator = FileExtensionValidator(allowed_extensions=allowed_extensions)
            ext_validator(uploaded_img)
        except (KeyError, ValidationError):
            # If the file was not uploaded or is not a valid image, render an error page
            return render(request, 'wings/dimensions/w_dimen2.html',
                          {'head': 'wing | Dimensions', 'img_path': 'static/images/404.gif',
                           'img_name': 'Uploaded Image: ', 'out1': 'The file uploaded is either ', 'ans': 'NOT',
                           'out2': 'an image or not of required format.', 'out3': '',
                           'out4': 'Accepted formats include TIFF, PNG, '
                                   'JPG & JPEG.',
                           'user_name': request.user.username.upper()})

        # CHECK EITHER THE IMAGE IS OF WING OR NOT.
        img1 = __reader(uploaded_img)
        img2 = img1.convert('RGB')
        orig_img = __upload_file_to_userdir(request, img2, '.png', flag=True)

        if not image_check(img1, orig_img):
            return render(request, 'wings/dimensions/w_dimen2.html',
                          {'head': 'wing | Dimensions', 'img_path': orig_img,
                           'img_name': 'Uploaded Image: ', 'out1': 'The image uploaded is ', 'ans': 'NOT',
                           'out2': ' of wing', 'out3': 'Let us know if this is by mistake.',
                           'user_name': request.user.username.upper()})

        orig_img = __upload_file_to_userdir(request, img2, '.png', flag=True)
        # p = cv2.imread(orig_img)
        global dimen_flag
        hash_d = md5(orig_img)

        dimen_flag = False
        try:
            wing = Wing_Image.objects.get(hash=hash_d)
            global wing_object
            wing_object = wing
            dimen_flag = True

        except Wing_Image.DoesNotExist:
            global wingg
            wingg = Wing_Image()
            wingg.image = uploaded_img
            wingg.user = request.user
            wingg.hash = hash_d
            wingg.save()

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

        global dilation_bar
        global save_dil_path
        global orig_img_fn
        global wing_dimen_ui
        global mymy

        wing_dimen_ui = uploaded_img

        orig_img_fn = orig_img

        save_dil_path = save_dil

        dilation_bar = for_dil

        mymy = save_file

        # request.session['dilation'] = for_dil
        # dil = dilation(for_dil)
        # save_dil = __upload_file_to_userdir(request, dil, '.png', flag=False)
        # global dil_path
        # dil_path = save_dil
        # plt.imsave(dil_path, dil, cmap='gray')

        return redirect('/bar',
                        {'head': 'Makkhimeter | wing', 'user_name': request.user.username.upper()})

    return render(request, 'wings/dimensions/w_dimen2.html',
                  {'head': 'wing | Dimensions', 'img_path': '../static/images/perfect.png',
                   'img_name': 'Expected Input Image ', 'user_name': request.user.username.upper()})


def w_bar(request):
    if request.user.is_anonymous:
        return redirect("/login")

    # for_dil = request.session['dilation']
    for_dil = dilation_bar
    save_dil = save_dil_path

    def algorithm_selection(algorithm, save_dil):
        get_values = get_values_from_slider(request, for_dil, save_dil)
        save_dil = get_values[0]
        dil = get_values[1]

        global images

        def images():
            return path1, path2, outimg, outimg2

        path1 = __upload_file_to_userdir(request, 'xyz', '.png', flag=False)
        path2 = __upload_file_to_userdir(request, 'xyz', '.png', flag=False)

        outimg = __upload_file_to_userdir(request, 'xyz', '.png', flag=False)
        outimg2 = __upload_file_to_userdir(request, 'xyz', '.png', flag=False)
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

        # STORING IN DATABASE

        if not dimen_flag:
            dimen = w_dimen()
            for i in dat:
                dimen.wd_peri = list(i.values())[-1]
                dimen.wd_area = list(i.values())[-2]
                dimen.wd_o_img = wingg
            dimen.save()
        else:
            try:
                dimen = w_dimen.objects.get(wd_o_img=wing_object)
            except w_dimen.DoesNotExist:
                dimen = w_dimen()
                for i in dat:
                    dimen.wd_peri = list(i.values())[-1]
                    dimen.wd_area = list(i.values())[-2]
                dimen.wd_o_img = wing_object
                dimen.save()

        return data, dat, outimg, outimg2

    if 'highlight' in request.POST:
        WD_P.preprocess_img = for_dil
        dil = WD_P.Dilation()
        # dil = dilation(for_dil)
        plt.imsave(save_dil, dil, cmap='gray')

        return render(request, 'wings/dimensions/bar.html',
                      {'head': 'Dimensions | Exposure', 'img_path': save_dil, 'img_name': 'Binary Image',
                       'val1': 7, 'val2': 12, 'img_p': orig_img_fn, 'img_n': 'Original Image',
                       'but_name': 'Reset to default values', 'user_name': request.user.username.upper()})

    if 'check' in request.POST:
        # VALUE GET NAI HORAI
        global values_from_slider

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
                      {'head': 'Dimensions | Exposure', 'img_path': save_dil, 'img_name': 'Binary Image',
                       'img_p': orig_img_fn, 'img_n': 'Original Image',
                       'val1': val1, 'val2': val2, 'but_name': 'Reset to default values',
                       'user_name': request.user.username.upper()})

    if 'default' in request.POST:
        WD_P.preprocess_img = for_dil
        dil = WD_P.Dilation()
        # dil = dilation(for_dil)
        plt.imsave(save_dil, dil, cmap='gray')
        return render(request, 'wings/dimensions/bar.html',
                      {'head': 'Dimensions | Exposure', 'img_path': save_dil, 'img_name': 'Binary Image', 'val1': 7,
                       'val2': 12, 'but_name': 'Reset to default values',
                       'img_p': orig_img_fn, 'img_n': 'Original Image', 'user_name': request.user.username.upper()})
    orig_img = orig_img_fn

    global flag
    flag = True

    if 'yes' in request.POST:
        flag = True

        result = algorithm_selection(WD_P.Skelatonize, save_dil)
        data, dat, outimg, outimg2 = result[0], result[1], result[2], result[3]

        return render(request, 'wings/dimensions/output.html',
                      {'d': data, 'head': 'Dimensions | Result', 'img2': outimg, 'img1': outimg2, 'f': dat,
                       'orig_img': orig_img, 'user_name': request.user.username.upper()})

    if 'no' in request.POST:
        flag = False
        result = algorithm_selection(WD_P.FloodFill, save_dil)
        # result = algorithm_selection(other_option, save_dil)
        data, dat, outimg, outimg2 = result[0], result[1], result[2], result[3]

        return render(request, 'wings/dimensions/output.html',
                      {'d': data, 'head': 'Dimensions | Result', 'img2': outimg, 'img1': outimg2, 'f': dat,
                       'orig_img': orig_img, 'user_name': request.user.username.upper()})

    else:
        return render(request, 'wings/dimensions/bar.html',
                      {'head': 'Dimensions | Exposure', 'img_path': save_dil, 'img_name': 'Binary Image',
                       'val1': 7, 'val2': 12, 'img_p': orig_img_fn, 'img_n': 'Original Image',
                       'but_name': 'Extract binary', 'user_name': request.user.username.upper()})


def detail_dimen(request):
    if request.user.is_anonymous:
        return redirect("/login")

    if flag:
        img1 = orig_img_fn
        img2 = save_dil_path
        img3 = mymy

        fin = images()
        img4 = fin[0]
        img5 = fin[1]
        img6 = fin[2]
        img7 = fin[3]
        return render(request, 'wings/dimensions/detail_1.html',
                      {'head': 'Dimensions | Detailed steps', 'img1': img1, 'img2': img2, 'img3': img3, 'img4': img4,
                       'img5': img5, 'img6': img6, 'img7': img7, 'user_name': request.user.username.upper()})

    else:
        img1 = orig_img_fn
        img2 = save_dil_path
        img3 = mymy

        fin = images()
        img4 = fin[0]
        img6 = fin[2]
        img7 = fin[3]

        return render(request, 'wings/dimensions/detail_2.html',
                      {'head': 'Dimensions | Detailed steps', 'img1': img1, 'img2': img2, 'img3': img3, 'img4': img4,
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
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    return render(request, 'wings/shape/w_shape.html',
                  {'head': 'Makkhimeter | wing', 'user_name': request.user.username.upper()})


def wingshape2(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    if request.method == 'POST':
        uploaded_img = request.FILES['img']

        try:
            # Validate the uploaded image file
            allowed_extensions = ['tif']
            ext_validator = FileExtensionValidator(allowed_extensions=allowed_extensions)
            ext_validator(uploaded_img)
        except (KeyError, ValidationError):
            # If the file was not uploaded or is not a valid image, render an error page
            return render(request, 'wings/dimensions/w_dimen2.html',
                          {'head': 'Wing | Shape', 'img_path': 'static/images/404.gif',
                           'img_name': 'Uploaded Image: ', 'out1': 'The file uploaded is either ', 'ans': 'NOT',
                           'out2': ' an image or not of required format.', 'out3': '',
                           'out4': 'Accepted formats include TIFF',
                           'user_name': request.user.username.upper()})

        img1 = __reader(uploaded_img)
        # yeh ubyte ko dena hai wind dimension
        # IMAGE CONVERSIONS FOR THE DL MODEL.
        img2 = img1.convert('RGB')

        # CHECK EITHER THE IMAGE IS OF WING OR NOT.
        path = __upload_file_to_userdir(request, img2, '.png', flag=True)
        if not image_check(img1, path):
            return render(request, 'wings/dimensions/w_dimen2.html',
                          {'head': 'wing | Dimensions', 'img_path': path,
                           'img_name': 'Uploaded Image: ', 'out1': 'The image uploaded is ', 'ans': 'NOT',
                           'out2': ' of wing', 'out3': 'Let us know if this is by mistake.',
                           'user_name': request.user.username.upper()})

        path = __upload_file_to_userdir(request, img2, '.png')

        md5_hash = md5(path)

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
        try:
            wing = Wing_Image.objects.get(hash=md5_hash)
            shape = w_shape.objects.filter(ws_o_img=wing).first()

            if not shape:
                s = w_shape()
                if pred == 0:
                    s.ws_pred = 'Mutation'
                else:
                    s.ws_pred = 'Oregan'
                s.ws_normal_prob = prob_oreg
                s.ws_mutated_prob = prob_mut
                s.ws_o_img = wing
                s.save()

        except Wing_Image.DoesNotExist:

            wing = Wing_Image()
            wing.image = uploaded_img
            wing.user = request.user
            wing.hash = md5_hash
            wing.save()

            s = w_shape()
            if pred == 0:
                s.ws_pred = 'Mutation'
            else:
                s.ws_pred = 'Oregan'
            s.ws_normal_prob = prob_oreg
            s.ws_mutated_prob = prob_mut
            s.ws_o_img = wing
            s.save()

        mutation = dl.k_model(path)

        if pred == 0:
            # RENDERING OUTPUTS ON HTML PAGE
            for subclass in mutation:
                print(subclass)
                if subclass == 1 or 0:
                    return render(request, 'wings/shape/w_shape2.html',
                                  {'head': 'wing | Shape', 'ans': 'Mutated', 'out': 'class.', 'prob_mut': prob_mut,
                                   'prob_oreg': prob_oreg, 'img_path': path, 'img_name': 'Uploaded Image: ',
                                   'sub_class': 'VG^1 or Xa /+ or Ser^1 / +', 'key': 'Broken Mutant Wing.',
                                   'user_name': request.user.username.upper()})
                if subclass == 4:
                    return render(request, 'wings/shape/w_shape2.html',
                                  {'head': 'wing | Shape', 'ans': 'Mutated', 'out': 'class.', 'prob_mut': prob_mut,
                                   'prob_oreg': prob_oreg, 'img_path': path, 'img_name': 'Uploaded Image: ',
                                   'sub_class': 'E^1', 'key': 'Colour differences. ',
                                   'user_name': request.user.username.upper()})
                if subclass == 5:
                    return render(request, 'wings/shape/w_shape2.html',
                                  {'head': 'wing | Shape', 'ans': 'Mutated', 'out': 'class.', 'prob_mut': prob_mut,
                                   'prob_oreg': prob_oreg, 'img_path': path, 'img_name': 'Uploaded Image: ',
                                   'sub_class': 'Ser^1 / +', 'key': 'Broken Wing.',
                                   'user_name': request.user.username.upper()})
                if subclass == 2 or 3 or 6:
                    return render(request, 'wings/shape/w_shape2.html',
                                  {'head': 'wing | Shape', 'ans': 'Mutated', 'out': 'class.', 'prob_mut': prob_mut,
                                   'prob_oreg': prob_oreg, 'img_path': path, 'img_name': 'Uploaded Image: ',
                                   'sub_class': 'Ser^1 / +', 'key': 'Damaged Wing.',
                                   'user_name': request.user.username.upper()})
        elif pred == 1:
            # RENDERING OUTPUTS ON HTML PAGE
            return render(request, 'wings/shape/w_shape2.html',
                          {'head': 'wing | Shape', 'ans': 'Oregan', 'out': 'class.', 'prob_oreg': prob_oreg,
                           'prob_mut': prob_mut, 'img_path': path, 'img_name': 'Uploaded Image: ',
                           'user_name': request.user.username.upper()})

    else:
        return render(request, 'wings/shape/w_shape2.html',
                      {'head': 'wing | Shape', 'img_path': '../static/images/perfect.png',
                       'img_name': 'Expected Input Image', 'user_name': request.user.username.upper()})


def wingbristles(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    return render(request, 'wings/bristles/w_bristles.html',
                  {'head': 'Makkhimeter | wing', 'user_name': request.user.username.upper()})


def wingbristles2(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    if request.method == "POST":
        uploaded_img = request.FILES['img']
        try:
            # Validate the uploaded image file
            allowed_extensions = ['tif']
            ext_validator = FileExtensionValidator(allowed_extensions=allowed_extensions)
            ext_validator(uploaded_img)

        except (KeyError, ValidationError):
            # If the file was not uploaded or is not a valid image, render an error page
            return render(request, 'wings/dimensions/w_dimen2.html',
                          {'head': 'wing | Bristles', 'img_path': 'static/images/404.gif',
                           'img_name': 'Uploaded Image: ', 'out1': 'The file uploaded is either ', 'ans': 'NOT',
                           'out2': ' an image or not of required format.', 'out3': '',
                           'out4': 'Accepted formats include TIFF',
                           'user_name': request.user.username.upper()})

        img1 = __reader(uploaded_img)

        orig_img = __upload_file_to_userdir(request, img1, '.png', flag=True)
        # CHECK EITHER THE IMAGE IS OF WING OR NOT.
        if not image_check(img1, orig_img):
            return render(request, 'wings/dimensions/w_dimen2.html',
                          {'head': 'wing | Dimensions', 'img_path': orig_img,
                           'img_name': 'Uploaded Image: ', 'out1': 'The image uploaded is ', 'ans': 'NOT',
                           'out2': ' of wing', 'out3': 'Let us know if this is by mistake.',
                           'user_name': request.user.username.upper()})

        crop_img = __upload_file_to_userdir(request, img1, ".png")

        # Agr image pehly se hi database mein pari wi hai..
        # #tu bristles count wale table mein us [pehly se] hi image wale ki id le kr ani paregi.

        hash_b = md5(crop_img)

        request.session['crop_img'] = crop_img

        img = Image.open(crop_img)
        img1 = WB_PreP.PreProcessing(img)
        # img1 = prepreprocess(img)
        plt.imsave(crop_img, img1[2], cmap='gray')

        WB_P.prep = crop_img

        try:
            wing = Wing_Image.objects.get(hash=hash_b)
            w_brisltes = w_bristles.objects.filter(wb_o_img=wing).first()
            if not w_brisltes:
                w_brisltes = w_bristles()
                w_brisltes.wb_o_img = wing
                w_brisltes.bristle_count = WB_P.overallbristles()
                w_brisltes.save()
        except Wing_Image.DoesNotExist:
            wing = Wing_Image()
            wing.image = uploaded_img
            wing.user = request.user
            wing.hash = hash_b
            wing.save()

            w_brisltes = w_bristles()
            w_brisltes.wb_o_img = wing
            w_brisltes.bristle_count = WB_P.overallbristles()
            w_brisltes.save()

        return redirect("/cropper_wing",
                        {'head': 'Bristles | Finder', 'img': crop_img, 'user_name': request.user.username.upper()})

    return render(request, 'wings/bristles/w_bristles2.html',
                  {'head': 'wing | Bristles', 'img_path': '../static/images/perfect.png',
                   'img_name': 'Expected Input Image ', 'user_name': request.user.username.upper()})


def cropper_bristles(request):
    if request.user.is_anonymous:
        return redirect("/login")
    crop_img = request.session['crop_img']
    return render(request, 'wings/bristles/cropper.html',
                  {'head': 'Bristles | Finder', 'img': crop_img, 'user_name': request.user.username.upper()})


def cropper_eye(request):
    if request.user.is_anonymous:
        return redirect("/login")
    crop_img_eye = request.session['crop_img_eye']
    return render(request, 'eyes/ommatidum/cropper.html',
                  {'head': 'Ommatidium | Finder', 'img': crop_img_eye, 'user_name': request.user.username.upper()})


def c_us(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    return render(request, 'others/contactus.html',
                  {'head': 'Makkhimeter | Contact Us', 'user_name': request.user.username.upper()})


def a_us(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    return HttpResponse("This page is going to be updated soon :)) ")
    # return render(request, 'others/aboutus.html',
    #               {'head': 'Makkhimeter | About Us', 'user_name': request.user.username.upper()})


def f_b(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    return render(request, 'others/feedback.html',
                  {'head': 'Makkhimeter | Give Feedback', 'user_name': request.user.username.upper()})


def wing_f(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")
    return render(request, 'f_w.html', {'head': 'Makkhimeter | wing', 'user_name': request.user.username.upper()})


def eye_f(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    return render(request, 'f_e.html', {'head': 'Makkhimeter | Eyes', 'user_name': request.user.username.upper()})


# def thorax_f(request):
#     if request.user.is_anonymous:
#         return redirect("/login")
#     return render(request, 'f_t.html', {'head': 'Makkhimeter | Thorax'})
#

# def w_option(request):
#     # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
#     if request.user.is_anonymous:
#         return redirect("/login")
#
#     save_dil = dil_img()
#     return render(request, 'wings/dimensions/opt.html',
#                   {'head': 'Makkhimeter | Wings', 'img_path': save_dil, 'img_name': 'Uploaded Image'})

def df_to_html(df):
    json_records = df.reset_index().to_json(orient='records')
    data = []
    data = json.loads(json_records)
    return data


def eye_omat(request):
    if request.user.is_anonymous:
        return redirect("/login")

    return render(request, 'eyes/ommatidum/omat_count.html',
                  {'head': 'Makkhimeter | Eyes', 'user_name': request.user.username.upper()})


def eye_omat2(request):
    if request.user.is_anonymous:
        return redirect("/login")

    if request.method == 'POST':
        uploaded_img = request.FILES['img']

        try:
            # Validate the uploaded image file
            allowed_extensions = ['jpg', 'jpeg']
            ext_validator = FileExtensionValidator(allowed_extensions=allowed_extensions)
            ext_validator(uploaded_img)

        except (KeyError, ValidationError):
            # If the file was not uploaded or is not a valid image, render an error page
            return render(request, 'eyes/ommatidum/omat_2.html',
                          {'head': 'Eye | Ommatidium', 'img_path': 'static/images/404.gif',
                           'img_name': 'Uploaded Image: ', 'out1': 'The file uploaded is either ', 'ans': 'NOT',
                           'out2': ' an image or not of required format.', 'out3': '',
                           'out4': 'Accepted formats include JPG & JPEG',
                           'user_name': request.user.username.upper()})

        img1 = Image.open(uploaded_img)
        # with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        #     f.save(temp_file.name)
        crop_img_eye = __upload_file_to_userdir(request, img1, ".png", flag=True)
        # img1 = uploaded_img.read()
        #
        #
        # crop_img_eye = __upload_file_to_userdir(request, img1, ".png")

        request.session['crop_img_eye'] = crop_img_eye

        img = Image.open(crop_img_eye)
        img1 = WB_PreP.PreProcessing(img)
        # img1 = prepreprocess(img)
        plt.imsave(crop_img_eye, img1[2], cmap='gray')

        ommatdia = EO_PreP.overallommatidium(crop_img_eye)
        md5_hash = md5(crop_img_eye)

        try:
            eye = Eye_Image.objects.get(hash=md5_hash)
            omm = e_ommatidium.objects.filter(eo_o_img=eye).first()
            if not e_ommatidium:
                eo = e_ommatidium()
                eo.eo_o_img = eye
                eo.ommatidium_count = ommatdia
                eo.save()

        except Eye_Image.DoesNotExist:
            eye = Eye_Image()
            eye.image = uploaded_img
            eye.user = request.user
            eye.hash = md5_hash
            eye.save()

            eo = e_ommatidium()
            eo.eo_o_img = eye
            eo.ommatidium_count = ommatdia
            eo.save()

        return redirect("/cropper_eye", {'head': 'Ommatidium | Finder', 'img': crop_img_eye,
                                         'user_name': request.user.username.upper()})

    return render(request, 'eyes/ommatidum/omat_2.html',
                  {'head': 'Eyes | Ommatidium Count', 'img_path': '../static/images/eye_front.jpg',
                   'img_name': 'Expected Input Image', 'user_name': request.user.username.upper()})


def eye_col(request):
    if request.user.is_anonymous:
        return redirect("/login")

    return render(request, 'eyes/colour/col.html',
                  {'head': 'Makkhimeter | Eyes', 'user_name': request.user.username.upper()})


def eye_col2(request):
    if request.user.is_anonymous:
        return redirect("/login")

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
                          {'head': 'Eye | Colour', 'img_path': 'static/images/404.gif',
                           'img_name': 'Uploaded Image: ', 'out1': 'The file uploaded is either ', 'ans': 'NOT',
                           'out2': ' an image or not of required format.', 'out3': '',
                           'out4': 'Accepted formats include TIFF, PNG, '
                                   'JPG & JPEG.',
                           'user_name': request.user.username.upper()})

        f = Image.open(uploaded_img)

        img_eye = __upload_file_to_userdir(request, f, ".png", flag=False)
        f.save(img_eye)

        md5_hash = md5(img_eye)

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

        df = dff.to_dict('records')

        lab = []
        hexval = []
        per = []

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
            col = e_colour.objects.filter(ec_o_img=eye).first()

            if not e_colour:
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
            eye.user = request.user
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

        js = json.dumps(data)
        return render(request, 'eyes/colour/output.html',
                      {'head': 'Eyes | Eye Colour', 'img': img_eye, 'd': df, 'main': lab[max_index],
                       'data': js,
                       'user_name': request.user.username.upper()})

    return render(request, 'eyes/colour/col2.html',
                  {'head': 'Eyes | Eye Colour', 'img_path': '../static/images/eye_front.jpg',
                   'img_name': 'Expected Input Image', 'user_name': request.user.username.upper()})


def hex_to_rgb(hex_value):
    red = int(hex_value[1:3], 16)
    green = int(hex_value[3:5], 16)
    blue = int(hex_value[5:7], 16)
    return red, green, blue


def eyedimen(request):
    if request.user.is_anonymous:
        return redirect("/login")
    return render(request, 'eyes/Dimensions/e_dimen.html',
                  {'head': 'Makkhimeter | Eyes', 'user_name': request.user.username.upper()})


def eyedimen2(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    if request.method == 'POST':
        uploaded_img = request.FILES['img']

        try:
            # Validate the uploaded image file
            allowed_extensions = ['png', 'tif', 'jpg', 'jpeg']
            ext_validator = FileExtensionValidator(allowed_extensions=allowed_extensions)
            ext_validator(uploaded_img)
        except (KeyError, ValidationError):
            # If the file was not uploaded or is not a valid image, render an error page
            return render(request, 'eyes/Dimension/e_dimen2.html',
                          {'head': 'Eye | Dimensions', 'img_path': 'static/images/404.gif',
                           'img_name': 'Uploaded Image: ', 'out1': 'The file uploaded is either ', 'ans': 'NOT',
                           'out2': ' an image or not of required format.', 'out3': '',
                           'out4': 'Accepted formats include TIFF, PNG, '
                                   'JPG & JPEG.',
                           'user_name': request.user.username.upper()})

        img1 = __reader(uploaded_img)
        img2 = img1.convert('RGB')
        orig_img = __upload_file_to_userdir(request, img2, '.png', flag=True)

        # if not image_check(img1, orig_img):
        #     return render(request, 'eyes/dimensions/e_dimen2.html',
        #                   {'head': 'Wings | Dimensions', 'img_path': orig_img,
        #                    'img_name': 'Uploaded Image: ', 'out1': 'The image uploaded is ', 'ans': 'NOT',
        #                    'out2': 'of eye', 'out3': 'Let us know if this is by mistake.',
        #                    'user_name': request.user.username.upper()})

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

        md5_hash = md5(orig_img)

        try:
            eye = Eye_Image.objects.get(hash=md5_hash)
            ed = e_dimension.objects.filter(ed_o_img=eye).first()
            if not ed:
                eye_d = e_dimension()
                eye_d.ed_o_img = eye
                eye_d.earea = area
                eye_d.eperimeter = peri
                eye_d.save()

        except Eye_Image.DoesNotExist:
            eye = Eye_Image()
            eye.image = uploaded_img
            eye.user = request.user
            eye.hash = md5_hash
            eye.save()

            eye_d = e_dimension()
            eye_d.ed_o_img = eye
            eye_d.earea = area
            eye_d.eperimeter = peri
            eye_d.save()

        return render(request, 'eyes/Dimensions/eyedimen_output.html',
                      {"orig": orig_img, "dil": dil_img, "Ar": area, "Pr": peri,
                       'user_name': request.user.username.upper()})

    return render(request, 'eyes/Dimensions/e_dimen2.html',
                  {'head': 'Eyes | Dimensions', 'img_path': '../static/images/eye_front.jpg',
                   'img_name': 'Expected Input Image', 'user_name': request.user.username.upper()})


def fetch_wingdata(request):
    area_peri = w_dimen.objects.all()
    nom_mut = w_shape.objects.all()
    bristle = w_bristles.objects.all()

    return area_peri, nom_mut, bristle


def wing_dashboard(request):
    if request.user.is_anonymous:
        return redirect("/login")

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

    return render(request, "dashboard/w_dashboard.html",
                  {
                      'head': 'Wing | Insights', 'user_name': request.user.username.upper(),
                      'area_avg': round(sum(area) / len(area), 2), 'peri_avg': round(sum(peri) / len(peri), 2),
                      'bristles_avg': round(sum(bristles) / len(bristles), 2), 'peri_min': min(peri),
                      'peri_max': max(peri), 'area_min': min(area), 'area_max': max(area),
                      'normal': pred.count('Oregan'), 'mutation': pred.count('Mutation')
                  })


def fetch_eyedata(request):
    area_peri = e_dimension.objects.all()
    e_color = e_colour.objects.all()
    ommatidia = e_ommatidium.objects.all()

    return area_peri, e_color, ommatidia


def eye_dashboard(request):
    if request.user.is_anonymous:
        return redirect("/login")

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

    return render(request, "dashboard/e_dashboard.html",
                  {
                      'head': 'Eye | Insights', 'user_name': request.user.username.upper(),
                      'area_avg': round(sum(area) / len(area), 2), 'peri_avg': round(sum(peri) / len(peri), 2),
                      'omm_avg': round(sum(ommatidia) / len(ommatidia), 2), 'peri_min': min(peri),
                      'peri_max': max(peri), 'area_min': min(area), 'area_max': max(area),
                  })


# def wingfront(request):
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
            login(request, user)
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'user/register.html', {'form': form})


# def fetch_data(request):
#     w_area = w_dimen.objects.all()
#     for i in w_area:
#         return HttpResponse(i.wd_area)

def myteam(request):
    if request.user.is_anonymous:
        return redirect('/login')

    return HttpResponse("This page is under construction. It'll be updated soon. :))")
