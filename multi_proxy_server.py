#!/usr/bin/env python3
import socket, time, sys
from multiprocessing import Process

#define global address and buffer size
HOST = ""
PORT = 8001
BUFFER_SIZE = 1024

# get ip
def get_remote_ip(extern_host):
    print('Getting IP for {host}')
    try:
        remote_ip = socket.gethostbyname(host)
    except socket.gaierror:
        print('Hostname could not be resolved. Exiting...')
        sys.exit()
    
    print(f'IP address of {host} is {remote_ip}')
    return remote_ip

def handle_request(addr, conn, proxy_end):
    print("Getting data...")
    send_full_data = conn.recv(BUFFER_SIZE)
    print("Sending received data to google")
    proxy_end.sendall(send_full_data)
    proxy_end.shutdown(socket.SHUT_WR)
    data = proxy_end.recv(BUFFER_SIZE)
    print("Sending received data to client")
    conn.send(data)

def main():
    # establish localhost, extern_host (google), port, buffer size
    extern_host = 'www.google.com'
    port = 80

    # establish "start" of proxy (connects to localhost)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_start:
        print("Starting multiprocessing proxy server")
        # bind, and set to listening mode
        proxy_start.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy_start.bind((HOST, PORT))
        proxy_start.listen(1)

        while True:
            # accept incoming connections from proxy_start, print information about connection
            conn, addr = proxy_start.accept()
            print("Connected by", addr)

            # establish "end" of proxy (connects to google)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_end:
                # TODO: get remote IP of google, connect proxy_end to it
                print("Connecting to Google")
                remote_ip = get_remote_ip(extern_host)
                proxy_end.connect((remote_ip, port))

                # allow for multiple connections with a Process daemon
                p = Process(target = handle_request(addr, conn, proxy_end), args = (addr, conn, proxy_end))
                p.daemon = True
                p.start()
                print("Started process ", p)
            
            # close the connection
            conn.close()

if __name__ == "__main__":
    main()