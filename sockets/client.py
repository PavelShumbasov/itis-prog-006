import socket
from threading import Thread

host = 'localhost'
port = 5555
ENCODING = "UTF-8"
DATA_SIZE = 1024

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


client_socket.connect((host, port))
server_response = client_socket.recv(DATA_SIZE)
print(server_response.decode(ENCODING))


def get_messages():
    while True:
        server_response = client_socket.recv(DATA_SIZE)
        if not server_response:
            break

        print(server_response.decode(ENCODING))


def send_messages():
    while True:
        message = input()
        if not message:
            break
        client_socket.send(message.encode(ENCODING))


thread1 = Thread(target=get_messages)
thread2 = Thread(target=send_messages)

thread1.start()
thread2.start()

thread1.join()
thread2.join()

client_socket.close()