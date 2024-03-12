import os
import socket
import threading
import datetime
import pymysql
import time

# 서버 정보
server_address = ("192.168.8.31", 5000)
mydb = pymysql.connect(
  host="elite.cxrdcyi1vpo5.us-east-2.rds.amazonaws.com",
  user="admin",
  password="team31337!",
  database="elite"
)

# 이미지 파일을 저장할 디렉토리 경로
save_directory_path = "C:/Users/HB/Desktop/최종테스트/save_dir"
#img_directory_path = "C:/Users/k_y_k/OneDrive/Desktop/새 폴더/AI/img"

image_extensions = (".jpg", ".jpeg", ".png")

def save_file_to_directory(file_path):
    directory_name = file_path[:3]
    directory_path = os.path.join(save_directory_path, directory_name)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    return os.path.join(directory_path, os.path.basename(file_path))

# 클라이언트 IP
mobius_client_ip = "192.168.8.179"
ai_client_ip = "192.168.8.212"

# 함수: Mobius 클라이언트로부터 이미지를 받는 작업
def receive_from_mobius(client_socket, client_address):
    try:
        while True:
            # 파일 데이터를 받기 전에 먼저 파일 데이터의 크기를 받음
            num_chunks_bytes = client_socket.recv(4)
            if not num_chunks_bytes:
                # 클라이언트가 연결을 종료한 경우
                print("Connection closed by Mobius client")
                break
            num_chunks = int.from_bytes(num_chunks_bytes, byteorder="big")

            # 파일명 길이로부터 파일명 받기
            filename_length_bytes = client_socket.recv(4)
            if not filename_length_bytes:
                break
            filename_length = int.from_bytes(filename_length_bytes, byteorder="big")
            filename_bytes = client_socket.recv(filename_length)
            if not filename_bytes:
                break
            filename = filename_bytes.decode("utf-8")

            # 파일 크기 받기
            file_size_bytes = client_socket.recv(8)
            if not file_size_bytes:
                break
            file_size = int.from_bytes(file_size_bytes, byteorder="big")

            # 파일 데이터 받기
            file_data = b""
            bytes_received = 0
            while bytes_received < file_size:
                chunk_size = min(file_size - bytes_received, 1024)
                data = client_socket.recv(chunk_size)
                if not data:
                    break
                file_data += data
                bytes_received += len(data)

            # 파일 데이터 검증
            if len(file_data) != file_size:
                print(f"Data transfer incomplete for {filename}")
                break

            # 파일 데이터 저장
            save_path = save_file_to_directory(filename)
            with open(save_path, "wb") as file:
                file.write(file_data)
                print(f"{filename} saved to {save_path}")
    except (ConnectionAbortedError, ConnectionResetError):
        print(f"Connection closed by Mobius client: {client_address}")

    # 클라이언트 소켓 종료


def update_DB():
    cursor = mydb.cursor()

    while True:
        # DB에서 모든 학생의 student_id와 attendance_status 가져오기
        cursor.execute("SELECT student_id, attendance_status FROM attendance_801_elite")
        db_data = cursor.fetchall()

        # 텍스트 파일 읽기
        with open('attendance.txt', 'r') as file:
            txt_data = file.readlines()

        # 출석/이탈/지각/결석 업데이트
        for line in txt_data:
            student_id = line.strip()
            found = False

            # DB에서 학생 정보 확인
            for db_student_id, attendance_status in db_data:
                if student_id == db_student_id:
                    found = True

                    # 출석인 경우
                    if attendance_status != '출석':
                        cursor.execute("UPDATE attendance_801_elite SET attendance_status = '출석' WHERE student_id = %s", (student_id,))
                        print(f"출석: 학생 {student_id}")
                    

            # DB에 학생 정보가 없는 경우 (결석 처리)

        # 이탈 처리
        for db_student_id, attendance_status in db_data:
            if attendance_status == '출석' and db_student_id not in [student_id.strip() for student_id in txt_data]:
                cursor.execute("UPDATE attendance_801_elite SET attendance_status = '이탈' WHERE student_id = %s", (db_student_id,))
                print(f"이탈: 학생 {db_student_id}")

        # DB 업데이트 저장
        mydb.commit()

        # 10초마다 업데이트 확인
        time.sleep(1.5)

    # DB 연결 종료
    mydb.close()





        













    

