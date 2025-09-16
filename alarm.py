
import time
import os
import platform
import threading
import sys
import tty
import termios
import select

# 프로그램의 주 반복 루프를 제어하는 전역 플래그
KEEP_RUNNING = True

def alarm_worker(stop_event):
    """
    별도 스레드에서 알람 로직을 실행하는 함수.
    stop_event가 설정되면 작업을 중단합니다.
    """
    try:
        print("첫 알람은 30분 후에 울립니다.")
        if stop_event.wait(timeout=30 * 60):
            return

        alarm_message = "첫 번째 알람입니다. 일어나세요!"
        print(f"\n*** {alarm_message} ***")
        if platform.system() == "Darwin":
            os.system(f'say "{alarm_message}"')

        while not stop_event.is_set():
            print("\n3분 후에 다음 알람이 울립니다.")
            if stop_event.wait(timeout=3 * 60):
                break

            if not stop_event.is_set():
                alarm_message = "3분 간격 알람입니다."
                print(f"\n*** {alarm_message} ***")
                if platform.system() == "Darwin":
                    os.system(f'say "{alarm_message}"')
    except Exception as e:
        print(f"알람 스레드에서 오류 발생: {e}")

def input_listener(stop_event):
    """'q'는 현재 실행을 중지(재시작), 'ESC'는 프로그램을 영구 종료시킵니다."""
    global KEEP_RUNNING
    old_settings = termios.tcgetattr(sys.stdin.fileno())
    try:
        tty.setcbreak(sys.stdin.fileno())
        while not stop_event.is_set():
            if select.select([sys.stdin], [], [], 0.1)[0]:
                char = sys.stdin.read(1)
                if char == 'q':
                    print("\n알람을 재시작합니다...")
                    stop_event.set()  # 현재 주기만 중단
                    break
                elif char == '\x1b':  # ESC 키
                    print("\n프로그램을 영구적으로 종료합니다...")
                    KEEP_RUNNING = False  # 주 반복 루프 중단
                    stop_event.set()      # 현재 주기도 중단
                    break
    finally:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)

def main():
    """
    KEEP_RUNNING 플래그가 True인 동안 알람/입력 스레드를 반복적으로 시작합니다.
    """
    global KEEP_RUNNING
    while KEEP_RUNNING:
        print("\n알람 프로그램을 시작합니다. ('q' 키: 재시작, 'ESC' 키: 영구 종료)")
        stop_event = threading.Event()
        
        alarm_thread = threading.Thread(target=alarm_worker, args=(stop_event,))
        input_thread = threading.Thread(target=input_listener, args=(stop_event,))

        alarm_thread.start()
        input_thread.start()

        alarm_thread.join()
        input_thread.join()

        if KEEP_RUNNING:
            time.sleep(1) # 재시작 전 잠시 대기

    print("알람 프로그램이 완전히 종료되었습니다.")

if __name__ == "__main__":
    main()
