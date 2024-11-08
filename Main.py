import subprocess
import os

def clear_screen():
    # Clear the console screen
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    # Pause until the user presses Enter
    input("Nhấn Enter để tiếp tục...")

def main_menu():
    while True:
        clear_screen()
        print("---------------------- MENU ----------------------")
        print("1. Quản lí nhân viên.py")
        print("2. Chạy mô hình training dữ liệu gương mặt.py")
        print("3. Chấm công dựa trên sinh trắc học.py")
        print("4. Xem và Xuất dữ liệu")
        print("0. Thoát")

        choice = input("Nhập lựa chọn của bạn: ")

        if choice == '1':
            subprocess.run(["python", "D:/Tai Lieu Hoc Tap/Tri Tue Nhan Tao/Do An/Nhan Dien Khuon Mat/thu thap du lieu nguoi dung.py"])
            pause()
        elif choice == '2':
            subprocess.run(["python", "D:/Tai Lieu Hoc Tap/Tri Tue Nhan Tao/Do An/Nhan Dien Khuon Mat/train.py"])
            pause()
        elif choice == '3':
            subprocess.run(["python", "D:/Tai Lieu Hoc Tap/Tri Tue Nhan Tao/Do An/Nhan Dien Khuon Mat/dectect.py"])
            pause()
        elif choice == '4':
            subprocess.run(["python", "D:/Tai Lieu Hoc Tap/Tri Tue Nhan Tao/Do An/Nhan Dien Khuon Mat/xuat du lieu.py"])
            pause()
        elif choice == '0':
            print("Đã thoát chương trình.")
            break
        else:
            print("Lựa chọn không hợp lệ. Vui lòng thử lại.")
            pause()

# Gọi menu chính
main_menu()