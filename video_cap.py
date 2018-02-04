import cv2
import time
import dropbox
from dropbox.files import WriteMode
import sys
from datetime import datetime

def determin_onoff(single_channel_img, threshold, rate):
    thed = cv2.threshold(single_channel_img, threshold, 255, cv2.THRESH_BINARY)[1]

    nonzero_areas = thed.nonzero()
    nonzero_area_count = len(nonzero_areas[0])

    print(nonzero_area_count, thed.shape[0]*thed.shape[1])
    return nonzero_area_count * 1.0 / (thed.shape[0]*thed.shape[1]) >= rate

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("python %s [ACCESS_TOKEN_FILE] [SAVE_FNAME] [KOTATSU_ON_ACCESS] [KOTATSU_OFF_ACCESS]" % (sys.argv[1],))
        sys.exit(0)

    access_token = None
    save_fname = sys.argv[2]
    with open(sys.argv[1]) as fr:
        access_token = fr.readline().strip()

    # open Dropbox instance
    dbx = dropbox.Dropbox(access_token)
    dbx.users_get_current_account()

    # try open VideoCapture 
    cap = cv2.VideoCapture(-1)
    while True:
        print("try to capture...")
        ret, frame = cap.read()
        if frame is not None:
            print(frame.shape)
        if ret and frame is not None and frame.shape[0] != 0:
            break
        time.sleep(10)
        cap = cv2.VideoCapture(-1)

    prev_on_state = None

    print("start to capture loop")
    while True:
        ret, frame = cap.read()
        if ret and frame is not None:
            updated_time = datetime.now()

            # determine kotatsu is on/off (not good work)
            rchannel = frame[:,:,2]
            is_on = determin_onoff(rchannel, 80, 0.02)
            print(str(frame.shape) + ":" + str(updated_time) + ":is_on = " + str(is_on))
            # write updated time to the image
            cv2.putText(frame, str(updated_time), (10,20), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,255))
            # save image
            cv2.imwrite(save_fname, frame)

            # upload to Dropbox
            with open(save_fname, "rb") as fr:
                dbx.files_upload(fr.read(), '/' + save_fname, mode=WriteMode('overwrite', None))

            prev_on_state = is_on
        else:
            print("failed to capture: " + str(datetime.now()))
            

        time.sleep(60*15)
