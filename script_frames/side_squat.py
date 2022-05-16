#! usr/bin/env python3

# !pip install mediapipe opencv-python

from distutils import dist
import cv2
from matplotlib.text import Text
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def init_metrics(): ###criteria which is hip to ground vertical distance to be the lowest + hips, shoulder, arms , ankle
    metrics = {
        'hip_to_ankle_dist' : 10e99,
        'crit_1' : {
            'back_leg_angle' : 0 
        },
        'crit_2' : {
            'back_arm_angle' : 180
        }
    }

    return metrics

class sideLandmarkIdentifier():
    def __init__(self, landmarks):
        self.landmarks = landmarks

    def frame_criteria_1_2(self, frame, hip_to_ankle_dist, back_leg_angle,back_arm_angle):
        return frame, hip_to_ankle_dist, back_leg_angle,back_arm_angle
    # def frame_criteria_2(self, frame, back_arm_angle):
    #     return frame, back_arm_angle

# if __name__ == '__main__':
#     frame_config = 'side'
#     cap = cv2.VideoCapture('Vid/side-running.mp4')

#     debug = True
#     # Setup mediapipe instance
#     with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
#         while cap.isOpened():
#             ret, frame = cap.read()
#             try:
#                 # Recolor image to RGB
#                 image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#                 image.flags.writeable = False

#                 # Make detection
#                 results = pose.process(image)

#                 # Recolor back to BGR
#                 image.flags.writeable = True
#                 image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
#             except:
#                 cv2.imwrite('frame_criteria_1.png', frame_to_save_1)
#                 cv2.imwrite('frame_criteria_2.png', frame_to_save_2)
#                 print(
#                     f'front knee angle : {C1_front_knee_angle}, hip angle: {C1_hip_angle}')
#                 print(
#                     f'Ankle height : {C2_ankle_height}, Ankle-to-Hip distance: {C2_ankle_hip_distance}')
#                 break
#             # Extract landmarks
#             try:
#                 landmarks = results.pose_landmarks.landmark
#                 LandmarkIdentifier = sideLandmarkIdentifier(landmarks)

#                 # LEFT LEG
#                 # Get left leg coordinates
#                 left_hip, left_knee, left_ankle = LandmarkIdentifier.left_leg_landmarks()
#                 # Calculate angle
#                 left_leg_angle = LandmarkIdentifier.calculate_angle(
#                     left_hip, left_knee, left_ankle)
#                 # Visualise angle
#                 LandmarkIdentifier.showText(
#                     left_leg_angle, left_knee, image, 'left leg', debug)

#                 # RIGHT LEG
#                 # Get right leg coordinates
#                 right_hip, right_knee, right_ankle = LandmarkIdentifier.right_leg_landmarks()
#                 # Calculate angle
#                 right_leg_angle = LandmarkIdentifier.calculate_angle(
#                     right_hip, right_knee, right_ankle)
#                 # Visualise angle
#                 LandmarkIdentifier.showText(
#                     right_leg_angle, right_knee, image, 'right leg', debug)

#                 # LEFT HIP
#                 # Get left hip coordinates
#                 left_shoulder, left_hip, left_knee = LandmarkIdentifier.left_hip_landmarks()
#                 # Calculate angle
#                 left_hip_angle = LandmarkIdentifier.calculate_angle(
#                     left_shoulder, left_hip, left_knee)
#                 # Visualise angle
#                 LandmarkIdentifier.showText(
#                     left_hip_angle, left_hip, image, 'left hip', debug)

#                 # RIGHT HIP
#                 # Get right hip coordinates
#                 right_shoulder, right_hip, right_knee = LandmarkIdentifier.right_hip_landmarks()
#                 # Calculate angle
#                 right_hip_angle = LandmarkIdentifier.calculate_angle(
#                     right_shoulder, right_hip, right_knee)

#                 # Visualise angle
#                 LandmarkIdentifier.showText(
#                     right_hip_angle, right_hip, image, 'right hip', debug)

#                 right_dist = LandmarkIdentifier.calculate_distance(
#                     right_hip, right_ankle, image, debug)
#                 LandmarkIdentifier.showText(
#                     right_dist, right_ankle, image, 'right distance (hip and ankle)', debug)

#                 left_dist = LandmarkIdentifier.calculate_distance(
#                     left_hip, left_ankle, image, debug)
#                 LandmarkIdentifier.showText(
#                     left_dist, left_ankle, image, 'left distance (hip and ankle)', debug)

#                 # SIDE
#                 if right_leg_angle > back_knee_angle:
#                     frame_to_save_1, back_knee_angle, C1_front_knee_angle, C1_hip_angle = LandmarkIdentifier.frame_criteria_1(
#                         frame, right_leg_angle, left_leg_angle, right_hip_angle)
#                 # second frame (side)
#                 if right_ankle[1] < ankle_height:
#                     frame_to_save_2, C2_ankle_height, C2_ankle_hip_distance = LandmarkIdentifier.frame_criteria_2(
#                         frame, right_ankle[1], right_dist)

#                 except:
#                 pass

#             # Render detections
#             # mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
#             #                           mp_drawing.DrawingSpec(
#             #                               color=(245, 117, 66), thickness=2, circle_radius=2),
#             #                           mp_drawing.DrawingSpec(
#             #                               color=(245, 66, 230), thickness=2, circle_radius=2)
#                 #   )

#             cv2.imshow('Mediapipe Feed - side frame', image)

#             if cv2.waitKey(10) & 0xFF == ord('q'):
#                 break

#         cap.release()
#         cv2.destroyAllWindows()

#     # cv2.imwrite(frame_to_save_2, 'frame_criteria_2.png')
