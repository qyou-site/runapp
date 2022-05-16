#! usr/bin/env python3

# !pip install mediapipe opencv-python

from distutils import dist
import cv2
from matplotlib.text import Text
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def init_metrics():
    metrics = {
        'right': {
            'ankle_height_right': 10e99,
            'shoulder_hor_angle_right': 0,
            'hip_hor_angle_right': 0,
            'knee_hor_angle_right': 0,
        },
        'left': {
            'ankle_height_left': 10e99,
            'shoulder_hor_angle_left': 0,
            'hip_hor_angle_left': 0,
            'knee_hor_angle_left': 0

        }
    }

    return metrics


class frontLandmarkIdentifier():
    def __init__(self, landmarks):
        self.landmarks = landmarks

    def frame_criteria_3(self, frame, ankle_height, shoulder_hor_angle, hip_hor_angle, knee_hor_angle):
        return frame, ankle_height, shoulder_hor_angle, hip_hor_angle, knee_hor_angle


if __name__ == '__main__':
    cap = cv2.VideoCapture('Vid/front-running.mp4')

    debug = True
    # Setup mediapipe instance
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            try:
                # Recolor image to RGB
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                # Make detection
                results = pose.process(image)

                # Recolor back to BGR
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            except:
                try:
                    # LandmarkIdentifier.return_results(LandmarkIdentifier.)
                    pass
                except:
                    print('Landmark object not defined yet')
                    pass
                cv2.imwrite('frame_criteria_3_right.png', frame_to_save_3)
                cv2.imwrite('frame_criteria_3_left.png', frame_to_save_4)
                print(
                    f'right knee angle: {front_right_knee_angle}, shoulder horizontal_angle: {shoulder_hor_angle_right}, hip horizontal_angle: {hip_hor_angle_right}, knee horizontal_angle: {knee_hor_angle_right}')
                print(
                    f'left knee angle: {front_left_knee_angle}, shoulder horizontal_angle: {shoulder_hor_angle_left}, hip horizontal_angle: {hip_hor_angle_left}, knee horizontal_angle: {knee_hor_angle_left}')
                break
            # Extract landmarks
            try:
                landmarks = results.pose_landmarks.landmark
                LandmarkIdentifier = frontLandmarkIdentifier(landmarks)

                # # if frame_config == 'front':
                # # LEFT ARM
                # # Get left arm coordinates
                # left_shoulder, left_elbow, left_wrist = LandmarkIdentifier.left_arm_landmarks()
                # # Calculate angle
                # left_arm_angle = LandmarkIdentifier.calculate_angle(
                #     left_shoulder, left_elbow, left_wrist)
                # # Visualise angle
                # LandmarkIdentifier.showText(
                #     left_arm_angle, left_elbow, image, 'left arm', debug)

                # # RIGHT ARM
                # # Get right arm coordinates
                # right_shoulder, right_elbow, right_wrist = LandmarkIdentifier.right_arm_landmarks()
                # # Calculate angle
                # right_arm_angle = LandmarkIdentifier.calculate_angle(
                #     right_shoulder, right_elbow, right_wrist)
                # # Visualise angle
                # LandmarkIdentifier.showText(
                #     right_arm_angle, right_elbow, image, 'right arm', debug)

                # LEFT LEG
                # Get left leg coordinates
                left_hip, left_knee, left_ankle = LandmarkIdentifier.left_leg_landmarks()
                # Calculate angle
                left_leg_angle = LandmarkIdentifier.calculate_angle(
                    left_hip, left_knee, left_ankle)
                # Visualise angle
                LandmarkIdentifier.showText(
                    left_leg_angle, left_knee, image, 'left leg', True)

                # RIGHT LEG
                # Get right leg coordinates
                right_hip, right_knee, right_ankle = LandmarkIdentifier.right_leg_landmarks()
                # Calculate angle
                right_leg_angle = LandmarkIdentifier.calculate_angle(
                    right_hip, right_knee, right_ankle)
                # Visualise angle
                LandmarkIdentifier.showText(
                    right_leg_angle, right_knee, image, 'right leg', True)

                # LEFT HIP
                # Get left hip coordinates
                left_shoulder, left_hip, left_knee = LandmarkIdentifier.left_hip_landmarks()
                # Calculate angle
                left_hip_angle = LandmarkIdentifier.calculate_angle(
                    left_shoulder, left_hip, left_knee)
                # Visualise angle
                LandmarkIdentifier.showText(
                    left_hip_angle, left_hip, image, 'left hip', debug)

                # RIGHT HIP
                # Get right hip coordinates
                right_shoulder, right_hip, right_knee = LandmarkIdentifier.right_hip_landmarks()
                # Calculate angle
                right_hip_angle = LandmarkIdentifier.calculate_angle(
                    right_shoulder, right_hip, right_knee)
                # Visualise angle
                LandmarkIdentifier.showText(
                    right_hip_angle, right_hip, image, 'right hip', debug)

                # FRONT
                # Shoulders
                if left_shoulder[1] < right_shoulder[1]:
                    shoulder_hor = [left_shoulder[0], right_shoulder[1]]
                    shoulder_hor_angle = LandmarkIdentifier.calculate_angle(
                        left_shoulder, right_shoulder, shoulder_hor)
                    LandmarkIdentifier.showText(
                        shoulder_hor_angle, shoulder_hor, image, 'shoulder angle', True)
                else:
                    shoulder_hor = [right_shoulder[0], left_shoulder[1]]
                    shoulder_hor_angle = LandmarkIdentifier.calculate_angle(
                        right_shoulder, left_shoulder, shoulder_hor)
                    LandmarkIdentifier.showText(
                        shoulder_hor_angle, shoulder_hor, image, 'shoulder angle', True)
                # Hips
                if left_hip[1] < right_hip[1]:
                    hip_hor = [left_hip[0], right_hip[1]]
                    hip_hor_angle = LandmarkIdentifier.calculate_angle(
                        left_hip, right_hip, hip_hor)
                    LandmarkIdentifier.showText(
                        hip_hor_angle, hip_hor, image, 'hip angle', True)
                else:
                    hip_hor = [right_hip[0], left_hip[1]]
                    hip_hor_angle = LandmarkIdentifier.calculate_angle(
                        right_hip, left_hip, hip_hor)
                    LandmarkIdentifier.showText(
                        hip_hor_angle, hip_hor, image, 'hip angle', True)
                # Knees
                if left_knee[1] < right_knee[1]:
                    knee_hor = [left_knee[0], right_knee[1]]
                    knee_hor_angle = LandmarkIdentifier.calculate_angle(
                        left_knee, right_knee, knee_hor)
                    LandmarkIdentifier.showText(
                        knee_hor_angle, knee_hor, image, 'knee angle', True)
                else:
                    knee_hor = [right_knee[0], left_knee[1]]
                    knee_hor_angle = LandmarkIdentifier.calculate_angle(
                        right_knee, left_knee, knee_hor)
                    LandmarkIdentifier.showText(
                        knee_hor_angle, knee_hor, image, 'knee angle', True)

                if right_leg_angle > front_right_knee_angle:
                    frame_to_save_3, front_right_knee_angle, shoulder_hor_angle_right, hip_hor_angle_right, knee_hor_angle_right = LandmarkIdentifier.frame_criteria_3(
                        frame, right_leg_angle, shoulder_hor_angle, hip_hor_angle, knee_hor_angle)

                if left_leg_angle > front_left_knee_angle:
                    frame_to_save_4, front_left_knee_angle, shoulder_hor_angle_left, hip_hor_angle_left, knee_hor_angle_left = LandmarkIdentifier.frame_criteria_3(
                        frame, left_leg_angle, shoulder_hor_angle, hip_hor_angle, knee_hor_angle)

            except:
                pass

            # Render detections
            # mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
            #                           mp_drawing.DrawingSpec(
            #                               color=(245, 117, 66), thickness=2, circle_radius=2),
            #                           mp_drawing.DrawingSpec(
            #                               color=(245, 66, 230), thickness=2, circle_radius=2)
                #   )

            cv2.imshow('Mediapipe Feed - front frame', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        # cv2.imwrite(frame_to_save_2, 'frame_criteria_2.png')
