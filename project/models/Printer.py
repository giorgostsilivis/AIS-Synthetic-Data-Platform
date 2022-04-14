# -*- coding: utf-8 -*-
from flask import flash
import pandas as pd
from project.resampling import resampling


class Printer(object):

    def show_string(self, text):
        if text == '':
            flash("You didn't enter any text to flash")
        else:
            flash(text + "!!!")

class Data(object):

    def data_leech(self):
        # df = pd.read_csv('project/static/vessel.csv')[['longitude','latitude','sog']]
        df = pd.read_csv('project/static/vessel.csv')
        return df

class Data_pred(object):

    def data_leech(self):
        # df = pd.read_csv('project/static/vessel.csv')[['longitude','latitude','sog']]
        resampling.resample()
        df = pd.read_csv('project/static/pred_vessel.csv')
        return df