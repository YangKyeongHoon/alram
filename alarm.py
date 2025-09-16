
import time
import os
import platform
import threading
import sys
import tty
import termios
import select

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
    """키 입력을 실시간으로 감지하여 'q' 또는 ESC가 눌리면 stop_event를 설정합니다."""
    old_settings = termios.tcgetattr(sys.stdin.fileno())
    try:
        tty.setcbreak(sys.stdin.fileno())
        while not stop_event.is_set():
            if select.select([sys.stdin], [], [], 0.1)[0]:
                char = sys.stdin.read(1)
                if char == 'q' or char == '\x1b':  # '\x1b'는 ESC 키의 ASCII 코드
                    print("\n종료 키 입력됨. 프로그램 종료 중...")
                    stop_event.set()
                    break
    finally:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)

def main():
    """
    알람 및 입력 감지 스레드를 시작하고 종료를 관리합니다.
    """
    stop_event = threading.Event()
    print("알람 프로그램을 시작합니다. 종료하려면 'q' 또는 'ESC' 키를 누르세요.")

    alarm_thread = threading.Thread(target=alarm_worker, args=(stop_event,))
    input_thread = threading.Thread(target=input_listener, args=(stop_event,))

    alarm_thread.start()
    input_thread.start()

    alarm_thread.join()
    input_thread.join()

    print("알람 프로그램을 종료합니다.")

if __name__ == "__main__":
    main()
