# import socket programming library
import socket
# import thread module
from _thread import start_new_thread
import threading
import json
from json.decoder import JSONDecodeError
from adafruit_motorkit import MotorKit

print_lock = threading.Lock()
kit = MotorKit()


def move_forward(angle, strength):
    
    if angle != 0:
        strength_2 = strength - strength / (180 / abs(angle))
    else:
        strength_2 = strength
        
    if strength_2 > 1:
        strength_2 = 1
    elif strength_2 < -1:
        strength_2 = -1
        
    if angle > 0:
        print("move_forward, right:", strength_2, 'left:', strength)
        kit.motor1.throttle = strength_2
        kit.motor2.throttle = strength_2
        kit.motor3.throttle = strength
        kit.motor4.throttle = strength
    elif angle < 0:
        print("move_forward, right:", strength, 'left:', strength_2)
        kit.motor1.throttle = strength
        kit.motor2.throttle = strength
        kit.motor3.throttle = strength_2
        kit.motor4.throttle = strength_2
    else:
        print("move_forward, straight", strength)
        kit.motor1.throttle = strength
        kit.motor2.throttle = strength
        kit.motor3.throttle = strength
        kit.motor4.throttle = strength


def move_backward(angle, strength):
    print("move_backward")
    move_forward(angle, -strength)


def stop():
    print("stop")
    kit.motor1.throttle = 0
    kit.motor2.throttle = 0
    kit.motor3.throttle = 0
    kit.motor4.throttle = 0


def race(cmd):
    direction = cmd['direction']
    angle = cmd['angle']
    strength = -cmd['strength'] / 100
    
    if strength > 1:
        strength = 1
    elif strength < -1:
        strength = -1
    
    if direction == 1:
        move_forward(angle, strength)
    elif direction == -1:
        move_backward(angle, strength)
    else:
        stop()


# thread function
def threaded(client, addr):
    while True:
        # data received from client
        data = client.recv(1024)
        if not data:
            print('Disconn from:', addr[0] + ':' + str(addr[1]))

            # lock released on exit
            print_lock.release()
            break

        try:
            cmd = json.loads(data.decode('utf-8'))
            print('Message from:', addr[0] + ':' + str(addr[1]), cmd)
            race(cmd)
        except JSONDecodeError:
            print("An exception occurred")
            print('Message from:', addr[0] + ':' + str(addr[1]), cmd)
        # finally:
        client.sendall("33333\n".encode())

    # connection closed
    client.close()


def main():
    stop()
    host = ""
    port = 9999

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    max_conn = 5
    s.listen(max_conn)
    print('Socket is listening on poet', port, 'max connections:', str(max_conn))

    # a forever loop until client wants to exit
    try:
        while True:
            # establish connection with client
            client, addr = s.accept()

            # lock acquired by client
            print_lock.acquire()
            print('Connected to:', addr[0] + ':' + str(addr[1]))

            # Start a new thread and return its identifier
            start_new_thread(threaded, (client, addr,))

    except KeyboardInterrupt:
        s.close()
        print('Keyboard Interrupt!')


if __name__ == '__main__':
    main()
