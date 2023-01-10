import io
import os
import uuid
import glob
import imagehash
import json

from PIL import Image
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.http import HttpResponse

from Droso.models import *

# IMPORTING SCRIPTS
from Python_Scripts.DIP.Wings.Wing_Bristles import *
from Python_Scripts.DIP.Wings.Wing_Dimensions import *
from Python_Scripts.DIP.Eyes.Eye_Ommatidium import *
from Python_Scripts.DIP.Eyes.Eye_Dimensions import *
from Python_Scripts.DIP.Eyes.Eye_Colour import *

from Python_Scripts.DL import dl

# CREATING OBJECTS
WD_PreP = WD_PreProcessing()
WD_P = WD_Procesing()
WD_PostP = WD_PostProcessing()

WB_PreP = WB_PreProcessing()
EO_PreP = EO_PreProcessing()


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
    __clear_cache(__find_userpath(request) + "/cache")
    # LOGOUT USER
    logout(request)

    return render(request, 'user/logout.html')


def __reader(obj):
    # FUNCTION TO READ IMAGES
    data = obj.read()
    file = io.BytesIO(data)
    open_file = Image.open(file)

    return open_file


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


def __upload_file_to_userdir(request, file, file_format, flag=True, cache=False):
    # ASSIGNS NAME AND PATH TO THE FILE
    # SAVE FILE ONLY IF FLAG IS TRUE
    path = __find_userpath(request)
    rand_name = str(uuid.uuid4())
    if flag:
        if cache:
            final_path = path + "/cache/" + rand_name + file_format
            file.save(final_path)
            return final_path
        # UPLOADS USER FILES TO THEIR DIRECTORY
        else:
            final_path = path + "/" + rand_name + file_format
            file.save(final_path)
            return final_path
    else:
        if cache:
            final_path = path + "/cache/" + rand_name + file_format
            return final_path
        else:
            final_path = path + "/" + rand_name + file_format
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

    print(len(corners))

    if len(corners) > 2000:
        return True
    else:
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
    cache = path + '/cache'
    # CHECK THE VERY EXISTENCE OF THE DIRECTORY
    is_exist = os.path.exists(path)
    if is_exist:
        pass
    else:
        # MAKE A DIRECTORY NAMED WITH USERNAME
        os.mkdir(path)
        os.mkdir(cache)

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
        # pre_process = preprocess(img2)

        # CHECK EITHER THE IMAGE IS OF WING OR NOT.
        orig_img = __upload_file_to_userdir(request, img2, '.png', flag=True, cache=True)
        if not image_check(img1, orig_img):
            return render(request, 'wings/dimensions/w_dimen2.html',
                          {'head': 'Wings | Dimensions', 'img_path': orig_img,
                           'img_name': 'Uploaded Image: ', 'out1': 'The image uploaded is ', 'ans': 'NOT',
                           'out2': 'of wing', 'out3': 'Let us know if this is by mistake.'})

        orig_img = __upload_file_to_userdir(request, img2, '.png', flag=True)
        p = cv2.imread(orig_img)
        img = img_as_ubyte(p)
        # print(p)
        # print(img)
        # fimg = save_img(img2, 'wing')
        global wing_d
        wing_d = Wing_Image()
        wing_d.image = img
        wing_d.user = request.user
        wing_d.save()

        pre_process = WD_PreP.PreProcessing_2(img2)

        global orig_img_fn

        def orig_img_fn():
            return orig_img

        save_file = __upload_file_to_userdir(request, pre_process, '.png', flag=False, cache=True)
        file_path = save_file

        plt.imsave(file_path, pre_process, cmap='gray')

        for_dil = cv2.imread(file_path, 0)
        save_dil = __upload_file_to_userdir(request, 'dil', '.png', flag=False, cache=True)
        global dilation_bar
        global save_dil_path

        def save_dil_path():
            return save_dil

        def dilation_bar():
            return for_dil

        global mymy

        def mymy():
            return save_file

        # request.session['dilation'] = for_dil
        # dil = dilation(for_dil)
        # save_dil = __upload_file_to_userdir(request, dil, '.png', flag=False)
        # global dil_path
        # dil_path = save_dil
        # plt.imsave(dil_path, dil, cmap='gray')

        return redirect('/bar',
                        {'head': 'Drosometer | Wings'})

    return render(request, 'wings/dimensions/w_dimen2.html',
                  {'head': 'Wings | Dimensions', 'img_path': '../static/images/perfect.png',
                   'img_name': 'Like this: '})


