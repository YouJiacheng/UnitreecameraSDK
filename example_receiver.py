import numpy as np
import cv2
from tqdm import tqdm
import dt_apriltags
from contextlib import suppress

IMG_SIZE = (464, 400)
TAG_SIZE = 0.15

# Given corners of a tag, return whether it is close to a rectangle
def is_near_rectangle(tag):
    # Calculate the length of each side
    corners = tag.corners
    side_lengths = []
    for i in range(4):
        side_lengths.append(np.linalg.norm(corners[i] - corners[(i + 1) % 4]))
    
    # Check if the lengths are approximately equal
    for i in range(4):
        if abs(side_lengths[i] - side_lengths[(i + 1) % 4]) > 50:
            print(f"{tag.tag_id} Not a rectangle")
            return False
    return True

def get_heading_vector(tag):
    # Get the heading vector of the tag using homography matrix
    # The heading vector is the vector from the center of the tag to upper of the tag
    # The heading vector is in the camera frame
    upper_center = np.array([0, -1, 1]).reshape(3, 1)
    upper_center_pro = np.matmul(tag.homography, upper_center).reshape(-1)
    upper_center_pro = upper_center_pro / upper_center_pro[2]
    upper_center_pro = upper_center_pro[:2]
    heading_vector = upper_center_pro - tag.center
    return heading_vector

def get_y_shift(tag):
    # Get the y_shift of the tag using homography matrix
    # Project the center back to the tag plane
    img_center = np.array([IMG_SIZE[0] / 2, IMG_SIZE[1] / 2, 1]).reshape(3, 1)
    inverse_homography = np.linalg.inv(tag.homography)
    img_center_pro = np.matmul(inverse_homography, img_center).reshape(-1)
    img_center_pro = img_center_pro / img_center_pro[2]
    img_center_pro = img_center_pro[:2]
    y_shift = img_center_pro[0] / 2. * TAG_SIZE
    return y_shift


cap = cv2.VideoCapture(
    "udpsrc address=192.168.123.15 port=9201 "
    "! application/x-rtp,media=video,encoding-name=H264 "
    "! rtph264depay ! h264parse ! omxh264dec ! videoconvert ! appsink"
)


# Write a video
import datetime
outname = 'test_' + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + '.mp4'
writer = cv2.VideoWriter(outname, cv2.VideoWriter_fourcc(*'mp4v'), 30, (464,400))

detector = dt_apriltags.Detector(families='tag16h5')

with tqdm() as bar, suppress(KeyboardInterrupt):
    while True:
        rv, image = cap.read()
        if not rv:
            continue
        rv, arr = cv2.imencode('.png', image)
        assert rv
        # Gray scale
        img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Detect tags
        tags = detector.detect(img)
        tags = [tag for tag in tags if is_near_rectangle(tag)]
        # Draw tags
        color_img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        for tag in tags:
            if tag.decision_margin < 50:
                continue
            for idx in range(len(tag.corners)):
                cv2.line(color_img, tuple(tag.corners[idx-1, :].astype(int)), tuple(tag.corners[idx, :].astype(int)), (0, 255, 0))

            cv2.putText(color_img, str(tag.tag_id),
                        org=(tag.corners[0, 0].astype(int)+10,tag.corners[0, 1].astype(int)+10),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.8,
                        color=(0, 0, 255))
            # show the heading vector as an arrow
            heading_vector = get_heading_vector(tag)
            center = tag.center.astype(int)
            end = heading_vector.astype(int) + center
            cv2.arrowedLine(color_img, tuple(center), tuple(end), (255, 0, 0), 2)
            # print the y_shift at the lower left corner of the frame
            y_shift = get_y_shift(tag)
            # put the y_shift on the image, need to be high resolution
            cv2.putText(color_img, f'y_shift: {y_shift:.3f}',
                        org=(10, 390),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1.8,
                        color=(0, 0, 255))
        # Draw the central vertical line and the central horizontal line
        cv2.line(color_img, (232, 0), (232, 400), (0, 0, 255))
        cv2.line(color_img, (0, 200), (464, 200), (0, 0, 255))

        writer.write(color_img)
        bar.update()

writer.release()