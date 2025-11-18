import socket
import struct
import sys
import os


def recv_exactly(sock, n):
    """Читает ровно n байт из сокета. Блокирует, пока не получит все."""
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise RuntimeError("Сервер закрыл соединение")
        buf += chunk
    return buf


def send_rinex(host: str, port: int, filepath: str, filepath2: str):
    if not os.path.isfile(filepath):
        print(f"Ошибка: файл не найден — {base_filepath}")
        return

    if not os.path.isfile(filepath2):
        print(f"Ошибка: файл не найден — {rover_filepath}")
        return
    
    with open(base_filepath, 'rb') as f:
        base_file_data = f.read()
    base_filename = os.path.basename(base_filepath)

    with open(rover_filepath, 'rb') as f:
        rover_file_data = f.read()
    rover_filename = os.path.basename(rover_filepath)


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        # --- Отправка файла ---
        s.sendall(struct.pack('>I', len(base_filename)))      # длина имени (4 байта)
        s.sendall(base_filename.encode('utf-8'))              # имя файла
        s.sendall(struct.pack('>Q', len(base_file_data)))     # размер файла (8 байт)
        s.sendall(base_file_data)                             # содержимое

        # --- Отправка файла ---
        s.sendall(struct.pack('>I', len(rover_filename)))      
        s.sendall(rover_filename.encode('utf-8'))              
        s.sendall(struct.pack('>Q', len(rover_file_data)))     
        s.sendall(rover_file_data)                                                  

        # --- Приём ответа ---
        # Читаем первые 4 байта для определения типа ответа
        prefix = recv_exactly(s, 4)

        if prefix == b"OK::":
            # Успех: читаем 8 байт — длину результата
            size_bytes = recv_exactly(s, 8)
            result_size = struct.unpack('>Q', size_bytes)[0]

            # Читаем сам результат (ровно result_size байт)
            result = recv_exactly(s, result_size)

            print("\n=== Результат обработки ===")
            print(result.decode('utf-8'))

        elif prefix.startswith(b"ERR"):  # например, b"ERRO" от "ERROR:..."
            # Дочитываем остаток сообщения об ошибке
            rest = s.recv(1024)
            full_error = (prefix + rest).decode('utf-8', errors='replace')
            print("Сервер вернул ошибку:", full_error)

        else:
            print("Некорректный ответ от сервера:", repr(prefix))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Использование: python client.py <путь_к_файлу.obs>")
        sys.exit(1)
    send_rinex('localhost', 9999, sys.argv[1])
