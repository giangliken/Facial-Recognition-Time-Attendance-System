import pyodbc
import cv2
import os
import time

# Thông tin kết nối đến SQL Server
server = 'LT-TRUONGGIANG\\SQLEXPRESS'  # Thay đổi theo tên server của bạn
database = 'SPACEGO SYSTEM'  # Tên database
connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
# Kết nối tới Microsoft SQL Server
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

# Tạo bảng 'NHANVIEN' nếu chưa tồn tại
cursor.execute('''
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='NHANVIEN' AND xtype='U')
    CREATE TABLE NHANVIEN (
        employee_id NVARCHAR(6) PRIMARY KEY,
        full_name NVARCHAR(100),
        address NVARCHAR(255),
        birthdate DATE,
        position NVARCHAR(50)
    )
''')
conn.commit()

# Tạo thư mục lưu dữ liệu nếu chưa tồn tại
dataset_path = "know-faces"
if not os.path.exists(dataset_path):
    os.makedirs(dataset_path)


def add_employee():
    # Tạo mã số nhân viên tự động theo cấu trúc XXXXXX
    existing_employees = [name for name in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, name))]
    new_employee_id = len(existing_employees) + 1
    employee_id = f"{new_employee_id:06d}"  # Mã số nhân viên theo định dạng XXXXXX

    user_folder = os.path.join(dataset_path, employee_id)
    os.makedirs(user_folder)

    # Nhập thông tin nhân viên
    full_name = input("Nhập họ tên nhân viên: ").strip()
    address = input("Nhập địa chỉ nhân viên: ").strip()
    birthdate = input("Nhập ngày sinh (YYYY-MM-DD): ").strip()
    position = input("Nhập chức vụ nhân viên: ").strip()

    # Chèn thông tin nhân viên vào bảng 'NHANVIEN'
    cursor.execute('''
        INSERT INTO NHANVIEN (employee_id, full_name, address, birthdate, position)
        VALUES (?, ?, ?, ?, ?)
    ''', (employee_id, full_name, address, birthdate, position))
    conn.commit()

    # Bắt đầu thu thập gương mặt mới
    collect_faces(employee_id, user_folder)


def update_employee():
    existing_employee_id = input("Nhập mã số nhân viên để cập nhật gương mặt: ").strip()

    cursor.execute('SELECT * FROM NHANVIEN WHERE employee_id = ?', (existing_employee_id,))
    employee_data = cursor.fetchone()

    if employee_data:
        print(f"Đã tìm thấy nhân viên: {employee_data.full_name}")
        user_folder = os.path.join(dataset_path, existing_employee_id)

        # Xóa các ảnh cũ trong thư mục
        if os.path.exists(user_folder):
            for file in os.listdir(user_folder):
                file_path = os.path.join(user_folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print(f"Đã xóa các ảnh cũ trong thư mục {user_folder}.")

        # Cập nhật thông tin nhân viên
        full_name = input("Nhập họ tên nhân viên (hoặc nhấn Enter để giữ nguyên): ").strip() or employee_data.full_name
        address = input("Nhập địa chỉ nhân viên (hoặc nhấn Enter để giữ nguyên): ").strip() or employee_data.address
        birthdate = input(
            "Nhập ngày sinh (YYYY-MM-DD) (hoặc nhấn Enter để giữ nguyên): ").strip() or employee_data.birthdate
        position = input("Nhập chức vụ nhân viên (hoặc nhấn Enter để giữ nguyên): ").strip() or employee_data.position

        # Cập nhật thông tin nhân viên vào bảng 'NHANVIEN'
        cursor.execute('''
            UPDATE NHANVIEN
            SET full_name = ?, address = ?, birthdate = ?, position = ?
            WHERE employee_id = ?
        ''', (full_name, address, birthdate, position, existing_employee_id))
        conn.commit()

        # Cập nhật gương mặt
        collect_faces(existing_employee_id, user_folder)
    else:
        print("Mã số nhân viên không tồn tại.")


def delete_employee():
    existing_employee_id = input("Nhập mã số nhân viên để xóa: ").strip()

    cursor.execute('SELECT * FROM NHANVIEN WHERE employee_id = ?', (existing_employee_id,))
    employee_data = cursor.fetchone()

    if employee_data:
        # Xóa thông tin nhân viên
        cursor.execute('DELETE FROM NHANVIEN WHERE employee_id = ?', (existing_employee_id,))
        conn.commit()

        # Xóa thư mục gương mặt
        user_folder = os.path.join(dataset_path, existing_employee_id)
        if os.path.exists(user_folder):
            os.rmdir(user_folder)
        print(f"Đã xóa nhân viên {employee_data.full_name} với mã số {existing_employee_id}.")
    else:
        print("Mã số nhân viên không tồn tại.")


def collect_faces(employee_id, user_folder):
    max_images = 100  # Số lượng ảnh khuôn mặt cần thu thập
    image_count = 0

    # Chọn nguồn video (camera hoặc file video)
    source = input("Nhập '0' để mở camera hoặc đường dẫn file video: ").strip()
    cap = cv2.VideoCapture(source) if source != '0' else cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Không thể mở nguồn video.")
        return

    # Tải cascade để phát hiện khuôn mặt
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    directions = ['front', 'left', 'right', 'up', 'down']
    images_per_direction = max_images // len(directions)

    current_direction_index = 0
    current_direction = directions[current_direction_index]
    captured_per_direction = 0

    print(f"Xin hãy quay mặt {current_direction}")

    while image_count < max_images:
        ret, frame = cap.read()
        if not ret:
            print("Error: Không thể đọc frame từ nguồn video.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            file_name = f"{user_folder}/{employee_id}_{current_direction}_{captured_per_direction}.jpg"
            cv2.imwrite(file_name, gray[y:y + h, x:x + w])
            image_count += 1
            captured_per_direction += 1

        cv2.imshow('Face Capture', frame)
        print(f"Đã lưu {captured_per_direction} ảnh ở hướng {current_direction}...")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if captured_per_direction >= images_per_direction:
            current_direction_index += 1
            if current_direction_index >= len(directions):
                break
            current_direction = directions[current_direction_index]
            captured_per_direction = 0
            print(f"Xin hãy quay mặt {current_direction}")
            time.sleep(2)

    cap.release()
    cv2.destroyAllWindows()
    print(f"Đã lưu {image_count} ảnh vào thư mục {user_folder} với mã số nhân viên: {employee_id}")


def main_menu():
    while True:
        print("\n--- MENU ---")
        print("1. Thêm nhân viên")
        print("2. Cập nhật nhân viên")
        print("3. Xóa nhân viên")
        print("4. Thoát")

        choice = input("Nhập lựa chọn của bạn: ")

        if choice == '1':
            add_employee()
        elif choice == '2':
            update_employee()
        elif choice == '3':
            delete_employee()
        elif choice == '4':
            print("Đã thoát chương trình.")
            break
        else:
            print("Lựa chọn không hợp lệ. Vui lòng thử lại.")


# Chạy menu chính
main_menu()

# Đóng kết nối SQL
conn.close()