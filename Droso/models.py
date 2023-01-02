from django.contrib.auth.models import User
from django.db import models


class Wing_Image(models.Model):
    wing = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to="static\db_wingimages")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        pass


class Eye_Image(models.Model):
    eye = models.AutoField(primary_key=True)
    image = models.CharField(max_length=200)
    dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        pass


class w_dimen(models.Model):
    wdimen = models.AutoField(primary_key=True)
    wd_o_img = models.ForeignKey(Wing_Image, on_delete=models.CASCADE, default=None)
    # wd_o_img = models.CharField(max_length=600)
    # wd_b_img = models.CharField(max_length=600)

    wd_area = models.FloatField(max_length=100)
    wd_peri = models.FloatField(max_length=100)

    # wd_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Later could be used for abstraction/permissions/proxy
        pass


class w_shape(models.Model):
    wshape = models.AutoField(primary_key=True)
    ws_o_img = models.ForeignKey(Wing_Image, on_delete=models.CASCADE, default=None)
    # ws_o_img = models.CharField(max_length=600)
    ws_pred = models.CharField(max_length=10)

    ws_normal_prob = models.FloatField(max_length=100)
    ws_mutated_prob = models.FloatField(max_length=100)

    # ws_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        pass


class w_bristles(models.Model):
    wbrisltes = models.AutoField(primary_key=True)
    wb_o_img = models.ForeignKey(Wing_Image, on_delete=models.CASCADE, default=None)
    bristle_count = models.IntegerField()

    class Meta:
        pass


class e_colour(models.Model):
    ecolour = models.AutoField(primary_key=True)
    ec_o_img = models.ForeignKey(Eye_Image, on_delete=models.CASCADE, default=None)

    colour1 = models.FloatField(max_length=100)
    colour2 = models.FloatField(max_length=100)
    colour3 = models.FloatField(max_length=100)

    pred = models.CharField(max_length=10)

    class Meta:
        pass


class e_dimension(models.Model):
    edimension = models.AutoField(primary_key=True)
    ed_o_img = models.ForeignKey(Eye_Image, on_delete=models.CASCADE, default=None)
    earea = models.FloatField(max_length=100)
    eperimeter = models.FloatField(max_length=100)

    class Meta:
        pass


class e_ommatidium(models.Model):
    emodel = models.AutoField(primary_key=True)
    eo_o_img = models.ForeignKey(Eye_Image, on_delete=models.CASCADE, default=None)

    ommatidium_count = models.IntegerField()

    class Meta:
        pass
