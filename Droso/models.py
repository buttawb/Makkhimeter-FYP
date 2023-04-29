from django.contrib.auth.models import User
from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files import File

from Drosometer import settings


def compress(image):
    im = Image.open(image)
    im_io = BytesIO()
    im.save(im_io, 'JPEG', quality=60)
    new_image = File(im_io, name=image.name)
    return new_image


class Wing_Image(models.Model):
    wing = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to="static\db_wingimages",
                              verbose_name="Image")
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE, null=True, blank=True,
                             verbose_name="User ID")
    hash = models.CharField(max_length=33,
                            verbose_name="MD5 Hash of Image")
    dt = models.DateTimeField(auto_now_add=True,
                              verbose_name="Date & Time")

    def save(self, *args, **kwargs):
        new_image = compress(self.image)
        self.image = new_image
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Wing Image"


class Eye_Image(models.Model):
    eye = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to="static\db_eyeimages",
                              verbose_name="Image")
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE, null=True, blank=True,
                             verbose_name="User ID")
    hash = models.CharField(max_length=33,
                            verbose_name="MD5 Hash of Image")
    dt = models.DateTimeField(auto_now_add=True,
                              verbose_name="Date & Time")

    def save(self, *args, **kwargs):
        new_image = compress(self.image)
        self.image = new_image
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Eye Image"


class w_dimen(models.Model):
    wdimen = models.AutoField(primary_key=True)
    wd_o_img = models.ForeignKey(Wing_Image,
                                 on_delete=models.CASCADE,
                                 default=None, null=True, blank=True,
                                 verbose_name="Original Image ID")
    # wd_o_img = models.CharField(max_length=600)
    # wd_b_img = models.CharField(max_length=600)

    wd_area = models.FloatField(max_length=100,
                                verbose_name="Wing overall Area")
    wd_peri = models.FloatField(max_length=100,
                                verbose_name="Wing overall Perimeter")

    # wd_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Later could be used for abstraction/permissions/proxy
        verbose_name = "Wing Dimension"


class w_shape(models.Model):
    wshape = models.AutoField(primary_key=True)
    ws_o_img = models.ForeignKey(Wing_Image,
                                 on_delete=models.CASCADE,
                                 default=None, null=True, blank=True,
                                 verbose_name="Original Image ID")
    # ws_o_img = models.CharField(max_length=600)
    ws_pred = models.CharField(max_length=10,
                               verbose_name="Prediction")

    ws_normal_prob = models.FloatField(max_length=100,
                                       verbose_name="Probability % of Normal")
    ws_mutated_prob = models.FloatField(max_length=100,
                                        verbose_name="Probability % of Mutant")

    # ws_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Wing Shape"


class w_bristles(models.Model):
    wbrisltes = models.AutoField(primary_key=True)
    wb_o_img = models.ForeignKey(Wing_Image,
                                 on_delete=models.CASCADE, null=True, blank=True,
                                 default=None,
                                 verbose_name="Original Image ID")
    bristle_count = models.IntegerField(verbose_name="Wing overall Bristles")

    class Meta:
        verbose_name = "Wing Bristle"


# class colour(models.Model):
#     color = models.AutoField(primary_key=True)
#     color_name = models.CharField(max_length=100,
#                                   verbose_name="Colour Name")
#
#     class Meta:
#         verbose_name = "Colour"


class e_colour(models.Model):
    ecolour = models.AutoField(primary_key=True)
    ec_o_img = models.ForeignKey(Eye_Image,
                                 on_delete=models.CASCADE,
                                 default=None, null=True, blank=True,
                                 verbose_name="Original Image ID")

    # col1 = models.ForeignKey(colour,
    #                          on_delete=models.CASCADE,
    #                          default=None,
    #                          verbose_name="Colour 1 ID",
    #                          related_name="a")
    # col2 = models.ForeignKey(colour,
    #                          on_delete=models.CASCADE,
    #                          default=None,
    #                          verbose_name="Colour 2 ID",
    #                          related_name="b")
    # col3 = models.ForeignKey(colour,
    #                          on_delete=models.CASCADE,
    #                          default=None,
    #                          verbose_name="Colour 3 ID",
    #                          related_name="c")
    # col4 = models.ForeignKey(colour,
    #                          on_delete=models.CASCADE,
    #                          default=None,
    #                          verbose_name="Colour 4 ID",
    #                          related_name="d")

    c1_hex = models.CharField(max_length=100,
                              verbose_name="Colour 1 Hex Value")
    c2_hex = models.CharField(max_length=100,
                              verbose_name="Colour 2 Hex Value")
    c3_hex = models.CharField(max_length=100,
                              verbose_name="Colour 3 Hex Value")
    c4_hex = models.CharField(max_length=100,
                              verbose_name="Colour 4 Hex Value")

    c1_p = models.FloatField(max_length=100,
                             verbose_name="Colour 1 %")
    c2_p = models.FloatField(max_length=100,
                             verbose_name="Colour 2 %")
    c3_p = models.FloatField(max_length=100,
                             verbose_name="Colour 3 %")
    c4_p = models.FloatField(max_length=100,
                             verbose_name="Colour 4 %")

    c1_name = models.CharField(max_length=100,
                               verbose_name="Colour 1 name")
    c2_name = models.CharField(max_length=100,
                               verbose_name="Colour 2 name")
    c3_name = models.CharField(max_length=100,
                               verbose_name="Colour 3 name")
    c4_name = models.CharField(max_length=100,
                               verbose_name="Colour 4 name")

    pred_name = models.CharField(max_length=10,
                                 verbose_name="Predicted Colour")
    pred_hex = models.CharField(max_length=100,
                                verbose_name="Predicted COlour Hex Value")


class Meta:
    verbose_name = "Eye Colour"


class e_dimension(models.Model):
    edimension = models.AutoField(primary_key=True)
    ed_o_img = models.ForeignKey(Eye_Image,
                                 on_delete=models.CASCADE,
                                 default=None, null=True, blank=True,
                                 verbose_name="Original Image ID")
    earea = models.FloatField(max_length=100,
                              verbose_name="Eye overall Area")
    eperimeter = models.FloatField(max_length=100,
                                   verbose_name="Eye overall Perimeter")

    class Meta:
        verbose_name = "Eye Dimension"


class e_ommatidium(models.Model):
    emodel = models.AutoField(primary_key=True)
    eo_o_img = models.ForeignKey(Eye_Image,
                                 on_delete=models.CASCADE,
                                 default=None, null=True, blank=True,
                                 verbose_name="Original Image ID")
    ommatidium_count = models.IntegerField(verbose_name="Eye overall Ommatidium")

    class Meta:
        verbose_name = "Eye Ommatidium"
        verbose_name_plural = "Eye Ommatidium"


class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        pass

    def __str__(self):
        return self.name
