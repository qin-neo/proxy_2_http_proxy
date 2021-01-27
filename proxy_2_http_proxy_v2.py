# qinhuawei@outlook.com
import logging,threading,socket,socks,getpass,argparse,select
from urllib.parse import urlparse

def getaddrinfo(*args):
    if not args[0]:
        return socket_getaddrinfo(*args)
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]

socket.socket = socks.socksocket
socket_getaddrinfo = socket.getaddrinfo
socket.getaddrinfo = getaddrinfo

class https_proxy():
    def __init__(self, client_sock, client_addr):
        headers= {}
        header=''

        while True:
            header = client_sock.recv(65535).decode()
            index=header.find('\n')
            if index >0:
                break
        first_row = header[:index]
        headers['method'], headers['path'], headers['protocol'] = first_row.split()

        url=urlparse(headers['path'])
        if url.scheme == 'http':
            #logging.info(url)
            if url.path.count(':'):
                ip, port = url.netloc.split(':')
            else:
                ip = url.netloc
                port = 80
            proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            proxy_sock.connect((ip, int(port)))
            proxy_sock.sendall(header.encode())

            inputs  = [proxy_sock, client_sock]
            outputs = []
            while True:
                readable, writable, exceptional = select.select(inputs, outputs, inputs)
                try:
                    for s in readable:
                        if proxy_sock == s:
                            client_sock.sendall(proxy_sock.recv(512))
                        else:
                            proxy_sock.sendall(client_sock.recv(512))
                except:
                    logging.exception('------http------')
                    break
            return
        else:
            logging.info(url.path)
            ip, port = url.path.split(':')

        try:
            proxy_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            proxy_sock.connect((ip, int(port)))
            client_sock.send('HTTP/1.1 200 Connection established\r\nDate: Thu, 08 Oct 2020 08:28:59 CST\r\nVia: 1.1 NEO.QIN-PROXY\r\n\r\n'.encode())
        except:
            logging.exception('------------')

        def client_sock_recv():
            while True:
                try:
                    buff = client_sock.recv(65535)
                    if buff:
                        proxy_sock.send(buff)
                    else:
                        return
                except:
                    logging.exception('client_sock_recv')
                    return

        def proxy_sock_recv():
            while True:
                try:
                    buff = proxy_sock.recv(65535)
                    if buff:
                        client_sock.send(buff)
                    else:
                        return
                except:
                    logging.exception('proxy_sock_recv')
                    return

        t_recv = threading.Thread(target=client_sock_recv, args=())
        t_send = threading.Thread(target=proxy_sock_recv, args=())
        t_recv.start()
        t_send.start()
        t_send.join()
        t_recv.join()
        client_sock.close()
        proxy_sock.close()
        logging.info(f'---- {client_addr} end ----')

class tcp_server():
    def __init__(self, host, port, client_ips, handler=https_proxy):
        server_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server_sock.bind((host,port))
        server_sock.listen()

        while True:
            try:
                client_sock, client_addr = server_sock.accept()
                client_ip, _ = client_addr
                if not client_ip in client_ips:
                    client_sock.close()
                    logging.warning('{} not in {}'.format(client_ip, client_ips))
                    continue
                logging.info(f'---- {client_addr} connected ----')
                threading.Thread(target=handler, args=(client_sock, client_addr)).start()
            except KeyboardInterrupt:
                return
            except:
                logging.exception('------------')

def get_local_ip(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        return s.getsockname()[0]
    finally:
        s.close()
    return ''

if __name__ == "__main__":
    log_format = "%(asctime)-15s %(levelname).4s %(filename)s:%(lineno)-4d %(message)s"
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logging.Formatter(log_format))
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)
    rootLogger.addHandler(consoleHandler)

    description = '''proxy_2_http_proxy: forward http(s) to http_proxy server. qinhuawei@outlook.com
  Client_PC ---->  Laptop     ---->     HTTP_PROXY    ---->   Internet
   10.0.0.2        20.0.0.2             30.0.0.2:8888
-c 10.0.0.2      -l 0.0.0.0:1234     -p 30.0.0.2:8888
EXAMPLE: python proxy_2_http_proxy_v2.py -c 10.0.0.2 -p 30.0.0.2:8888 -u proxy_username
On client_PC:
export https_proxy=http://20.0.0.2:1234

HTTPS cert issue, please visit https://github.com/qin-neo/proxy_2_http_proxy
'''
    parser_t = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser_t.add_argument('-l', dest='local_ip_port', type=str, required=False, default='0.0.0.0:1234',  help='local IP Port for client visit, default 0.0.0.0:1234')
    parser_t.add_argument('-c', dest='client_ip', type=str, required=True, help='client IP, example: 10.0.0.2,10.0.0.3')
    parser_t.add_argument('-p', dest='proxy_ip_port', type=str, required=True, help='The Real HTTP_PROXY IP:PORT, example:30.0.0.2:8888')
    parser_t.add_argument('-u', dest='user_pass', type=str, required=True, help='Username with password input or username:password')
    args = parser_t.parse_args()

    local_ip, local_port = args.local_ip_port.split(':')
    local_port = int(local_port)
    proxy_ip, proxy_port = args.proxy_ip_port.split(':')
    proxy_port = int(proxy_port)

    client_ips = args.client_ip.split(',')
    client_ips.append('127.0.0.1')

    if local_ip == '0.0.0.0':
        ip_2_client = get_local_ip(proxy_ip, proxy_port)
    else:
        ip_2_client = local_ip
        client_ips.append(local_ip)
    
    if args.user_pass.count(':'):
        usename, password = args.user_pass.split(':')
    else:
        usename = args.user_pass
        password = getpass.getpass(prompt='Password: ', stream=None)

    logging.info('============== START ==============')
    socks.set_default_proxy(socks.HTTP, addr=proxy_ip, port=proxy_port, username=usename, password=password)
    logging.info("Local {}:{}, remote {}".format(local_ip, local_port, args.proxy_ip_port))
    if ip_2_client:
        logging.info("export https_proxy=http://{}:{}".format(ip_2_client, local_port))
    tcp_server(local_ip, local_port, client_ips)
