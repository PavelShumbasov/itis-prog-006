import socket
from _thread import start_new_thread

host = 'localhost'
port = 5555
ENCODING = "UTF-8"
DATA_SIZE = 1024
count_thread = -1
all_clients = []

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Сокет, работающий по протоколу IPv4 на потоках
server_socket.bind((host, port))  # Привязали сокет к порту на компьютере
server_socket.listen(5)


def chat_with_client(connection, number_thr):
    if number_thr % 2 == 0:
        partner_numb = number_thr + 1
        welcome_message = "Вы успешно подключились! \nЖдем подключение собеседника."
    else:
        partner_numb = number_thr - 1
        welcome_message = "Вы успешно подключились! \nСобеседник ожидает вас."

    connection.send(str.encode(welcome_message))

    while True:
        data = connection.recv(DATA_SIZE).decode(ENCODING)
        print(data)
        if not data:
            break

        if partner_numb < len(all_clients):
            all_clients[partner_numb].send(str(" " * 30 + data).encode(ENCODING))
        else:
            connection.send("Ваш собеседник ещё не подключился".encode(ENCODING))

    connection.close()


while True:
    connection, address = server_socket.accept()
    if not connection or len(all_clients) >= 100:
        break

    print(f"Новое соединение: {address}")
    count_thread += 1
    all_clients.append(connection)

    start_new_thread(chat_with_client, (connection, count_thread,))

server_socket.close()
