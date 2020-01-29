# import socket programming library
import socket
# import thread module
from _thread import start_new_thread
import threading

print_lock = threading.Lock()


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

        # reverse the given string from client
        # data = data[::-1]

        # send back reversed string to client
        print('Message from:', addr[0] + ':' + str(addr[1]), data.decode('utf-8'))
        client.send(data)

    # connection closed
    client.close()


def main():
    host = ""
    port = 9999

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        print('Keyboard Interrupt!')
        s.close()


if __name__ == '__main__':
    main()
