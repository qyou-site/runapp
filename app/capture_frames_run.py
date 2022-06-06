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
from script_frames import front, side, back

class frameCaptureRun():
    def __init__(self, frame_angle, side_direction, debug):
        self.frame_angle = frame_angle
        self.debug = debug
        self.side_direction = side_direction

    def init_metrics(self):
        if self.frame_angle == 'side':
            self.metrics = side.init_metrics()
        elif self.frame_angle == 'front':
            self.metrics = front.init_metrics()
        elif self.frame_angle == 'back':
            self.metrics = back.init_metrics()

    def run(self, video):
        # Setup mediapipe instance
        FRAME_RATE = 20
        FPS = 20
        SHRINK_RATIO = 0.25
        mp_drawing = mp.solutions.drawing_utils
        mp_pose = mp.solutions.pose
        cap = cv2.VideoCapture(video)
        # cap.set(5,FPS)
        # cap.set(7,FRAME_RATE)

        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
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
                    image.flags.writeable = False

                    # Make detection
                    results = pose.process(image)

                    # Recolor back to BGR
                    image.flags.writeable = True
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                except:
                    break
                # Extract landmarks
                try:
                    landmarks = results.pose_landmarks.landmark
                    PoseUtils = UtilsGen(landmarks)
                    # if else statement
                    if self.frame_angle == 'side':
                        LandmarkIdentifier = side.sideLandmarkIdentifier(
                            landmarks)
                    elif self.frame_angle == 'front':
                        LandmarkIdentifier = front.frontLandmarkIdentifier(
                            landmarks)
                    elif self.frame_angle == 'back':
                        LandmarkIdentifier = back.backLandmarkIdentifier(landmarks)

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

                    # grab calculated metrics (method)
                    if self.frame_angle == 'side':
                        flag = PoseUtils.capture_frame_critera(right_ankle, right_knee, right_hip, left_ankle, left_knee, left_hip, left_shoulder, right_shoulder)
                        if self.side_direction == 'right':
                            right_dist = PoseUtils.calculate_distance(
                                right_hip, right_ankle, image, self.debug)
                            PoseUtils.showText(
                                right_dist, right_ankle, image, 'right distance (hip and ankle)', self.debug)
                            # first frame (side max back knee angle)
                            if right_leg_angle > self.metrics['crit_1']['back_knee_angle']:
                                frame_to_save_1, self.metrics['crit_1']['back_knee_angle'], self.metrics['crit_1']['front_knee_angle'], self.metrics['crit_1']['hip_angle'] = LandmarkIdentifier.frame_criteria_1(
                                    frame, right_leg_angle, left_leg_angle, right_hip_angle)
                            # second frame (side max ankle height)
                            if left_ankle[1] < self.metrics['crit_2']['ankle_height']:
                                frame_to_save_2, self.metrics['crit_2']['ankle_height'], self.metrics['crit_2']['Ankle-to-Hip distance'] = LandmarkIdentifier.frame_criteria_2(
                                    frame, left_ankle[1], right_dist)
                        
                        elif self.side_direction == 'left':
                            # left_dist = LandmarkIdentifier.calculate_distance(
                            #     left_hip, left_ankle, image, self.debug)
                            # LandmarkIdentifier.showText(
                            #     left_dist, left_ankle, image, 'left distance (hip and ankle)', self.debug)
                            left_dist = PoseUtils.calculate_distance(
                                left_hip, left_ankle, image, self.debug)
                            PoseUtils.showText(
                                left_dist, left_ankle, image, 'left distance (hip and ankle)', self.debug)
                            # first frame (side max back knee angle)
                            if left_leg_angle > self.metrics['crit_1']['back_knee_angle']:
                                frame_to_save_1, self.metrics['crit_1']['back_knee_angle'], self.metrics['crit_1']['ankle_height'], self.metrics['crit_1']['hip_angle'] = LandmarkIdentifier.frame_criteria_1(
                                    frame, left_leg_angle, left_leg_angle, left_hip_angle)
                            # second frame (side max ankle height)
                            if left_ankle[1] < self.metrics['crit_2']['ankle_height']:
                                frame_to_save_2, self.metrics['crit_2']['ankle_height'], self.metrics['crit_2']['Ankle-to-Hip distance'] = LandmarkIdentifier.frame_criteria_2(
                                    frame, left_ankle[1], left_dist)
                        if not flag:
                            break

                    elif self.frame_angle == 'front':
                        # FRONT
                        # Shoulders
                        if left_shoulder[1] < right_shoulder[1]:
                            shoulder_hor = [
                                left_shoulder[0], right_shoulder[1]]
                            shoulder_hor_angle = PoseUtils.calculate_angle(
                                left_shoulder, right_shoulder, shoulder_hor)
                            PoseUtils.showText(
                                shoulder_hor_angle, shoulder_hor, image, 'shoulder angle', self.debug)
                        else:
                            shoulder_hor = [
                                right_shoulder[0], left_shoulder[1]]
                            shoulder_hor_angle = PoseUtils.calculate_angle(
                                right_shoulder, left_shoulder, shoulder_hor)
                            PoseUtils.showText(
                                shoulder_hor_angle, shoulder_hor, image, 'shoulder angle', self.debug)
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
                        # Knees
                        if left_knee[1] < right_knee[1]:
                            knee_hor = [left_knee[0], right_knee[1]]
                            knee_hor_angle = PoseUtils.calculate_angle(
                                left_knee, right_knee, knee_hor)
                            PoseUtils.showText(
                                knee_hor_angle, knee_hor, image, 'knee angle', self.debug)
                        else:
                            knee_hor = [right_knee[0], left_knee[1]]
                            knee_hor_angle = PoseUtils.calculate_angle(
                                right_knee, left_knee, knee_hor)
                            PoseUtils.showText(
                                knee_hor_angle, knee_hor, image, 'knee angle', self.debug)

                        right_flag = PoseUtils.capture_frame_critera(right_knee, right_hip, right_shoulder)
                        left_flag = PoseUtils.capture_frame_critera(left_knee, left_hip, left_shoulder)

                        if not right_flag and not left_flag:
                            break

                        if right_ankle[1] < self.metrics['right']['ankle_height_right'] and right_flag:
                            frame_to_save_3, self.metrics['right']['ankle_height_right'], self.metrics['right']['shoulder_hor_angle_right'], self.metrics['right']['hip_hor_angle_right'], self.metrics['right']['knee_hor_angle_right'] = LandmarkIdentifier.frame_criteria_3(
                                frame, right_ankle[1], shoulder_hor_angle, hip_hor_angle, knee_hor_angle)

                        if left_ankle[1] < self.metrics['left']['ankle_height_left'] and left_flag:
                            frame_to_save_4, self.metrics['left']['ankle_height_left'], self.metrics['left']['shoulder_hor_angle_left'], self.metrics['left']['hip_hor_angle_left'], self.metrics['left']['knee_hor_angle_left'] = LandmarkIdentifier.frame_criteria_3(
                                frame, left_ankle[1], shoulder_hor_angle, hip_hor_angle, knee_hor_angle)


                    elif self.frame_angle == 'back':
                        right_ankle, right_heel, right_foot_index = PoseUtils.right_foot_landmarks()
                        right_feet_hor = [right_foot_index[0], right_heel[1]]
                        right_feet_angle = PoseUtils.calculate_angle(right_foot_index,right_heel,right_feet_hor)
                        PoseUtils.showText(right_feet_angle, right_foot_index, image, 'right feet angle', self.debug)

                        left_ankle, left_heel, left_foot_index = PoseUtils.left_foot_landmarks()
                        left_feet_hor = [left_foot_index[0], left_heel[1]]
                        left_feet_angle = PoseUtils.calculate_angle(left_foot_index,left_heel,left_feet_hor)
                        PoseUtils.showText(left_feet_angle, left_foot_index, image, 'left feet angle', self.debug)

                        right_flag = PoseUtils.capture_frame_critera(right_ankle,right_knee, right_hip)
                        left_flag = PoseUtils.capture_frame_critera(left_ankle, left_knee, left_hip)

                        if not right_flag and not left_flag:
                            break

                        if right_ankle[1] < self.metrics['right']['ankle_height_right'] and right_flag:
                            frame_to_save_5, self.metrics['right']['ankle_height_right'], self.metrics['right']['right_feet_angle'] = LandmarkIdentifier.frame_criteria_4(frame, right_ankle[1], right_feet_angle)

                        if left_ankle[1] < self.metrics['left']['ankle_height_left'] and left_flag:
                            frame_to_save_6, self.metrics['left']['ankle_height_left'], self.metrics['left']['left_feet_angle'] = LandmarkIdentifier.frame_criteria_4(frame, left_ankle[1], left_feet_angle)

                except:
                    pass

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
                    id_crit_1 : frame_to_save_1,
                    id_crit_2 : frame_to_save_2
                }
                PoseUtils.return_results(
                    self.metrics, to_save, 'side')
                PoseUtils.capture_metadata('running',id_crit_1,self.metrics['crit_1'], self.frame_angle)
                PoseUtils.capture_metadata('running',id_crit_2,self.metrics['crit_2'], self.frame_angle)

            elif self.frame_angle == 'front':
                to_save = {
                    id_crit_1 : frame_to_save_3,
                    id_crit_2 : frame_to_save_4
                }
                PoseUtils.return_results(
                    self.metrics, to_save, 'front')
                PoseUtils.capture_metadata('running',id_crit_1,self.metrics['right'], self.frame_angle)
                PoseUtils.capture_metadata('running',id_crit_2,self.metrics['left'], self.frame_angle)

            elif self.frame_angle == 'back':
                to_save = {
                    id_crit_1 : frame_to_save_5,
                    id_crit_2 : frame_to_save_6
                }
                PoseUtils.return_results(
                    self.metrics, to_save, 'back')
                PoseUtils.capture_metadata('running',id_crit_1,self.metrics['right'], self.frame_angle)
                PoseUtils.capture_metadata('running',id_crit_2,self.metrics['left'], self.frame_angle)

            print('Successfully uploaded and grabbed frames')
            # cv2.destroyAllWindows()


if __name__ == '__main__':
    with open('config.yml') as config_file:
        config = yaml.safe_load(config_file)
    frame_angle = config['params']['frame_angle']
    side_direction = config['params']['side']['direction']
    debug = config['params']['debug']
    testVid = config['params']['vid']

    FrameCapture = frameCaptureRun(frame_angle, side_direction, debug)
    FrameCapture.init_metrics()
    # print(testVid)
    FrameCapture.run(testVid)