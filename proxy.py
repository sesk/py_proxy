import socket
import ssl
import threading
import sys
import logging
import subprocess

logging.basicConfig(filename = "proxy.log", level = logging.DEBUG, format = "%(asctime)s - %(message)s")

def proxy_thread(client, data):
    req = b''

    logging.info("Получаем запрос")
    client.settimeout(0.1)
    while data:
        req += data
        try:
            data = client.recv(1024)
        except socket.error:
            break

    logging.info(req)

    serv = ssl.wrap_socket(socket.socket())
    serv.connect( ('server_url', 443) )

    logging.info("Отправляем запрос на сервер")
    serv.send(req)

    logging.info("Получаем ответ сервера")
    resp = b''
    serv.settimeout(1)
    data = serv.recv(1024)
    while data:
        resp += data
        try:
            data = serv.recv(1024)
        except socket.error:
            break

    logging.info(resp)

    logging.info("Отдаем ответ клиенту")
    client.send(resp)
    

def main_thread():
    logging.info("Старт главного потока");

    sock = ssl.wrap_socket(socket.socket(), 'proxy.key', 'proxy.crt', True)
    sock.bind( ('localhost', 43433) )
    sock.listen(10)

    while True:
        logging.info("Ждем входящее соединение");
        conn, addr = sock.accept()

        data = conn.recv(4)
        if data == b'STOP':
            break

        logging.info("Получен запрос")
        t = threading.Thread(target = proxy_thread, args = ( conn, data ) )
        t.run()
    logging.info("Остановка")

def start():
    logging.info("Запуск");
    subprocess.Popen("py proxy.py daemon", creationflags=0x08000000, close_fds=True)

def stop():
    logging.info("Останов");

    me = ssl.wrap_socket(socket.socket())
    me.connect( ('localhost', 43433) )
    me.send(b'STOP')
    me.close()

def run():
    if sys.argv[1] == "start":
        start();
    elif sys.argv[1] == "stop":
        stop();
    elif sys.argv[1] == "daemon":
        main_thread();
    else:
        print("Неизвестная комманда ", sys.argv[1])

if len(sys.argv) > 1:
    run()
else:
    print("Запускайте с параметром start - запуск, stop - останов");
       
