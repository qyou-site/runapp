import uuid
import os
from distutils import dist
from re import L
import yaml
import cv2
import mediapipe as mp
import numpy as np
from matplotlib.text import Text
from utils.global_pose import UtilsGen
from script_frames import front_squat, side_squat, back_squat

class frameCaptureSquat():
    def __init__(self, frame_angle, side_direction, debug):
        self.frame_angle = frame_angle
        self.debug = debug
        self.side_direction = side_direction

    def init_metrics(self):
        if self.frame_angle == 'side':
            self.metrics = side_squat.init_metrics()
        elif self.frame_angle == 'front':
            self.metrics = front_squat.init_metrics()
        elif self.frame_angle == 'back':
            self.metrics = back_squat.init_metrics()

    def run(self, video):
        # Setup mediapipe instance
        FRAME_RATE = 5
        FPS = 5
        SHRINK_RATIO = 0.25
        mp_drawing = mp.solutions.drawing_utils
        mp_pose = mp.solutions.pose
        cap = cv2.VideoCapture(video)
        cap.set(5,FPS)
        cap.set(7,FRAME_RATE)


        with mp_pose.Pose(min_detection_confidence=0.1, min_tracking_confidence=0.1) as pose:
            frame_count = 0
            while cap.isOpened():
                frame_count +=1
                ret, frame = cap.read()
                if frame_count % 10000 == 0:
                    print(f'working at {frame_count} frames')
                try:
                    frame = cv2.resize(frame,None,fx=SHRINK_RATIO,fy=SHRINK_RATIO)
                    # Recolor image to RGB
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # print(image.shape)
                    # image = image[200:1000,500:2000]
                    image.flags.writeable = False

                    # Make detection
                    results = pose.process(image)
                    
                    # Recolor back to BGR
                    image.flags.writeable = True
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                except:
                    pass
                # Extract landmarks
                # try:
                # print(image.shape)
                if results.pose_landmarks == None:
                    print('None')
                    continue
                landmarks = results.pose_landmarks.landmark
                PoseUtils = UtilsGen(landmarks)
                # if else statement
                if self.frame_angle == 'side':
                    LandmarkIdentifier = side_squat.sideLandmarkIdentifier(
                        landmarks)
                elif self.frame_angle == 'front':
                    LandmarkIdentifier = front_squat.frontLandmarkIdentifier(
                        landmarks)
                elif self.frame_angle == 'back':
                    LandmarkIdentifier = back_squat.backLandmarkIdentifier(landmarks)

                # grab coordinates (method)
                # LEFT LEG
                # Get left leg coordinates
                left_hip, left_knee, left_ankle = PoseUtils.left_leg_landmarks()
                # Calculate angle
                left_leg_angle = PoseUtils.calculate_angle(
                    left_hip, left_knee, left_ankle)
                # Visualise angle
                PoseUtils.showText(
                    left_leg_angle, left_knee, image, 'left leg', self.debug)

                # RIGHT LEG
                # Get right leg coordinates
                right_hip, right_knee, right_ankle = PoseUtils.right_leg_landmarks()
                # Calculate angle
                right_leg_angle = PoseUtils.calculate_angle(
                    right_hip, right_knee, right_ankle)
                # Visualise angle
                PoseUtils.showText(
                    right_leg_angle, right_knee, image, 'right leg', self.debug)

                # LEFT HIP
                # Get left hip coordinates
                left_shoulder, left_hip, left_knee = PoseUtils.left_hip_landmarks()
                # Calculate angle
                left_hip_angle = PoseUtils.calculate_angle(
                    left_shoulder, left_hip, left_knee)
                # Visualise angle
                PoseUtils.showText(
                    left_hip_angle, left_hip, image, 'left hip', self.debug)

                # RIGHT HIP
                # Get right hip coordinates
                right_shoulder, right_hip, right_knee = PoseUtils.right_hip_landmarks()
                # Calculate angle
                right_hip_angle = PoseUtils.calculate_angle(
                    right_shoulder, right_hip, right_knee)
                # Visualise angle
                PoseUtils.showText(
                    right_hip_angle, right_hip, image, 'right hip', self.debug)

                # LEFT arm
                # Get left arm coordinates
                left_shoulder, left_elbow, left_wrist = PoseUtils.left_arm_landmarks()
                # Calculate angle
                left_arm_angle = PoseUtils.calculate_angle(
                    left_shoulder, left_elbow, left_wrist)
                # Visualise angle
                # PoseUtils.showText(
                #     left_arm_angle, left_elbow, image, 'left arm', self.debug)

                # RIGHT arm
                # Get right arm coordinates
                right_shoulder, right_elbow, right_wrist = PoseUtils.right_arm_landmarks()
                # Calculate angle
                right_arm_angle = PoseUtils.calculate_angle(
                    right_shoulder, right_elbow, right_wrist)
                # Visualise angle
                # PoseUtils.showText(
                #     right_hip_angle, right_hip, image, 'right hip', self.debug)


                # grab calculated metrics (method)
                if self.frame_angle == 'side':
                    flag = PoseUtils.capture_frame_critera(right_ankle, right_knee, right_hip, left_ankle, left_knee, left_hip, left_shoulder, right_shoulder)
                    if self.side_direction == 'right':
                        right_hip_to_ankle_dist = PoseUtils.calculate_distance(right_hip, right_ankle, image, self.debug)
                        ### to check whether they are parallel, get distance of one of them, then map it back to the other (e.g. get distance from hip to shoulders, 
                        ### map it back to ankle, then add the distance, and you have 3 points to calculate the angle - knee, ankle, mapped coor)
                        ### criteria 1
                        x_dist = abs(right_shoulder[0] - right_hip[0])
                        y_dist = abs(right_shoulder[1] - right_hip[1])
                        temp_coor_1 = [right_ankle[0]+x_dist,right_ankle[1]-y_dist]
                        back_leg_angle = PoseUtils.calculate_angle(right_knee, right_ankle, temp_coor_1)

                        ###criteria 2
                        temp_coor_2 = [right_shoulder[0]+x_dist,right_shoulder[1]-y_dist]
                        back_arm_angle = PoseUtils.calculate_angle(right_elbow,right_shoulder,temp_coor_2)

                        PoseUtils.showText(
                            temp_coor_1, temp_coor_1, image, 'temp coordinates crit 1', self.debug)
                        PoseUtils.showText(
                            temp_coor_2, temp_coor_2, image, 'temp coordinates crit 2', self.debug)
                        # frame (lowest hip to ankle distance)
                        if right_hip_to_ankle_dist < self.metrics['hip_to_ankle_dist']:
                            frame_to_save_1_2, self.metrics['hip_to_ankle_dist'], self.metrics['crit_1']['back_leg_angle'], self.metrics['crit_2']['back_arm_angle'] = LandmarkIdentifier.frame_criteria_1_2(
                                frame, right_hip_to_ankle_dist, back_leg_angle, back_arm_angle)
                            # frame_to_save_2, self.metrics['crit_2']['back_arm_angle'] = LandmarkIdentifier.frame_criteria_2(
                            #     frame, back_arm_angle)
                    
                    elif self.side_direction == 'left':
                        left_hip_to_ankle_dist = PoseUtils.calculate_distance(left_hip, left_ankle, image, self.debug)
                        ### to check whether they are parallel, get distance of one of them, then map it back to the other (e.g. get distance from hip to shoulders, 
                        ### map it back to ankle, then add the distance, and you have 3 points to calculate the angle - knee, ankle, mapped coor)
                        ### criteria 1
                        x_dist = abs(left_shoulder[0] - left_hip[0])
                        y_dist = abs(left_shoulder[1] - left_hip[1])
                        temp_coor_1 = [left_ankle[0]-x_dist,left_ankle[1]-y_dist]
                        back_leg_angle = PoseUtils.calculate_angle(left_knee, left_ankle, temp_coor_1)

                        ###criteria 2
                        temp_coor_2 = [left_shoulder[0]-x_dist,left_shoulder[1]-y_dist]
                        back_arm_angle = PoseUtils.calculate_angle(left_elbow,left_shoulder,temp_coor_2)

                        PoseUtils.showText(
                            temp_coor_1, temp_coor_1, image, 'temp coordinates crit 1', self.debug)
                        PoseUtils.showText(
                            temp_coor_2, temp_coor_2, image, 'temp coordinates crit 2', self.debug)
                        # frame (lowest hip to ankle distance)
                        if left_hip_to_ankle_dist < self.metrics['hip_to_ankle_dist']:
                            frame_to_save_1_2, self.metrics['hip_to_ankle_dist'], self.metrics['crit_1']['back_leg_angle'], self.metrics['crit_2']['back_arm_angle'] = LandmarkIdentifier.frame_criteria_1_2(
                                frame, left_hip_to_ankle_dist, back_leg_angle,back_arm_angle)
                            # frame_to_save_2, self.metrics['crit_2']['back_arm_angle'] = LandmarkIdentifier.frame_criteria_2(
                            #     frame, back_arm_angle)
                    if not flag:
                        break

                elif self.frame_angle == 'front':
                    right_hip_to_ankle_dist = PoseUtils.calculate_distance(right_hip, right_ankle, image, self.debug)
                    left_hip_to_ankle_dist = PoseUtils.calculate_distance(left_hip, left_ankle, image, self.debug)
                    hip_to_ankle_dist = (right_hip_to_ankle_dist+left_hip_to_ankle_dist)/2
                    # FRONT
                    # Knees
                    knee_to_knee_dist = PoseUtils.calculate_distance(left_knee,right_knee, image, self.debug)


                    # if left_shoulder[1] < right_shoulder[1]:
                    #     shoulder_hor = [
                    #         left_shoulder[0], right_shoulder[1]]
                    #     shoulder_hor_angle = PoseUtils.calculate_angle(
                    #         left_shoulder, right_shoulder, shoulder_hor)
                    #     PoseUtils.showText(
                    #         shoulder_hor_angle, shoulder_hor, image, 'shoulder angle', self.debug)
                    # else:
                    #     shoulder_hor = [
                    #         right_shoulder[0], left_shoulder[1]]
                    #     shoulder_hor_angle = PoseUtils.calculate_angle(
                    #         right_shoulder, left_shoulder, shoulder_hor)
                    #     PoseUtils.showText(
                    #         shoulder_hor_angle, shoulder_hor, image, 'shoulder angle', self.debug)
                    # # Hips
                    # if left_hip[1] < right_hip[1]:
                    #     hip_hor = [left_hip[0], right_hip[1]]
                    #     hip_hor_angle = PoseUtils.calculate_angle(
                    #         left_hip, right_hip, hip_hor)
                    #     PoseUtils.showText(
                    #         hip_hor_angle, hip_hor, image, 'hip angle', self.debug)
                    # else:
                    #     hip_hor = [right_hip[0], left_hip[1]]
                    #     hip_hor_angle = PoseUtils.calculate_angle(
                    #         right_hip, left_hip, hip_hor)
                    #     PoseUtils.showText(
                    #         hip_hor_angle, hip_hor, image, 'hip angle', self.debug)
                    # # Knees
                    # if left_knee[1] < right_knee[1]:
                    #     knee_hor = [left_knee[0], right_knee[1]]
                    #     knee_hor_angle = PoseUtils.calculate_angle(
                    #         left_knee, right_knee, knee_hor)
                    #     PoseUtils.showText(
                    #         knee_hor_angle, knee_hor, image, 'knee angle', self.debug)
                    # else:
                    #     knee_hor = [right_knee[0], left_knee[1]]
                    #     knee_hor_angle = PoseUtils.calculate_angle(
                    #         right_knee, left_knee, knee_hor)
                    #     PoseUtils.showText(
                    #         knee_hor_angle, knee_hor, image, 'knee angle', self.debug)

                    right_flag = PoseUtils.capture_frame_critera(right_knee, right_hip, right_ankle)
                    left_flag = PoseUtils.capture_frame_critera(left_knee, left_hip, left_ankle)

                    if not right_flag or not left_flag:
                        break

                    if hip_to_ankle_dist < self.metrics['hip_to_ankle_dist']:
                        frame_to_save_3, self.metrics['hip_to_ankle_dist'], self.metrics['knee_to_knee_dist'] = LandmarkIdentifier.frame_criteria_1(
                            frame, hip_to_ankle_dist, knee_to_knee_dist)

                elif self.frame_angle == 'back':
                    right_hip_to_ankle_dist = PoseUtils.calculate_distance(right_hip, right_ankle, image, self.debug)
                    left_hip_to_ankle_dist = PoseUtils.calculate_distance(left_hip, left_ankle, image, self.debug)
                    hip_to_ankle_dist = (right_hip_to_ankle_dist+left_hip_to_ankle_dist)/2

                    # Hips
                    if left_hip[1] < right_hip[1]:
                        hip_hor = [left_hip[0], right_hip[1]]
                        hip_hor_angle = PoseUtils.calculate_angle(
                            left_hip, right_hip, hip_hor)
                        PoseUtils.showText(
                            hip_hor_angle, hip_hor, image, 'hip angle', self.debug)
                    else:
                        hip_hor = [right_hip[0], left_hip[1]]
                        hip_hor_angle = PoseUtils.calculate_angle(
                            right_hip, left_hip, hip_hor)
                        PoseUtils.showText(
                            hip_hor_angle, hip_hor, image, 'hip angle', self.debug)

                    # right_ankle, right_heel, right_foot_index = PoseUtils.right_foot_landmarks()
                    # right_feet_hor = [right_foot_index[0], right_heel[1]]
                    # right_feet_angle = PoseUtils.calculate_angle(right_foot_index,right_heel,right_feet_hor)
                    # PoseUtils.showText(right_feet_angle, right_foot_index, image, 'right feet angle', self.debug)

                    # left_ankle, left_heel, left_foot_index = PoseUtils.left_foot_landmarks()
                    # left_feet_hor = [left_foot_index[0], left_heel[1]]
                    # left_feet_angle = PoseUtils.calculate_angle(left_foot_index,left_heel,left_feet_hor)
                    # PoseUtils.showText(left_feet_angle, left_foot_index, image, 'left feet angle', self.debug)

                    right_flag = PoseUtils.capture_frame_critera(right_ankle,right_knee, right_hip)
                    left_flag = PoseUtils.capture_frame_critera(left_ankle, left_knee, left_hip)

                    if not right_flag or not left_flag:
                        break

                    if hip_to_ankle_dist < self.metrics['hip_to_ankle_dist']:
                        frame_to_save_5, self.metrics['hip_to_ankle_dist'], self.metrics['left_right_hip_angle'] = LandmarkIdentifier.frame_criteria_4(frame, hip_to_ankle_dist,hip_hor_angle)

                    # if left_ankle[1] < self.metrics['left']['ankle_height_left'] and left_flag:
                    #     frame_to_save_6, self.metrics['left']['ankle_height_left'], self.metrics['left']['left_feet_angle'] = LandmarkIdentifier.frame_criteria_4(frame, left_ankle[1], left_feet_angle)

                # except:
                    # pass

                # Render detections
                # mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                #                           mp_drawing.DrawingSpec(
                #                               color=(245, 117, 66), thickness=2, circle_radius=2),
                #                           mp_drawing.DrawingSpec(
                #                               color=(245, 66, 230), thickness=2, circle_radius=2)
                #       )
                
                # cv2.namedWindow(f"Mediapipe Feed - {self.frame_angle} frame", cv2.WINDOW_NORMAL)
                # cv2.imshow(f'Mediapipe Feed - {self.frame_angle} frame', image)
                
                # if cv2.waitKey(10) & 0xFF == ord('q'):
                #     break

            cap.release()
            id_crit_1 = uuid.uuid4()
            id_crit_2 = uuid.uuid4()

            if self.frame_angle == 'side':
                to_save = {
                    id_crit_1 : frame_to_save_1_2,
                    # id_crit_2 : frame_to_save_2
                }
                metrics = {
                   'hip_to_ankle_dist': self.metrics['hip_to_ankle_dist'],
                   'back_leg_angle': self.metrics['crit_1']['back_leg_angle'],
                    'back_arm_angle': self.metrics['crit_2']['back_arm_angle']
                }
                print(metrics)
                PoseUtils.return_results(
                    self.metrics, to_save, 'side')
                PoseUtils.capture_metadata('squat',id_crit_1,metrics, self.frame_angle)
                # PoseUtils.capture_metadata(id_crit_2,self.metrics['crit_2'], self.frame_angle)

            elif self.frame_angle == 'front':
                to_save = {
                    id_crit_1 : frame_to_save_3,
                    # id_crit_2 : frame_to_save_4
                }
                PoseUtils.return_results(
                    self.metrics, to_save,'front')
                PoseUtils.capture_metadata('squat',id_crit_1,self.metrics, self.frame_angle)
                # PoseUtils.capture_metadata(id_crit_2,self.metrics['left'], self.frame_angle)

            elif self.frame_angle == 'back':
                to_save = {
                    id_crit_1 : frame_to_save_5,
                    # id_crit_2 : frame_to_save_6
                }
                PoseUtils.return_results(
                    self.metrics, to_save, 'back')
                PoseUtils.capture_metadata('squat',id_crit_1,self.metrics, self.frame_angle)
                # PoseUtils.capture_metadata(id_crit_2,self.metrics['left'], self.frame_angle)

            print('Successfully uploaded and grabbed frames')
            # cv2.destroyAllWindows()


if __name__ == '__main__':
    with open('config.yml') as config_file:
        config = yaml.safe_load(config_file)
    frame_angle = config['params']['frame_angle']
    side_direction = config['params']['side']['direction']
    debug = config['params']['debug']
    testVid = config['params']['vid']

    FrameCapture = frameCaptureSquat(frame_angle, side_direction, debug)
    FrameCapture.init_metrics()
    # print(testVid)
    FrameCapture.run(testVid)
