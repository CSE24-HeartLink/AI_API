import subprocess
import sys
import time
import os

def run_server(file_name, port):
    try:
        return subprocess.Popen(
            [
                sys.executable, 
                "-m", 
                "uvicorn", 
                f"{file_name}:app", 
                "--reload", 
                f"--port={port}",
                "--host", 
                "0.0.0.0"  # 모든 네트워크 인터페이스에서 접근 가능하도록 설정
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
    except Exception as e:
        print(f"서버 실행 중 오류 발생 ({file_name}): {str(e)}")
        return None

def main():
    # 서버 설정
    servers = [
        {"name": "Chat_API_1", "port": 8000},
        {"name": "DALLE_API_1", "port": 8001},
        {"name": "Korean-STT", "port": 8002}
    ]
    
    processes = []
    
    try:
        print("AI 서버 시작 중...")
        
        # 서버 실행
        for server in servers:
            process = run_server(server["name"], server["port"])
            if process:
                processes.append(process)
                print(f"{server['name']} 서버가 포트 {server['port']}에서 실행 중입니다.")
                time.sleep(2)  # 서버 시작 간격
        
        print("\n모든 서버가 실행되었습니다.")
        print("서버를 종료하려면 Ctrl+C를 누르세요.\n")
        
        # 서버 로그 모니터링
        while True:
            for process in processes:
                output = process.stdout.readline()
                if output:
                    print(output.strip())
    
    except KeyboardInterrupt:
        print("\n서버 종료 중...")
        for process in processes:
            process.terminate()
        
        print("모든 서버가 종료되었습니다.")

if __name__ == "__main__":
    main()