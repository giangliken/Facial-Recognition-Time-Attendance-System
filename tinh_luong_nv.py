import pyodbc
import calendar
from datetime import datetime

# Thông tin kết nối đến SQL Server
server = 'LT-TRUONGGIANG\\SQLEXPRESS'
database = 'SPACEGO SYSTEM'
connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()


def create_salary_table():
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='LuongNhanVienThang' AND xtype='U')
        CREATE TABLE LuongNhanVienThang (
            UserName NVARCHAR(50) NOT NULL PRIMARY KEY,
            FullName NVARCHAR(100),
            Position NVARCHAR(50),
            TotalSalary INT,
            DaysWorked INT,
            Month INT,
            Year INT
        );
    """)
    conn.commit()


# Gọi hàm tạo bảng trước khi tính lương
create_salary_table()


# Hàm lấy thông tin từ bảng NHANVIEN
def get_employee_data():
    cursor.execute("SELECT employee_id, full_name, position FROM NHANVIEN")
    employees = cursor.fetchall()
    employee_data = {row[0]: {"full_name": row[1], "position": row[2]} for row in employees}
    return employee_data


# Hàm lấy thông tin từ bảng Attendance theo tháng
def get_attendance_by_month(month, year):
    cursor.execute("""
        SELECT UserName, CAST(Timestamp AS DATE) AS WorkDay
        FROM Attendance
        WHERE MONTH(Timestamp) = ? AND YEAR(Timestamp) = ?
        GROUP BY UserName, CAST(Timestamp AS DATE)
        """, (month, year))
    return cursor.fetchall()


# Hàm tính lương theo tháng
def calculate_monthly_salary(attendance_records, employee_data, month, year):
    salary_data = {}
    for record in attendance_records:
        user_name = record[0]
        work_day = record[1]

        if user_name in employee_data:
            employee = employee_data[user_name]
            position = employee["position"]

            # Lương theo chức vụ
            if position == "Quan ly":
                daily_salary = 500000  # Lương cho quản lý
            elif position == "Nhan vien":
                daily_salary = 200000  # Lương cho nhân viên
            else:
                daily_salary = 0  # Nếu không phải hai nhóm trên, lương bằng 0

            # Tổng hợp lương theo tháng
            if user_name not in salary_data:
                salary_data[user_name] = {
                    "full_name": employee["full_name"],
                    "position": position,
                    "total_salary": 0,
                    "days_worked": 0
                }

            # Cập nhật lương và số ngày làm việc
            salary_data[user_name]["total_salary"] += daily_salary
            salary_data[user_name]["days_worked"] += 1

            # Debugging: In thông tin lương cho nhân viên
            print(
                f"UserName: {user_name}, WorkDay: {work_day}, Position: {position}, DailySalary: {daily_salary}, TotalSalary: {salary_data[user_name]['total_salary']}, DaysWorked: {salary_data[user_name]['days_worked']}")

    return salary_data


# Hàm lưu dữ liệu lương theo tháng vào bảng LuongNhanVienThang
def save_monthly_salary_data(salary_data, month, year):
    for user_name, data in salary_data.items():
        total_salary = data["total_salary"]
        days_worked = data["days_worked"]

        # Cập nhật hoặc chèn mới dữ liệu lương vào bảng
        cursor.execute("""
            MERGE INTO LuongNhanVienThang AS target
            USING (SELECT ? AS UserName, ? AS FullName, ? AS Position, ? AS TotalSalary, ? AS DaysWorked, ? AS Month, ? AS Year) AS source
            ON target.UserName = source.UserName
            WHEN MATCHED THEN
                UPDATE SET FullName = source.FullName, Position = source.Position, TotalSalary = source.TotalSalary, DaysWorked = source.DaysWorked, Month = source.Month, Year = source.Year
            WHEN NOT MATCHED THEN
                INSERT (UserName, FullName, Position, TotalSalary, DaysWorked, Month, Year)
                VALUES (source.UserName, source.FullName, source.Position, source.TotalSalary, source.DaysWorked, source.Month, source.Year);
        """, (user_name, data["full_name"], data["position"], total_salary, days_worked, month, year))

    conn.commit()


# Hàm tính lương cho tất cả nhân viên trong một tháng
def process_salary_for_month(month, year):
    employee_data = get_employee_data()  # Lấy dữ liệu từ bảng NHANVIEN
    attendance_records = get_attendance_by_month(month, year)  # Lấy dữ liệu chấm công theo tháng
    salary_data = calculate_monthly_salary(attendance_records, employee_data, month, year)  # Tính lương
    save_monthly_salary_data(salary_data, month, year)  # Lưu dữ liệu lương vào bảng LuongNhanVienThang


# Ví dụ: Tính lương cho tháng 10 năm 2024
month = 10
year = 2024
process_salary_for_month(month, year)

# Đóng kết nối
cursor.close()
conn.close()

print(f"Hoàn tất tính lương cho tháng {month}/{year}.")
