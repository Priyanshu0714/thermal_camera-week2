import re
import pandas as pd
import cv2
import pytesseract
import os
from datetime import datetime

# for extracting the first frames only and sending it to the backend
def first_frame(video_path):
    # for reading the first frame
    capture = cv2.VideoCapture(video_path)
    ret, frame = capture.read()
    if ret:
        os.makedirs("static/frames", exist_ok=True)
        frame_output_path = os.path.join("static", "frames", "firstframe.png")
        cv2.imwrite(frame_output_path, frame)
        return frame_output_path
    return None

# def process_video(video_path):
#     # Output Excel path
#     filename = f"VideoData_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
#     output_path = os.path.join("results", filename)

#     # Lists to store data
#     forehead, nose, l_cheek, r_cheek, chin = [], [], [], [], []

#     capture = cv2.VideoCapture(video_path)

#     fps = capture.get(cv2.CAP_PROP_FPS)
#     skip_frames = int(fps // 3)
#     frame_count = 0

#     while True:
#         isTrue, frame = capture.read()
#         if not isTrue:
#             break

#         if frame_count % skip_frames == 0:
#             # Convert to grayscale and threshold
#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#             _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

#             # OCR config
#             custom_config = r'--oem 3 --psm 6'
#             text = pytesseract.image_to_string(thresh, config=custom_config)

#             # Extract numbers
#             numbers = re.findall(r'\b\d+\.\d+|\b\d+', text)

#             try:
#                 # Ensure at least 5 values are found
#                 if len(numbers) >= 5:
#                     forehead.append(float(numbers[0]))
#                     nose.append(float(numbers[1]))
#                     l_cheek.append(float(numbers[2]))
#                     r_cheek.append(float(numbers[3]))
#                     chin.append(float(numbers[4]))
#             except:
#                 continue

#         frame_count += 1

#     capture.release()
#     cv2.destroyAllWindows()

#     # Create and export DataFrame
#     data = {
#         'Forehead': forehead,
#         'Nose': nose,
#         'Left Cheek': l_cheek,
#         'Right Cheek': r_cheek,
#         'Chin': chin
#     }
#     df = pd.DataFrame(data)
#     df.to_excel(output_path, index=False)
#     return output_path

def process_video(video_path ,region_coordinates):
    
    filename = f"VideoData_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    output_path = os.path.join("results", filename)

    capture = cv2.VideoCapture(video_path)
    fps = capture.get(cv2.CAP_PROP_FPS)
    skip_frames = int(fps // 3)
    frame_count = 0

    # One list per region
    region_texts = [[] for _ in range(len(region_coordinates))]

    while True:
        isTrue, frame = capture.read()
        if not isTrue:
            break

        if frame_count % skip_frames == 0:
            for i, region in enumerate(region_coordinates):
                try:
                    x1 = int(region["x"])
                    y1 = int(region["y"])
                    w = int(region["width"])
                    h = int(region["height"])
                    x2 = x1 + w
                    y2 = y1 + h

                    roi = frame[y1:y2, x1:x2]
                    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

                    custom_config = r'--oem 3 --psm 6'
                    text = pytesseract.image_to_string(thresh, config=custom_config)
                    print(type(region_texts[i]))
                    region_texts[i].append(text.strip())
                except Exception as e:
                    print(f"Error in region {i}: {e}")
                    region_texts[i].append("")

        frame_count += 1

    capture.release()
    cv2.destroyAllWindows()

    # Create DataFrame with columns Region 1, Region 2, ...
    data = {f"Region {i+1}": region_texts[i] for i in range(len(region_texts))}
    df = pd.DataFrame(data)
    df.to_excel(output_path, index=False)
    return output_path
