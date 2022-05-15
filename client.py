import socket
from os.path import exists

from time import sleep

import sys


filename=sys.argv[1] 

cache = {}
index = 1


def compose_request(method, filename, hostname, port):
    if method == 'GET':
        request = "GET /%s HTTP/1.1\r\nHost:%s:%s\r\n\r\n" % (filename, hostname, port)
    else:
        request = "POST /%s HTTP/1.1\r\nHost:%s:%s\r\n\r\n" % (filename, hostname, port)
        file_exists = exists(filename)
        if file_exists:
            with open(filename) as file:
                payload = file.read()
                request += payload + "\r\n"
        else:
            print("File you're trying to access does not exist!")
            return 0

    return request


with open(filename) as f:
    operations = [operation.rstrip() for operation in f]

for operation in operations:
    method = operation.split()[0]
    filename = operation.split()[1][1:]
    hostname = operation.split()[2]
    no_of_words = len(operation.split(' '))
    if no_of_words < 4:
        port = 80
    else:
        port = int(operation.split()[3])
    output_request = compose_request(method, filename, hostname, port)

    if output_request == 0:
        print("Invalid Request....Will not be connected to server!")
        continue

    cached = 0
    for key in cache:
        if output_request in cache[key]['Request']:
            cached = 1
            print("Found in Cache!")
            print(cache[key]['Response'])
            if method == "GET":
                if cache[key]['Response'].split()[1] == "200":
                    print("Requested File content: \n" + cache[key]['Content'])

    if cached:
        continue

    print("Not found in cache....\n Connecting to server")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((hostname, port))
            print("Connected to server.")
            request_in_bytes = output_request.encode()
            s.sendall(request_in_bytes)
            cache[index] = {}
            cache[index]['Request'] = output_request
            print("Request is sent.")
            response = s.recv(4096).decode()
            cache[index]['Response'] = response
            print(response)
            if method == 'GET':
                if response.split()[1] == "200":
                    received_data = response.partition("\r\n\r\n")[2]
                    fp = open("client" + filename, "w")
                    fp.write(received_data)
                    cache[index]['Content'] = received_data
                    fp.close()

        except ConnectionRefusedError:
            print(f"Failed to connect with server - {hostname}:{port}!")
        sleep(2)
    index = index + 1


