import base64
import socket
import tqdm
import os
from Crypto.Cipher import AES

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 32768

key = 'iamonlyonesonali'
key_bytes = key.encode('utf-8') 

# cipher = AES.new(key, AES.MODE_EAX, nonce)

HOST_IP = socket.gethostbyname(socket.gethostname())
HOST_PORT = 9999
print(HOST_IP)


def bindSocket():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST_IP, HOST_PORT))
        print("Socket bind successful...")
    except:
        print("Error binding the receiver socket!")
    return server

def startReceiving(server_socket):
    server_socket.listen()

    client, sender_address = server_socket.accept()
    print(f"[+] {sender_address} is connected.")

    received = client.recv(1024).decode()
    received= received.split(SEPARATOR)
    tag_str = received[0]
    tag_bytes = base64.b64decode(tag_str.encode('utf-8'))
    nonce_str = received[1]
    nonce_bytes = base64.b64decode(nonce_str.encode('utf-8'))

    file_size=received[2]
    file_name=received[3]
    # file_name, file_size = received.split(SEPARATOR)
    file_name = os.path.basename(file_name)
    file_size = int(file_size)
    print("Receiving details: ", file_name, file_size)

    file = open("received/" + file_name, "wb")

    progress = tqdm.tqdm(
        range(file_size),
        f"Receiving {file_name}",
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    )

    done=False
    file_bytes=b""
    while not done:
        data = client.recv(1024)
        if file_bytes[-5:]== b"<END>":
            done = True
        else: 
            file_bytes+=data
        # progress.update(1024)
        progress.update(len(file_bytes))

    cipher = AES.new(key_bytes, AES.MODE_EAX, nonce=nonce_bytes)
    plaintext = cipher.decrypt(file_bytes[:-5])
    try:
        cipher.verify(tag_bytes)
        file.write(plaintext)
    except:
        print("failure")
    # while True:
    #     bytes_read = client.recv(BUFFER_SIZE)
    #     if not bytes_read:
    #         break
    #     file.write(cipher.decrypt(bytes_read))
    #     progress.update(len(bytes_read))
    file.close()
    client.close()


def closeSocket(server_socket):
    server_socket.close()
    print("Socket closed")
