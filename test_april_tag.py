import numpy as np
import cv2
import dt_apriltags
from pathlib import Path

IMG_SIZE = (464, 400)
TAG_SIZE = 0.16

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


img_fns = sorted(Path('./test_frames').glob('*.png'), key=lambda x: int(x.stem))

detector = dt_apriltags.Detector(families='tag16h5')
outpath = Path('./test_frames_out')
outpath.mkdir(exist_ok=True)

import tqdm
# output a video with the tags detected
writer = cv2.VideoWriter(str(outpath / 'test.mp4'), cv2.VideoWriter_fourcc(*'mp4v'), 30, (464,400))

for img_fn in tqdm.tqdm(img_fns):
    img = cv2.imread(str(img_fn), cv2.IMREAD_GRAYSCALE)
    tags = detector.detect(img)
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

    writer.write(color_img)

writer.release()

