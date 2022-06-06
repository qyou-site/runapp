
import numpy as np
from flask import Flask, Blueprint, jsonify, request, render_template, flash, redirect, url_for
import os
import pandas as pd
import random
from flask_login import login_required, current_user
from datetime import datetime
from .capture_frames_run import frameCaptureRun
from .capture_frames_squat import frameCaptureSquat
import cv2
import gspread

# sa = gspread.service_account(filename="newagent-pss9-9047ed9cb1b8.json")
# sh = sa.open_by_url('https://docs.google.com/spreadsheets/d/1YhmeuynXcs9Bo-Sl26HxsIkkrAbHdPMClxFh_nYVPvk')

# squat_wks = sh.worksheet("squat")
# running_wks = sh.worksheet("running")

views = Blueprint('views',__name__)

@views.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_vid():
    if request.method == 'GET':
        return render_template('upload.html',user=current_user)
    elif request.method == 'POST':
        if request.form['vid_type'] == 'squat':
            capture = frameCaptureSquat(request.form['frame'], request.form['side-direction'], False)
        elif request.form['vid_type'] == 'run':
            capture = frameCaptureRun(request.form['frame'], request.form['side-direction'], False)
        capture.init_metrics()
        vid_bytes = request.files['video'].read()
        with open('temp.mp4', "wb") as f:
            f.write(vid_bytes)
        capture.run('temp.mp4')
        os.remove('temp.mp4')
        message='Success!'
        sa = gspread.service_account(filename="newagent-pss9-9047ed9cb1b8.json")
        sh = sa.open_by_url('https://docs.google.com/spreadsheets/d/1YhmeuynXcs9Bo-Sl26HxsIkkrAbHdPMClxFh_nYVPvk')
        df = pd.read_csv('metadata.csv')

        dfr = df[df['video_type'] == 'running']
        dfr = dfr.dropna(axis=1,how='all')
        dfr = dfr.fillna('')
        run_wks = sh.worksheet('running')
        run_wks.update([dfr.columns.values.tolist()] + dfr.values.tolist())

        dfs = df[df['video_type'] == 'squat']
        dfs = dfs.dropna(axis=1,how='all')
        dfs = dfs.fillna('')
        squat_wks = sh.worksheet('squat')
        squat_wks.update([dfs.columns.values.tolist()] + dfs.values.tolist())
        
        return message,request.form 



@views.route('/', methods=['GET', 'POST'])
@login_required
def save_img():
    if request.method == 'GET':
        try:
            df_meta = pd.read_csv('metadata.csv')
        except FileNotFoundError as e:
            return "Please upload some videos for labelling - 127.0.0.1:5000/upload"
        index = random.randint(0,len(df_meta)-1) ###check whether its squat or running
        img_choice = df_meta.loc[index,'filename']
        img_frame = df_meta.loc[index,'frame']
        img = os.path.join(img_frame,img_choice)
        metadata = df_meta[df_meta['filename']==img_choice]
        metadata.dropna(inplace=True, axis=1)
        metadata = metadata.iloc[0]
        metadata = metadata.to_dict()
        print(metadata)
        return render_template('index.html', metadata = metadata, img_name=img, user=current_user)

    if request.method == 'POST':
        df_meta = pd.read_csv('metadata.csv')
        index = random.randint(0,len(df_meta)-1) ###check whether its squat or running
        img_choice = df_meta.loc[index,'filename']
        img_frame = df_meta.loc[index,'frame']
        img = os.path.join(img_frame,img_choice)

        metadata = df_meta[df_meta['filename']==img_choice]
        metadata.dropna(inplace=True, axis=1)
        metadata = metadata.iloc[0]
        metadata = metadata.to_dict()
        form = request.form

        ### Labels
        if 'labels.csv' in os.listdir():
            df_labels = pd.read_csv('labels.csv')
        else:
            df_labels = pd.DataFrame(columns=['img_name'])
        if form['img_name'] not in df_labels['img_name'].values:
            index = len(df_labels.index)
            df_labels.at[index,'video_type'] = form['video_type']
            for metric in form:
                df_labels.at[index, metric] = form[metric]
            df_labels.at[index,'score_int'] = form['score']
            df_labels.at[index,'no_labels'] = 1
            df_labels.at[index,'label_list'] = str([form['score']])
        else:
            index = df_labels[df_labels['img_name']==form['img_name']].index[0]
            df_labels.at[index,'video_type'] = form['video_type']
            df_labels.at[index,'img_name'] = form['img_name']
            label_list = eval(df_labels.at[index, 'label_list'])
            label_list.append(form['score'])
            df_labels.at[index, 'label_list'] = str(label_list)
            df_labels.at[index,'no_labels']+=1
            score = 0
            for single_score in eval(df_labels.at[index, 'label_list']):
                score+=int(single_score)
            df_labels.at[index,'score'] = score/int(df_labels.at[index,'no_labels'])
            df_labels.at[index,'score_int'] = round(df_labels.at[index,'score'])
        
        df_labels.at[index,'score'] = round(int(df_labels.at[index,'score']),2)
        df_labels.to_csv('labels.csv',index=False)


        ### Logs
        if 'label_log.csv' in os.listdir():
            df_logs = pd.read_csv('label_log.csv')
        else:
            df_logs = pd.DataFrame()

        index = len(df_labels.index)
        date = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
        user_id = current_user.id
        user_email = current_user.email
        username = current_user.first_name
        
        metadata_csv = pd.read_csv('metadata.csv')
        frame_angle = metadata_csv[metadata_csv['filename']==form['img_name'].split('/')[1]]['frame'].values[0]
        
        df_logs.at[index,'index'] = index
        df_logs.at[index,'date'] = date
        df_logs.at[index,'user_id'] = user_id
        df_logs.at[index,'user_email'] = user_email
        df_logs.at[index,'username'] = username
        df_logs.at[index,'image_name'] = form['img_name']
        df_logs.at[index,'frame_angle'] = frame_angle
        df_logs.at[index,'score'] = form['score']

        df_logs.to_csv('label_log.csv',index=False)

        ### put into googlesheets
        sa = gspread.service_account(filename="newagent-pss9-9047ed9cb1b8.json")
        sh = sa.open_by_url('https://docs.google.com/spreadsheets/d/1YhmeuynXcs9Bo-Sl26HxsIkkrAbHdPMClxFh_nYVPvk')

        df_label = pd.read_csv('labels.csv')
        labels_wks = sh.worksheet('labels')
        labels_wks.update([df_label.columns.values.tolist()] + df_label.values.tolist())

        df_log = pd.read_csv('label_log.csv')
        logs_wks = sh.worksheet('labels_log')
        logs_wks.update([df_log.columns.values.tolist()] + df_log.values.tolist())
# worksheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
        return render_template('index.html', metadata = metadata, img_name=img, user=current_user)