def wingshape(request):
    # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
    if request.user.is_anonymous:
        return redirect("/login")

    return render(request, 'wings/shape/w_shape.html', {'head': 'Drosometer | Wings'})


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

        # CHECK EITHER THE IMAGE IS OF WING OR NOT.
        path = __upload_file_to_userdir(request, img2, '.png', flag=True, cache=True)
        if not image_check(img1, path):
            return render(request, 'wings/dimensions/w_dimen2.html',
                          {'head': 'Wings | Dimensions', 'img_path': path,
                           'img_name': 'Uploaded Image: ', 'out1': 'The image uploaded is ', 'ans': 'NOT',
                           'out2': 'of wing', 'out3': 'Let us know if this is by mistake.'})

        path = __upload_file_to_userdir(request, img2, '.png')

        wing_s = Wing_Image()
        wing_s.image = uploaded_img
        wing_s.user = request.user
        wing_s.save()

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
        if pred == 0:
            shape.ws_pred = 'Mutation'
        else:
            shape.ws_pred = 'Oregan'
        shape.ws_normal_prob = prob_oreg
        shape.ws_mutated_prob = prob_mut
        shape.ws_o_img = wing_s
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

        orig_img = __upload_file_to_userdir(request, img1, '.png', flag=True, cache=True)
        # CHECK EITHER THE IMAGE IS OF WING OR NOT.
        if not image_check(img1, orig_img):
            return render(request, 'wings/dimensions/w_dimen2.html',
                          {'head': 'Wings | Dimensions', 'img_path': orig_img,
                           'img_name': 'Uploaded Image: ', 'out1': 'The image uploaded is ', 'ans': 'NOT',
                           'out2': 'of wing', 'out3': 'Let us know if this is by mistake.'})

        crop_img = __upload_file_to_userdir(request, img1, ".png")
        request.session['crop_img'] = crop_img

        img = Image.open(crop_img)
        img1 = WB_PreP.PreProcessing(img)
        # img1 = prepreprocess(img)
        plt.imsave(crop_img, img1[2], cmap='gray')

        return redirect("/cropper_wing", {'head': 'Bristles | Finder', 'img': crop_img})

    return render(request, 'wings/bristles/w_bristles2.html',
                  {'head': 'Wings | Bristles', 'img_path': '../static/images/perfect.png',
                   'img_name': 'Like this: '})


def cropper_bristles(request):
    if request.user.is_anonymous:
        return redirect("/login")
    crop_img = request.session['crop_img']
    return render(request, 'wings/bristles/cropper.html', {'head': 'Bristles | Finder', 'img': crop_img})


def cropper_eye(request):
    if request.user.is_anonymous:
        return redirect("/login")
    crop_img_eye = request.session['crop_img']
    return render(request, 'eyes/ommatidum/cropper.html', {'head': 'Ommatidium | Finder', 'img': crop_img_eye})


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

# def w_option(request):
#     # IF THE USER TRIES TO ACCESS ANY PAGE WITH URL WITHOUT SIGNING IN. REDIRECT TO LOGIN PAGE.
#     if request.user.is_anonymous:
#         return redirect("/login")
#
#     save_dil = dil_img()
#     return render(request, 'wings/dimensions/opt.html',
#                   {'head': 'Drosometer | Wings', 'img_path': save_dil, 'img_name': 'Uploaded Image'})

def df_to_html(df):
    json_records = df.reset_index().to_json(orient='records')
    data = []
    data = json.loads(json_records)
    return data


