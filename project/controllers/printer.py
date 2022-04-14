# -*- coding: utf-8 -*-
from project import app
from flask import render_template, request, redirect, url_for, flash, session, abort
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import folium
import pandas as pd
import os
from project.models.Printer import Printer, Data, Data_pred

class CreateForm(FlaskForm):
    text = StringField('name', validators=[DataRequired()])


@app.route('/')
def start():
    return render_template('printer/index.html')


@app.route('/print', methods=['GET', 'POST'])
def printer():
    form = CreateForm(request.form)
    if request.method == 'POST' and form.validate():
        printer = Printer()
        printer.show_string(form.text.data)
        return render_template('printer/index.html')
    return render_template('printer/print.html', form=form)


@app.route('/menu', methods=['GET', 'POST'])
def menu():
    # testvar  = 9419357
    return render_template('printer/menu.html')

@app.route('/map', methods=['GET','POST'])
def map():
    testvar  = 9419357
    return redirect('https://www.marinetraffic.com/en/ais/details/ships/imo:'+str(testvar))

@app.route('/upload')
def upload(messages=''):
   return render_template('printer/content.html',messages=messages)
	
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    printer = Printer()
    
    if request.method == 'POST':
        try:
            f = request.files['file']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            return redirect(url_for('mapdark'))
        except:
            # abort(500)
            messages= 'Please import a file'
            return render_template('printer/upload.html',messages=messages)
    else:
       return redirect(url_for('upload'))

@app.route('/mapdark', methods=['GET','POST'])
def mapdark():
    data = Data()
    df = data.data_leech()
    _mapdark = folium.Map(location=[df['latitude'][0], df['longitude'][0]],zoom_start=6,attributionControl=False,tiles='cartodbdark_matter')
    for index,row in df.iterrows():
        folium.Circle(
          location=[row['latitude'], row['longitude']],
          popup=str(row['sog'])+' kn',
          weight=1,
          radius=5,
          fill_color='Yellow',
          color='Blue',
          fill_opacity=row['sog']*0.05,
        ).add_to(_mapdark)

    data_ = Data_pred()
    df_ = data_.data_leech()
    # _mapdark = folium.Map(location=[df['latitude'][0], df['longitude'][0]],zoom_start=6,attributionControl=False,tiles='cartodbdark_matter')
    for index,row in df_.iterrows():
        folium.Circle(
          location=[row['latitude'], row['longitude']],
        #   popup=str(row['sog'])+' kn',
          weight=1,
          radius=5,
          fill_color='Yellow',
          color='Green',
        #   fill_opacity=row['sog']*0.05,
        ).add_to(_mapdark)
    # folium.TileLayer('cartodbdark_matter').add_to(_mapdark) # Sets Tile Theme to (Dark Theme)
    return _mapdark._repr_html_()


@app.route('/pred', methods=['GET','POST'])
def pred():
    data = Data_pred()
    df = data.data_leech()
    _mapdark = folium.Map(location=[df['latitude'][0], df['longitude'][0]],zoom_start=6,attributionControl=False,tiles='cartodbdark_matter')
    for index,row in df.iterrows():
        folium.Circle(
          location=[row['latitude'], row['longitude']],
        #   popup=str(row['sog'])+' kn',
          weight=1,
          radius=5,
          fill_color='Yellow',
          color='Blue',
        #   fill_opacity=row['sog']*0.05,
        ).add_to(_mapdark)
    # folium.TileLayer('cartodbdark_matter').add_to(_mapdark) # Sets Tile Theme to (Dark Theme)
    return _mapdark._repr_html_()

@app.route('/test', methods=['GET','POST'])
def test():
    messages = 'mapdark'
    return render_template('printer/menu_map.html',messages=messages)

@app.route('/desc', methods=['GET','POST'])
def desc():
    return render_template('printer/my.html')