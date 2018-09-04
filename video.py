import cv2
import os
import numpy as np
import glob


def convert_frames_to_video(pathIn, pathOut, fps, extension='.jpg', size=(1920,1920)):
    """
    Converts images in `pathIn` with the `extension` to a video in `pathOut`.

    Args:
        pathIn: path of frames
        pathOut: path of video
        fps: frames per second
    """
    frame_array = []
    files = sorted(glob.glob(os.path.join(pathIn, ('*' + extension))))

    out = cv2.VideoWriter(pathOut, cv2.VideoWriter_fourcc(*'DIVX'), fps, size)

    for i in range(len(files)):
        filename = files[i]
        # reading each files
        img = cv2.imread(filename)
        print(filename)
        # writing to a image array
        out.write(img)

    out.release()


def main():
    pathIn = './data/img/20180826_WKM2/'
    pathOut = './video.avi'
    fps = 12.0
    convert_frames_to_video(pathIn, pathOut, fps)


if __name__ == "__main__":
    main()

