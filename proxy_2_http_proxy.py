# qinhuawei@outlook.com
import socketserver,argparse,threading,socket,logging,select,time

g_proxy_ip = None
g_proxy_port = None
g_client_ips = None

class https_proxy(socketserver.StreamRequestHandler):
    def handle(self):
        peer_host, peer_port = self.connection.getpeername()
        print('--{}:{}--'.format(peer_host, peer_port))
        if not peer_host in g_client_ips:
            print('Only permit [{}].'.format(args.client_ip))
            return

        self.client_sock = socket.create_connection((g_proxy_ip, g_proxy_port))
        def thr_client_sock_recv():
            while True:
                try:
                    buff = self.client_sock.recv(65535)
                    if buff:
                        self.connection.send(buff)
                    else:
                        return
                except:
                    logging.exception('thr_client_sock_recv')
                    return

        def thr_cleint_sock_send():
            while self.client_sock.fileno():
                try:
                    buff = self.connection.recv(65535)
                    if buff:
                        self.client_sock.send(buff)
                    else:
                        return
                except:
                    logging.exception('thr_cleint_sock_send')
                    return

        t_recv = threading.Thread(target=thr_client_sock_recv, args=())
        t_send = threading.Thread(target=thr_cleint_sock_send, args=())
        t_recv.start()
        t_send.start()
        t_send.join()
        t_recv.join()
        self.client_sock.close()
        self.connection.close()
        print('--{}:{}--END'.format(peer_host, peer_port))

def get_local_ip(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((ip, port))
        return s.getsockname()[0]
    finally:
        s.close()
    return ''

if __name__ == "__main__":
    description = '''proxy_2_http_proxy: forward http(s) to http_proxy server. qinhuawei@outlook.com
  Client_PC ---->  Laptop     ---->     HTTP_PROXY    ---->   Internet
   10.0.0.2        20.0.0.2             30.0.0.2:8888
-c 10.0.0.2      -l 0.0.0.0:1234     -p 30.0.0.2:8888
EXAMPLE: python proxy_2_http_proxy.py -c 10.0.0.2 -p 30.0.0.2:8888
On client_PC:
export http_proxy=http://20.0.0.2:1234
If HTTP_PROXY need password authentication, please put your password on client_PC as example:
export http_proxy=http://username:password@20.0.0.2:1234

HTTPS cert issue, please visit https://github.com/qin-neo/proxy_2_http_proxy
'''
    parser_t = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser_t.add_argument('-l', dest='local_ip_port', type=str, required=False, default='0.0.0.0:1234',  help='local IP Port for client visit, default 0.0.0.0:1234')
    parser_t.add_argument('-c', dest='client_ip', type=str, required=True, help='client IP, example: 10.0.0.2,10.0.0.3')
    parser_t.add_argument('-p', dest='proxy_ip_port', type=str, required=True, help='The Real HTTP_PROXY IP:PORT, example:30.0.0.2:8888')
    args = parser_t.parse_args()

    local_ip, local_port = args.local_ip_port.split(':')
    local_port = int(local_port)
    g_proxy_ip, g_proxy_port = args.proxy_ip_port.split(':')
    g_proxy_port = int(g_proxy_port)
    g_client_ips = args.client_ip.split(',')
    g_client_ips.append('127.0.0.1')

    if local_ip == '0.0.0.0':
        ip_2_client = get_local_ip(g_client_ips[0], 8000)
    else:
        ip_2_client = local_ip

    tcp_server = socketserver.ThreadingTCPServer((local_ip, local_port), https_proxy)
    print("Local {}:{}, remote {}".format(local_ip, local_port, args.proxy_ip_port))
    if ip_2_client:
        print ("export http_proxy=http://{}:{}".format(ip_2_client, local_port))
        print ("export https_proxy=http://{}:{}".format(ip_2_client, local_port))
    tcp_server.serve_forever()