# 함수: AI 클라이언트에게 이미지를 전송하는 작업
def send_to_ai(client_socket, client_address):
    try:
        while True:
        # img 폴더 내부 탐색
            for folder_name in ["801", "802", "803", "804","202"]:
                folder_path = os.path.join(save_directory_path, folder_name)

                for root, dirs, files in os.walk(folder_path):
                    if len(files) > 0:
                        # 이미지 파일 확인
                        image_files = [f for f in files if f.lower().endswith(image_extensions)]

                        if len(image_files) == 0:
                            # 이미지 파일이 없으면 다음 폴더로 이동
                            continue

                        # 이미지 파일 전송
                        for filename in image_files:
                            file_path = os.path.join(root, filename)
                            with open(file_path, "rb") as file:
                    # 파일명과 파일 데이터를 함께 전송
                                filename_bytes = filename.encode("utf-8")
                                file_data = file.read()
                    
                            num_chunks = len(file_data)
                
                            client_socket.send(num_chunks.to_bytes(4, byteorder="big"))
                            print(f"{num_chunks}")
                            filename_length = len(filename)

                            client_socket.send(filename_length.to_bytes(4, byteorder="big"))
                            client_socket.send(filename.encode("utf-8"))

                            file_size = os.path.getsize(file_path)
                    
                            client_socket.send(file_size.to_bytes(8, byteorder="big"))
                            client_socket.sendall(file_data)
                            print(f"Size of {filename}: {file_size} bytes")
                            print(f"{filename} sent to server")
                            
                    # 파일 삭제
                            os.remove(file_path)
                            print(f"{file_path} deleted")

                        # AI 클라이언트 소켓 종료
                        #client_socket.close()

    except (ConnectionAbortedError, ConnectionResetError):
        print(f"Connection closed by AI client: {client_address}")

def receive_text_client(server_socket):
    copy = b''
    filepath = 'C:/Users/HB/attendance.txt'
    while True:
        data = server_socket.recv(1024)
        
        if copy == data:
            continue
        else:
            print('AI가 판단한 학번 데이터',repr(data.decode()))
            
            copy = data
            
            with open(filepath, 'w') as f:
                f.write(data.decode())
                f.close()


# 함수: 클라이언트 연결 처리
def handle_connections():
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(server_address)
        server_socket.listen(2)
        print("Server is ready to receive")
        DB_thread = threading.Thread(target=update_DB)
        DB_thread.start()


        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connected by {client_address}")
            


            if client_address[0] == mobius_client_ip:
                # Mobius 클라이언트로부터 이미지를 받는 작업을 쓰레드로 실행
                mobius_thread = threading.Thread(target=receive_from_mobius, args=(client_socket, client_address))
                mobius_thread.start()

            elif client_address[0] == ai_client_ip:
                # AI 클라이언트에게 이미지를 전송하는 작업을 쓰레드로 실행
                ai_thread = threading.Thread(target=send_to_ai, args=(client_socket, client_address))
                ai_thread.start()
                
                text_thread = threading.Thread(target=receive_text_client, args=(client_socket,))
                text_thread.start()


            else:
                # 다른 클라이언트의 연결은 거부
                print(f"Connection from {client_address} is not allowed")

    except OSError as e:
        print(f"OSError occurred: {str(e)}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        # 클라이언트 소켓 종료
        client_socket.close()

        # 서버 소켓 종료
        server_socket.close()

# 클라이언트 연결 처리 쓰레드 실행
handle_thread = threading.Thread(target=handle_connections)
handle_thread.start()

# handle_thread가 종료되면서 서버 소켓을 닫습니다.
handle_thread.join()