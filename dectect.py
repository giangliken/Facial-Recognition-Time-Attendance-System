import cv2
import os
import numpy as np
import pyodbc
import time

# Duong dan den mo hinh da huan luyen
model_path = "trained_model.yml"
dataset_path = "know-faces"

# Tai mo hinh nhan dien khuon mat da huan luyen
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(model_path)

# Tai cascade de phat hien khuon mat
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Thong tin ket noi den Microsoft SQL Server
server = 'LT-TRUONGGIANG\\SQLEXPRESS'  # Thay doi server theo may chu cua ban
database = 'SPACEGO SYSTEM'  # Thay doi ten database theo nhu cau
connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

# Doc bang NHANVIEN va tao tu dien de anh xa UserName voi FullName, Position va Employee ID
def load_employee_data():
    cursor.execute("SELECT employee_id, full_name, position FROM NHANVIEN")
    employees = cursor.fetchall()
    employee_mapping = {row[0]: (row[1], row[2]) for row in employees}
    return employee_mapping

# Lay du lieu nhan vien
employee_data = load_employee_data()

# Tao tu dien de anh xa nhan voi UserName nguoi dung
label_names = {}
current_label_id = 0

# Gan nhan tu cac thu muc nguoi dung
for user_name in os.listdir(dataset_path):
    user_folder = os.path.join(dataset_path, user_name)
    if os.path.isdir(user_folder):
        label_names[current_label_id] = user_name
        current_label_id += 1

# Ham de kiem tra cham cong vao ca da ton tai
def check_attendance(user_name):
    today = time.strftime('%Y-%m-%d')
    cursor.execute("SELECT * FROM Attendance WHERE UserName = ? AND Action = 'Vao Ca' AND CAST(Timestamp AS DATE) = ?", (user_name, today))
    return cursor.fetchone() is not None

# Ham de ghi nhan vao co so du lieu
def mark_attendance(user_name, action):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO Attendance (UserName, Action, Timestamp) VALUES (?, ?, ?)", (user_name, action, timestamp))
    conn.commit()

# Luu tru so lan vao ra ca trong ngay
attendance_counter = {}

# Ham de lay so lan vao ra ca trong ngay tu database
def get_attendance_count(user_name):
    today = time.strftime('%Y-%m-%d')
    cursor.execute("SELECT COUNT(*) FROM Attendance WHERE UserName = ? AND CAST(Timestamp AS DATE) = ?", (user_name, today))
    result = cursor.fetchone()
    if result:
        return result[0]  # So lan cham cong trong ngay
    return 0


# Ham de cap nhat so lan vao ra ca
def update_attendance_count(user_name):
    today = time.strftime('%Y-%m-%d')
    if user_name not in attendance_counter:
        attendance_counter[user_name] = {}
    if today not in attendance_counter[user_name]:
        attendance_counter[user_name][today] = 0
    attendance_counter[user_name][today] += 1

# Ham de nhan dien va hien thi khuon mat
def recognize_faces():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # Thiết lập độ rộng khung hình
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # Thiết lập chiều cao khung hình
    work_status = 0  # Biến để theo dõi trạng thái ca làm việc: 0 - vào ca, 1 - ra ca

    # Tạo cửa sổ hiển thị toàn màn hình
    cv2.namedWindow('Nhan dien khuon mat', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('Nhan dien khuon mat', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Không thể đọc dữ liệu từ camera.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        # Hiển thị tên hệ thống ở góc trên bên trái
        cv2.putText(frame, "HE THONG CHAM CONG SPACEGO SYSTEM", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Hiển thị thời gian ở ngay bên dưới tên hệ thống
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        cv2.putText(frame, f"Thoi gian: {current_time}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            label_id, confidence = recognizer.predict(roi_gray)
            user_name = label_names.get(label_id, "Unknown")

            if confidence < 100:
                full_name, position = employee_data.get(user_name, ("Unknown", "Unknown"))  # Lấy tên và chức vụ đầy đủ
                employee_id = user_name  # Lưu mã số nhân viên từ tên người dùng

                attendance_count = get_attendance_count(user_name)  # Lấy số lần chấm công trong ngày

                if attendance_count >= 4:
                    cv2.putText(frame, f"{full_name} da cham cong trong ngay hom nay!.", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    # Hiển thị mã số nhân viên và chức vụ ở góc dưới bên trái
                    cv2.putText(frame, f"Ma so NV: {employee_id}", (50, frame.shape[0] - 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                    cv2.putText(frame, f"Chuc vu: {position}", (50, frame.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                else:
                    if work_status == 0:
                        cv2.putText(frame, f"Xac nhan vao ca: {full_name}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 225, 255), 2)
                    elif work_status == 1:
                        cv2.putText(frame, f"Xac nhan ra ca: {full_name}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    cv2.putText(frame, "Nhan 'y' de xac nhan", (50, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    cv2.putText(frame, "Nhan 'n' de quay lai", (50, 210), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                    # Hiển thị mã số nhân viên và chức vụ ở góc dưới bên trái
                    cv2.putText(frame, f"Ma so NV: {employee_id}", (50, frame.shape[0] - 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                    cv2.putText(frame, f"Chuc vu: {position}", (50, frame.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

                    # Kiểm tra phím bấm để xác nhận
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('y'):
                        action = 'Vao Ca' if work_status == 0 else 'Ra Ca'
                        mark_attendance(user_name, action)
                        update_attendance_count(user_name)
                        work_status = (work_status + 1) % 2  # Chuyển trạng thái giữa vào ca và ra ca
                        cv2.putText(frame, "Cham cong thanh cong!", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        time.sleep(2)  # Dừng lại 2 giây để hiển thị kết quả
                    elif key == ord('n'):
                        cv2.putText(frame, "Huy xac nhan", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        time.sleep(2)  # Dừng lại 2 giây để hiển thị kết quả

        cv2.imshow('Nhan dien khuon mat', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()



if __name__ == "__main__":
    print("Bat dau nhan dien khuon mat...")
    recognize_faces()

cursor.close()
conn.close()

