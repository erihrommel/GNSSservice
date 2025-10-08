import socket
#Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Bind socket
server_address = ('localhost', 8000)
server_socket.bind(server_address)

#Слушать клиента (1)
server_socket.listen(1)
print(f'Сервер запущен: {server_address}')

while True:
    client_socket, client_address = server_socket.accept()
    print(f' Подключен клиент {client_address}')

    try:
        data = client_socket.recv(1024)
        if data:
            print(f'получено {data.decode("UTF-8")}')
            response = "Привет от сервера"
            client_socket.sendall(response.encode('UTF-8'))

    finally:
        client_socket.close()