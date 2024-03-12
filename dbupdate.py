import time
import pymysql

# DB 연결 설정
mydb = pymysql.connect(
    host="elite.cxrdcyi1vpo5.us-east-2.rds.amazonaws.com",
    user="admin",
    password="team31337!",
    database="elite"
)

cursor = mydb.cursor()

while True:
    # DB에서 모든 학생의 student_id와 attendance_status 가져오기
    cursor.execute("SELECT student_id, attendance_status FROM attendance_801_31337")
    db_data = cursor.fetchall()

    # 텍스트 파일 읽기
    with open('attendance.txt', 'r') as file:
        txt_data = file.readlines()

    # 출석/지각/결석 업데이트
    for db_student_id, attendance_status in db_data:
        if attendance_status != '출석' and db_student_id not in [student_id.strip() for student_id in txt_data]:
            cursor.execute("UPDATE attendance_801_31337 SET attendance_status = '결석' WHERE student_id = %s", (db_student_id,))
            print(f"결석: 학생 {db_student_id}")

    # 이탈 처리
    for db_student_id, attendance_status in db_data:
        if attendance_status == '출석' and db_student_id not in [student_id.strip() for student_id in txt_data]:
            cursor.execute("UPDATE attendance_801_31337 SET attendance_status = '이탈' WHERE student_id = %s", (db_student_id,))
            print(f"이탈: 학생 {db_student_id}")

    # 텍스트 파일에 있는 학생 처리
    for line in txt_data:
        student_id = line.strip()
        found = False

        # DB에서 학생 정보 확인
        for db_student_id, attendance_status in db_data:
            if student_id == db_student_id:
                found = True

                # 출석이 아닌 경우에만 처리
                if attendance_status != '출석':
                    # 결석인 경우
                    if attendance_status == '결석':
                        cursor.execute("UPDATE attendance_801_31337 SET attendance_status = '지각' WHERE student_id = %s", (student_id,))
                        print(f"지각: 학생 {student_id}")
                    else:
                        cursor.execute("UPDATE attendance_801_31337 SET attendance_status = '출석' WHERE student_id = %s", (student_id,))
                        print(f"출석: 학생 {student_id}")
                break  # Exit the loop once the student is found in the database

        # DB에 학생 정보가 없는 경우 (결석 처리)
        if not found:
            cursor.execute("UPDATE attendance_801_31337 SET attendance_status = '결석' WHERE student_id = %s", (student_id,))
            print(f"결석: 학생 {student_id}")

    # DB 업데이트 저장
    mydb.commit()

    # 10초마다 업데이트 확인
    time.sleep(5)

# DB 연결 종료
mydb.close()
