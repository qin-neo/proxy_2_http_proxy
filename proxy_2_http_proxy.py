# qinhuawei@outlook.com
import socketserver,argparse,threading,socket,logging,select,time

class https_proxy(socketserver.StreamRequestHandler):
    def handle(self):
        peer_host, peer_port = self.connection.getpeername()
        print('--{}:{}--'.format(peer_host, peer_port))
        if args.client_ip and args.client_ip != peer_host:
            print('Only permit {}.'.format(args.client_ip))
            return

        self.client_sock = socket.create_connection((args.remote_server_ip, args.remote_server_port))
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

if __name__ == "__main__":
    parser_t = argparse.ArgumentParser(description="proxy_2_http_proxy: forward http(s) to http_proxy server. qinhuawei@outlook.com")
    parser_t.add_argument('--local_port', dest='local_port', type=int, required=False, default=1234,  help='local PORT, default 1234')
    parser_t.add_argument('--local_ip', dest='local_ip', type=str, required=False, default='0.0.0.0',  help='local server IP, default 0.0.0.0')
    parser_t.add_argument('-c', dest='client_ip', type=str, required=False, default='',  help='client IP, Only forward this IP request')
    parser_t.add_argument('-r', dest='remote_server_ip', type=str, required=True, help='HTTP_PROXY Server IP')
    parser_t.add_argument('-p', dest='remote_server_port', type=int, required=True, help='HTTP_PROXY Server PORT')
    args = parser_t.parse_args()

    tcp_server = socketserver.ThreadingTCPServer((args.local_ip, args.local_port), https_proxy)
    print ("Local {}:{}, remote {}:{}".format(args.local_ip, args.local_port, args.remote_server_ip, args.remote_server_port))
    tcp_server.serve_forever()