def w_bar(request):
    if request.user.is_anonymous:
        return redirect("/login")

    # for_dil = request.session['dilation']
    for_dil = dilation_bar()
    save_dil = save_dil_path()

    def algorithm_selection(algorithm, save_dil):
        get_values = get_values_from_slider(request, for_dil, save_dil)
        save_dil = get_values[0]
        dil = get_values[1]

        global images

        def images():
            return path1, path2, outimg, outimg2

        path1 = __upload_file_to_userdir(request, 'xyz', '.png', flag=False, cache=True)
        path2 = __upload_file_to_userdir(request, 'xyz', '.png', flag=False, cache=True)

        outimg = __upload_file_to_userdir(request, 'xyz', '.png', flag=False, cache=True)
        outimg2 = __upload_file_to_userdir(request, 'xyz', '.png', flag=False, cache=True)
        step1 = algorithm(dil, path1, path2, outimg, outimg2)

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

        # STORING AREA & PERIMETER OF THE WHOLE WING IN DATABASE
        dimen = w_dimen()

        for i in dat:
            dimen.wd_peri = list(i.values())[-1]
            dimen.wd_area = list(i.values())[-2]
            dimen.wd_o_img = wing_d
            dimen.save()

        return data, dat, outimg, outimg2

    if 'highlight' in request.POST:
        dil = WD_P.Dilation(for_dil)
        # dil = dilation(for_dil)
        plt.imsave(save_dil, dil, cmap='gray')

        return render(request, 'wings/dimensions/bar.html',
                      {'head': 'Dimensions | Exposure', 'img_path': save_dil, 'img_name': 'Uploaded Image',
                       'val1': 7,
                       'val2': 12, 'but_name': 'Reset to default values'})

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
                      {'head': 'Dimensions | Exposure', 'img_path': save_dil, 'img_name': 'Uploaded Image',
                       'val1': val1, 'val2': val2, 'but_name': 'Reset to default values'})

    if 'default' in request.POST:
        dil = WD_P.Dilation(for_dil)
        # dil = dilation(for_dil)
        plt.imsave(save_dil, dil, cmap='gray')
        return render(request, 'wings/dimensions/bar.html',
                      {'head': 'Dimensions | Exposure', 'img_path': save_dil, 'img_name': 'Uploaded Image', 'val1': 7,
                       'val2': 12, 'but_name': 'Reset to default values'})
    orig_img = orig_img_fn()

    global flag
    flag = True

    if 'yes' in request.POST:
        flag = True
        result = algorithm_selection(WD_P.Skelatonize, save_dil)
        data, dat, outimg, outimg2 = result[0], result[1], result[2], result[3]

        return render(request, 'wings/dimensions/output.html',
                      {'d': data, 'head': 'Dimensions | Result', 'img2': outimg, 'img1': outimg2, 'f': dat,
                       'orig_img': orig_img})

    if 'no' in request.POST:
        flag = False
        result = algorithm_selection(WD_P.FloodFill, save_dil)
        # result = algorithm_selection(other_option, save_dil)
        data, dat, outimg, outimg2 = result[0], result[1], result[2], result[3]

        return render(request, 'wings/dimensions/output.html',
                      {'d': data, 'head': 'Dimensions | Result', 'img2': outimg, 'img1': outimg2, 'f': dat,
                       'orig_img': orig_img})

    else:
        return render(request, 'wings/dimensions/bar.html',
                      {'head': 'Dimensions | Exposure', 'img_path': orig_img_fn(), 'img_name': 'Uploaded Image',
                       'val1': 7,
                       'val2': 12, 'but_name': 'Extract wing.'})


def detail_dimen(request):
    if request.user.is_anonymous:
        return redirect("/login")

    if flag:
        img1 = orig_img_fn()
        img2 = save_dil_path()
        img3 = mymy()

        fin = images()
        img4 = fin[0]
        img5 = fin[1]
        img6 = fin[2]
        img7 = fin[3]
        return render(request, 'wings/dimensions/detail_1.html',
                      {'head': 'Dimensions | Detailed steps', 'img1': img1, 'img2': img2, 'img3': img3, 'img4': img4,
                       'img5': img5, 'img6': img6, 'img7': img7})

    else:
        img1 = orig_img_fn()
        img2 = save_dil_path()
        img3 = mymy()

        fin = images()
        img4 = fin[0]
        img6 = fin[2]
        img7 = fin[3]

        return render(request, 'wings/dimensions/detail_2.html',
                      {'head': 'Dimensions | Detailed steps', 'img1': img1, 'img2': img2, 'img3': img3, 'img4': img4,
                       'img6': img6, 'img7': img7})


def get_values_from_slider(request, for_dil, save_dil):
    val1 = int(request.POST.get('range1'))
    val2 = int(request.POST.get('range2'))

    dil = WD_P.Dilation(for_dil, val1, val2)
    # dil = dilation(for_dil, val1, val2)
    plt.imsave(save_dil, dil, cmap='gray')
    return save_dil, dil, val1, val2


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

        eye_o = Eye_Image()
        eye_o.image = uploaded_img
        eye_o.user = request.user
        eye_o.save()

        img1 = uploaded_img.read()
        # img1 = __reader(uploaded_img)

        crop_img_eye = __upload_file_to_userdir(request, img1, ".png")
        request.session['crop_img_eye'] = crop_img_eye

        img = Image.open(crop_img_eye)
        img1 = WB_PreP.PreProcessing(img)
        # img1 = prepreprocess(img)
        plt.imsave(crop_img_eye, img1[2], cmap='gray')

        return redirect("/cropper_eye", {'head': 'Ommatidium | Finder', 'img': crop_img_eye})

    return render(request, 'eyes/ommatidum/omat_2.html',
                  {'head': 'Eyes | Ommatidium Count', 'img_path': '../static/images/eye_front.png',
                   'img_name': 'Like this: '})


def register_page(request):
    return render(request, 'user/register.html')
