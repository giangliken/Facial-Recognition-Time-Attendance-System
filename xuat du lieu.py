import pyodbc
import pandas as pd
import subprocess  # Ensure subprocess is imported

# Thông tin kết nối đến SQL Server
server = 'LT-TRUONGGIANG\\SQLEXPRESS'
database = 'SPACEGO SYSTEM'
connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

def export_to_excel(query, filename):
    # Kết nối đến SQL Server
    conn = pyodbc.connect(connection_string)
    df = pd.read_sql_query(query, conn)
    df.to_excel(filename, index=False)
    conn.close()
    print(f'Data exported to {filename}')

def view_data(query):
    # Kết nối đến SQL Server
    conn = pyodbc.connect(connection_string)
    df = pd.read_sql_query(query, conn)
    conn.close()
    print(df)

def pause():
    input("Press Enter to continue...")

def main():
    while True:
        print("Chọn tùy chọn:")
        print("1: Xem dữ liệu Nhân viên")
        print("2: Xem dữ liệu Chấm công")
        print("3: Tính lương nhân viên")
        print("4: Xuất dữ liệu Nhân viên ra Excel")
        print("5: Xuất dữ liệu Chấm công ra Excel")
        print("0: Thoát")

        choice = input("Nhập lựa chọn của bạn: ")

        if choice == '1':
            query = "SELECT * FROM NhanVien"
            print("Dữ liệu Nhân viên:")
            view_data(query)
        elif choice == '2':
            query = "SELECT * FROM Attendance"
            print("Dữ liệu Chấm công:")
            view_data(query)
        elif choice == '3':
            try:
                subprocess.run(["python", "D:/Tai Lieu Hoc Tap/Tri Tue Nhan Tao/Do An/Nhan Dien Khuon Mat/tinh_luong_nv.py"])
                query = "SELECT * FROM LuongNhanVienThang"  # Replace with actual salary calculation query if needed
                export_to_excel(query, 'data_xlsx/luong_nhan_vien.xlsx')
                subprocess.run(["python", "D:/Tai Lieu Hoc Tap/Tri Tue Nhan Tao/Do An/Nhan Dien Khuon Mat/in bang luong nv.py"])
                pause()
            except Exception as e:
                print(f"An error occurred while processing option 3: {e}")
        elif choice == '4':
            query = "SELECT * FROM NhanVien"
            export_to_excel(query, 'data_xlsx/nhan_vien.xlsx')
        elif choice == '5':
            query = "SELECT * FROM Attendance"
            export_to_excel(query, 'data_xlsx/cham_cong.xlsx')
        elif choice == '0':
            print("Đang thoát...")
            break
        else:
            print("Lựa chọn không hợp lệ. Vui lòng thử lại.")

if __name__ == "__main__":
    main()
