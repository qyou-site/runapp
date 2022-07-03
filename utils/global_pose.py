import os
from re import L
import pandas as pd
import mediapipe as mp
import numpy as np
import cv2
from datetime import datetime
import gspread

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

class UtilsGen():
    def __init__(self, landmarks, height):
        self.landmarks = landmarks
        self.height = height
    
    def calculate_angle(self, a, b, c):  # global utils
        a = np.array(a)  # First
        b = np.array(b)  # Mid
        c = np.array(c)  # End

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
            np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    def calculate_distance(self, a, b, img, debug):  # global utils
        width = img.shape[1]
        height = img.shape[0]
        x1 = a[1] * width
        y1 = a[0] * height
        x2 = b[1] * width
        y2 = b[0] * height

        dist = ((x1-x2)**2+(y1-y2)**2)**0.5

        
        # if debug:
        #     cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)),
        #              (255, 0, 0), thickness=1)
        return dist

    def draw_line(self, point1, point2, img): 
        width = img.shape[1]
        height = img.shape[0]
        y1 = point1[1] * height
        x1 = point1[0] * width
        y2 = point2[1] * height
        x2 = point2[0] * width
        # x1 = point1[1] * width
        # y1 = point1[0] * height
        # x2 = point2[1] * width
        # y2 = point2[0] * height

        cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)),
                    (0, 255, 0), thickness=1)
        return img

    def showText(self, metric, point, image, text, debug):  # global utils
        if debug:
            if type(metric) != list:
                metric = str(round(metric,2))
            cv2.putText(image, f'{text}: {metric}',
                        tuple(np.multiply(
                            point, [image.shape[1], image.shape[0]]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0,
                                                      255, 0), 1, cv2.LINE_AA
                        )
        return image

    def greater_less_frame(self, landmark_coor):
        if landmark_coor[0] < 0 or landmark_coor[0] > 1:
            return 0
        if landmark_coor[1] < 0 or landmark_coor[1] > 1:
            return 0
        return 1

    def capture_frame_critera(self, *args):
        for coor in args:
            flag = self.greater_less_frame(coor)
            if flag == 0:
                break
        return flag

    def return_results(self, metrics, dict_to_save, frame):
        for key, value in dict_to_save.items():
            cv2.imwrite(os.path.join('app','static',frame,str(key)+'.png'), value)
# 'static'+frame+'/'+str(key)+'
        for key, value in metrics.items():
            print(f'{key} : {value}')

    def left_arm_landmarks(self):
        left_shoulder = [self.landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         self.landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        left_elbow = [self.landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                      self.landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        left_wrist = [self.landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                      self.landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

        return left_shoulder, left_elbow, left_wrist

    def right_arm_landmarks(self):
        right_shoulder = [self.landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          self.landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        right_elbow = [self.landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                       self.landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        right_wrist = [self.landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                       self.landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

        return right_shoulder, right_elbow, right_wrist

    def left_leg_landmarks(self):
        left_hip = [self.landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    self.landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        left_knee = [self.landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                     self.landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        left_ankle = [self.landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                      self.landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

        return left_hip, left_knee, left_ankle

    def right_leg_landmarks(self):
        right_hip = [self.landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                     self.landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        right_knee = [self.landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                      self.landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        right_ankle = [self.landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                       self.landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

        return right_hip, right_knee, right_ankle

    def left_hip_landmarks(self):
        left_shoulder = [self.landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         self.landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        left_hip = [self.landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    self.landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        left_knee = [self.landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                     self.landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]

        return left_shoulder, left_hip, left_knee

    def right_hip_landmarks(self):
        right_shoulder = [self.landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          self.landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        right_hip = [self.landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                     self.landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        right_knee = [self.landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                      self.landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]

        return right_shoulder, right_hip, right_knee

    def right_foot_landmarks(self):
        right_ankle = [self.landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                          self.landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
        right_heel = [self.landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].x,
                     self.landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].y]
        right_foot_index = [self.landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].x,
                      self.landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].y]

        return right_ankle, right_heel, right_foot_index

    def left_foot_landmarks(self):
        left_ankle = [self.landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                          self.landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        left_heel = [self.landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].x,
                     self.landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].y]
        left_foot_index = [self.landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x,
                      self.landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y]

        return left_ankle, left_heel, left_foot_index

    def capture_metadata(self, video_type, filename, metrics, frame_angle, side_direction):
        date = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
      
        sheet_id = '1YhmeuynXcs9Bo-Sl26HxsIkkrAbHdPMClxFh_nYVPvk'
        sa = gspread.service_account(filename="newagent-pss9-9047ed9cb1b8.json")
        sh = sa.open_by_url('https://docs.google.com/spreadsheets/d/1YhmeuynXcs9Bo-Sl26HxsIkkrAbHdPMClxFh_nYVPvk')
       
        main_sheet = 'metadata'
        url_main = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={main_sheet}'
        
        running_sheet = 'running'
        url_run = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={running_sheet}'

        squat_sheet = 'squat'
        url_sqt = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={squat_sheet}'

        try:
            df = pd.read_csv(url_main)
        except pd.errors.EmptyDataError as e:
            df = pd.DataFrame()
        index = len(df.index)
        df = df.dropna(axis=1,how='all')
        
        df.at[index,'date'] = date
        df.at[index,'filename'] = str(filename)+".png"
        df.at[index,'video_type'] = video_type
        df.at[index,'height'] = self.height
        df.at[index,'frame'] = frame_angle
        df.at[index,'side_direction'] = side_direction
        for metric in metrics:
            df.at[index, metric] = round(metrics[metric],2)
        df = df.fillna('')
        main_wks = sh.worksheet('metadata')
        main_wks.update([df.columns.values.tolist()] + df.values.tolist())

        if video_type == 'running':
            try:
                df = pd.read_csv(url_run)
            except pd.errors.EmptyDataError as e:
                df = pd.DataFrame()
            index = len(df.index)
            df = df.dropna(axis=1,how='all')
            
            df.at[index,'date'] = date
            df.at[index,'filename'] = str(filename)+".png"
            df.at[index,'video_type'] = video_type
            df.at[index,'height'] = self.height
            df.at[index,'frame'] = frame_angle
            df.at[index,'side_direction'] = side_direction
            for metric in metrics:
                df.at[index, metric] = round(metrics[metric],2)
            df = df.fillna('')
            run_wks = sh.worksheet('running')
            run_wks.update([df.columns.values.tolist()] + df.values.tolist())
        elif video_type == 'squat':
            try:
                df = pd.read_csv(url_sqt)
            except pd.errors.EmptyDataError as e:
                df = pd.DataFrame()
            index = len(df.index)
            df = df.dropna(axis=1,how='all')
            
            df.at[index,'date'] = date
            df.at[index,'filename'] = str(filename)+".png"
            df.at[index,'video_type'] = video_type
            df.at[index,'height'] = self.height
            df.at[index,'frame'] = frame_angle
            df.at[index,'side_direction'] = side_direction
            for metric in metrics:
                df.at[index, metric] = round(metrics[metric],2)
            df = df.fillna('')
            squat_wks = sh.worksheet('squat')
            squat_wks.update([df.columns.values.tolist()] + df.values.tolist())