import cv2
import numpy as np
import os
import threading

# Thư mục chứa các ảnh của những người đã biết
KNOWN_FACES_DIR = "know-faces"
FRAME_THICKNESS = 3  # Độ dày của khung hình nhận diện
FONT_THICKNESS = 2   # Độ dày font hiển thị tên
CONFIDENCE_THRESHOLD = 60.0  # Ngưỡng tin cậy để gán nhãn Unknown

# Tạo đối tượng nhận diện khuôn mặt
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Tạo và huấn luyện mô hình nhận diện khuôn mặt
recognizer = cv2.face.LBPHFaceRecognizer_create()

# Lưu trữ tên và ảnh của những người đã biết
known_faces = []
known_labels = []
label_map = {}
current_label = 0

# Tải ảnh của những người đã biết
print("Tải và mã hóa khuôn mặt...")
for name in os.listdir(KNOWN_FACES_DIR):
    label_map[current_label] = name
    for filename in os.listdir(f"{KNOWN_FACES_DIR}/{name}"):
        image = cv2.imread(f"{KNOWN_FACES_DIR}/{name}/{filename}")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        for (x, y, w, h) in faces:
            face_img = gray[y:y+h, x:x+w]
            known_faces.append(face_img)
            known_labels.append(current_label)
    current_label += 1

recognizer.train(known_faces, np.array(known_labels))

# Chọn nguồn video (camera hoặc file video)
sources = input("Nhập '0' để mở camera hoặc đường dẫn file video (tối đa 3, cách nhau bởi dấu phẩy): ").strip().split(',')

# Giới hạn số lượng nguồn video tối đa là 3
sources = sources[:3]

# Biến toàn cục để lưu mức thu phóng
zoom_levels = [1.0] * len(sources)

# Hàm xử lý sự kiện chuột
def mouse_callback(event, x, y, flags, param):
    global zoom_levels
    window_index = param
    if event == cv2.EVENT_MOUSEWHEEL:
        if flags > 0:
            zoom_levels[window_index] += 0.1
        else:
            zoom_levels[window_index] = max(1.0, zoom_levels[window_index] - 0.1)

# Hàm để xử lý từng nguồn video
def process_video(source, window_name, window_index):
    if source == '0':
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print(f"Error: Không thể mở nguồn video {source}.")
        return

    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_callback, window_index)

    while True:
        # Đọc frame từ nguồn video
        ret, frame = cap.read()

        if not ret:
            # Nếu không thể đọc frame, đặt lại video về đầu
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # Chuyển đổi ảnh thành màu xám
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Nhận diện khuôn mặt trong frame
        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            # Vẽ hình chữ nhật quanh khuôn mặt
            color = [0, 255, 0]  # Màu xanh cho khung nhận diện
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, FRAME_THICKNESS)

            # Lấy vùng khuôn mặt
            face_img = gray[y:y+h, x:x+w]

            # Nhận diện khuôn mặt
            label, confidence = recognizer.predict(face_img)

            # Nếu mức độ tin cậy vượt quá ngưỡng, gán nhãn là "Unknown"
            if confidence < CONFIDENCE_THRESHOLD:
                name = label_map.get(label, "Unknown")
            else:
                name = "Unknown"

            # Vẽ tên người lên ảnh
            cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, FONT_THICKNESS)

        # Thu phóng video
        height, width = frame.shape[:2]
        new_size = (int(width * zoom_levels[window_index]), int(height * zoom_levels[window_index]))
        frame = cv2.resize(frame, new_size)

        # Hiển thị kết quả
        cv2.imshow(window_name, frame)

        # Kiểm tra sự kiện phím
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    # Giải phóng tài nguyên
    cap.release()
    cv2.destroyWindow(window_name)

# Xử lý từng nguồn video trong các luồng riêng biệt
threads = []
for i, source in enumerate(sources):
    window_name = f"Video {i+1}"
    thread = threading.Thread(target=process_video, args=(source.strip(), window_name, i))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

cv2.destroyAllWindows()
