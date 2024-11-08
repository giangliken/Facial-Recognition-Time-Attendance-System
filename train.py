import cv2
import os
import numpy as np
from PIL import Image
from tqdm import tqdm

# Đường dẫn đến thư mục lưu trữ dữ liệu khuôn mặt
dataset_path = "know-faces"
model_save_path = "trained_model.yml"

# Khởi tạo bộ nhận diện khuôn mặt LBPH
recognizer = cv2.face.LBPHFaceRecognizer_create()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Hàm lấy danh sách các hình ảnh và nhãn (label) tương ứng
def get_images_and_labels(dataset_path):
    face_samples = []
    face_labels = []
    label_names = {}
    current_label_id = 0

    for user_name in os.listdir(dataset_path):
        user_folder = os.path.join(dataset_path, user_name)

        if not os.path.isdir(user_folder):
            continue

        if user_name not in label_names:
            label_names[user_name] = current_label_id
            current_label_id += 1

        label_id = label_names[user_name]

        for image_file in os.listdir(user_folder):
            image_path = os.path.join(user_folder, image_file)

            if not image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            img = Image.open(image_path).convert('L')
            img_np = np.array(img, 'uint8')

            faces = face_cascade.detectMultiScale(img_np, scaleFactor=1.1, minNeighbors=5)

            for (x, y, w, h) in faces:
                face_samples.append(img_np[y:y + h, x:x + w])
                face_labels.append(label_id)

    return face_samples, face_labels, label_names

# Hàm kiểm tra độ chính xác của mô hình
def test_model(test_path, recognizer, label_names):
    correct_predictions = 0
    total_predictions = 0

    # Đếm số lượng hình ảnh kiểm tra
    total_images = sum(len(files) for _, _, files in os.walk(test_path))

    # Sử dụng tqdm để hiển thị thanh tiến trình
    for user_name in os.listdir(test_path):
        user_folder = os.path.join(test_path, user_name)

        if not os.path.isdir(user_folder):
            continue

        for image_file in os.listdir(user_folder):
            image_path = os.path.join(user_folder, image_file)

            if not image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            img = Image.open(image_path).convert('L')
            img_np = np.array(img, 'uint8')

            faces = face_cascade.detectMultiScale(img_np, scaleFactor=1.1, minNeighbors=5)

            for (x, y, w, h) in faces:
                face = img_np[y:y + h, x:x + w]
                label_id, confidence = recognizer.predict(face)

                if label_id in label_names.values():
                    actual_name = [name for name, id in label_names.items() if id == label_id][0]
                    if actual_name == user_name:
                        correct_predictions += 1
                total_predictions += 1

    accuracy = (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Độ chính xác: {accuracy:.2f}% ({correct_predictions}/{total_predictions})")

print("Bắt đầu quá trình huấn luyện khuôn mặt...")

# Lấy hình ảnh và nhãn
faces, labels, label_names = get_images_and_labels(dataset_path)

if len(faces) == 0:
    print("Không có dữ liệu khuôn mặt nào được tìm thấy trong thư mục.")
else:
    print("Đang huấn luyện...")

    # Huấn luyện bộ nhận diện với dữ liệu khuôn mặt và nhãn
    for i in tqdm(range(len(faces)), desc="Training Progress"):
        recognizer.update(faces[i:i + 1], np.array(labels[i:i + 1]))

    # Lưu mô hình đã được huấn luyện vào file
    recognizer.save(model_save_path)

    print(f"Huấn luyện hoàn tất. Mô hình đã được lưu vào: {model_save_path}")
    print(f"Mapping of labels to names: {label_names}")

    # Kiểm tra độ chính xác trên tập dữ liệu kiểm tra
    #test_dataset_path = "test-faces"  # Đường dẫn đến thư mục chứa dữ liệu kiểm tra
    #print("Đang kiểm tra độ chính xác của mô hình...")
    #test_model(test_dataset_path, recognizer, label_names)
