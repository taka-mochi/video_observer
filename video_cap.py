import cv2
import time
import dropbox
from dropbox.files import WriteMode
import sys
from datetime import datetime

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("python %s [ACCESS_TOKEN_FILE] [SAVE_FNAME]" % (sys.argv[1],))
        sys.exit(0)

    access_token = None
    save_fname = sys.argv[2]
    with open(sys.argv[1]) as fr:
        access_token = fr.readline().strip()

    dbx = dropbox.Dropbox(access_token)
    dbx.users_get_current_account()
        
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

    print("start to capture loop")
    while True:
        ret, frame = cap.read()
        if ret and frame is not None:
            updated_time = datetime.now()
            print(str(frame.shape) + ":" + str(updated_time))
            cv2.putText(frame, str(updated_time), (10,20), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,255))
            cv2.imwrite(save_fname, frame)
            with open(save_fname, "rb") as fr:
                dbx.files_upload(fr.read(), '/' + save_fname, mode=WriteMode('overwrite', None))
        else:
            print("failed to capture: " + str(datetime.now()))
            

        time.sleep(60*15)
