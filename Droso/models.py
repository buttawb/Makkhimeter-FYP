from django.db import models
import cv2


class w_dimen(models.Model):
    wdimen = models.AutoField(primary_key=True)

    wd_o_img = models.CharField(max_length=600)
    wd_b_img = models.CharField(max_length=600)

    wd_area = models.FloatField(max_length=100)
    wd_peri = models.FloatField(max_length=100)

    wd_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Later could be used for abstraction/permissions/proxy
        pass


class w_shape(models.Model):
    wshape = models.AutoField(primary_key=True)

    ws_o_img = models.CharField(max_length=600)
    ws_pred = models.CharField(max_length=10)

    ws_normal_prob = models.FloatField(max_length=100)
    ws_mutated_prob = models.FloatField(max_length=100)

    ws_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        pass
