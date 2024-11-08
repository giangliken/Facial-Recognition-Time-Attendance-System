import os
import pyodbc
from reportlab.lib.pagesizes import A6
from reportlab.pdfgen import canvas
from datetime import datetime

# Thong tin ket noi den SQL Server
server = 'LT-TRUONGGIANG\\SQLEXPRESS'
database = 'SPACEGO SYSTEM'
connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

# Tao thu muc de luu bill luong neu chua ton tai
folder_path = 'LuongNhanVien'
if not os.path.exists(folder_path):
    os.makedirs(folder_path)


# Ham lay thong tin luong nhan vien tu bang LuongNhanVienThang
def get_salary_bills():
    cursor.execute("SELECT UserName, FullName, Position, TotalSalary, DaysWorked, Month, Year FROM LuongNhanVienThang")
    return cursor.fetchall()


# Ham lay chi tiet lam viec tu bang Attendance
def get_attendance_data(user_name):
    cursor.execute("SELECT * FROM Attendance WHERE UserName = ?", (user_name,))
    return cursor.fetchall()


# Ham tao file bill cho moi nhan vien duoi dang PDF
def create_salary_bill_pdf(employee_data):
    user_name, full_name, position, total_salary, days_worked, month, year = employee_data

    # Duong dan file
    file_path = os.path.join(folder_path, f"{user_name}_bill_{month}_{year}.pdf")

    # Tao PDF voi kich thuoc A6
    c = canvas.Canvas(file_path, pagesize=A6)
    width, height = A6

    # Viet tieu de
    c.setFont("Helvetica-Bold", 12)
    c.drawString(10, height - 15, "CONG TY TNHH MTV SPACEGO")

    # Noi dung bill
    bill_content = f"""BANG LUONG NHAN VIEN
==============================================
Ten nhan vien: {full_name}
Chuc vu: {position}
Tong luong: {total_salary} VND
So ngay lam viec: {days_worked}
Thang: {month} Nam: {year}
==============================================
"""
    # Viet noi dung vao PDF
    text_object = c.beginText(10, height - 30)
    text_object.setFont("Helvetica", 10)
    for line in bill_content.splitlines():
        text_object.textLine(line)
    c.drawText(text_object)

    # Lay chi tiet lam viec
    attendance_data = get_attendance_data(user_name)

    # Ve tieu de bang cho chi tiet lam viec
    c.setFont("Helvetica-Bold", 10)
    c.drawString(10, height - 130, "Chi tiet ngay lam viec:")
    c.drawString(10, height - 145, "UserName | Action | Timestamp")

    # Ve bang cho chi tiet lam viec
    start_y = height - 160
    c.setFont("Helvetica", 8)
    row_height = 10
    row_count = 0  # Count rows to manage page space

    # Ve cac dong cho tung chi tiet lam viec
    for record in attendance_data:
        # Assuming the record has the following fields, adjust the indexes based on your table structure
        action = record[2]  # Change this index if the action is at a different column
        timestamp = record[3]  # Change this index if the timestamp is at a different column

        date_str = timestamp.strftime("%d/%m/%Y")
        time_str = timestamp.strftime("%H:%M")

        # In ra chi tiet
        c.drawString(10, start_y - row_count * row_height, f"{user_name} | {action} | {time_str}")
        row_count += 1

        # Check if we've reached the bottom of the page
        if start_y - (row_count * row_height) < 10:  # Leave some space at the bottom
            c.showPage()  # Start a new page
            c.setFont("Helvetica-Bold", 12)
            c.drawString(10, height - 15, "CONG TY TNHH MTV SPACEGO")
            c.setFont("Helvetica-Bold", 10)
            c.drawString(10, height - 130, "Chi tiet ngay lam viec:")
            c.drawString(10, height - 145, "UserName | Action | Timestamp")
            row_count = 0  # Reset row count for new page
            start_y = height - 160  # Reset y position for new page

    # Them ngay thang in bill o duoi cung
    c.setFont("Helvetica", 8)
    print_date = datetime.now().strftime("%d/%m/%Y")
    c.drawString(10, 10, f"Ngay in bill: {print_date}")

    # Luu file PDF
    c.save()
    print(f"Da tao bill luong cho {full_name} tai {file_path}")


# Ham in bill luong cho tat ca nhan vien
def print_salary_bills():
    salary_bills = get_salary_bills()  # Lay du lieu bill luong
    for employee_data in salary_bills:
        create_salary_bill_pdf(employee_data)  # Tao file bill cho tung nhan vien


# In bill luong cho nhan vien
print_salary_bills()

# Dong ket noi
cursor.close()
conn.close()

print("Hoan tat in bill luong cho tat ca nhan vien.")
