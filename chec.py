import pymysql

# MySQL 데이터베이스에 접속하는 함수
def connect_to_mysql():
    conn = pymysql.connect(
        host="elite.cxrdcyi1vpo5.us-east-2.rds.amazonaws.com",
        user="admin",
        password="team31337!",
        database="elite"
    )
    return conn

# attendance_801_elite 테이블에서 출석 상태가 '출석', '결석', '지각'인 학생의 student_id와 attendance_status 목록을 가져오는 함수
def get_attendance_students():
    conn = connect_to_mysql()
    cursor = conn.cursor()

    query = "SELECT student_id, attendance_status FROM attendance_801_elite WHERE attendance_status IN ('출석', '결석', '지각')"
    cursor.execute(query)

    students = cursor.fetchall()
    cursor.close()
    conn.close()

    return students

# acc_att_801 테이블에서 stu_id와 student_id가 같은 학생의 1week 필드를 attendance_status로 업데이트하는 함수
def update_attendance_status(students):
    conn = connect_to_mysql()
    cursor = conn.cursor()

    for student in students:
        student_id, attendance_status = student

        week = 1  # 첫 주로 초기화

        week_field = f"{week}week"
        next_week_field = f"{week + 1}week"

        query = f"SELECT {week_field} FROM acc_att_801_elite WHERE stu_id = %s"
        cursor.execute(query, (student_id,))
        result = cursor.fetchone()

        if result and result[0] is not None:
            # 데이터가 존재하는 경우, 다음 주로 업데이트
            query = f"UPDATE acc_att_801_elite SET `{next_week_field}` = %s WHERE stu_id = %s"
            cursor.execute(query, (attendance_status, student_id))

        # attendance_801_elite 테이블 업데이트
        query = "UPDATE attendance_801_elite SET attendance_status = %s WHERE student_id = %s"
        cursor.execute(query, (attendance_status, student_id))

    conn.commit()
    cursor.close()
    conn.close()

