# proxy_2_http_proxy
```
proxy_2_http_proxy: forward http(s) to http_proxy server. qinhuawei@outlook.com
optional arguments:
  -h, --help              show this help message and exit>
  --local_port LOCAL_PORT local PORT, default 1234                   
  --local_ip LOCAL_IP     local server IP, default 0.0.0.0
  -c CLIENT_IP            client IP, Only forward this IP request
  -r REMOTE_SERVER_IP     HTTP_PROXY Server IP
  -p REMOTE_SERVER_PORT   HTTP_PROXY Server PORT

   Client    ---->    Laptop     ---->     HTTP_PROXY    ---->   Internet
  10.0.0.2           20.0.0.2              30.0.0.2:8888

Laptop visit Internet
                http_porxy=http://user:pass@30.0.3.2:8888
               https_proxy=http://user:pass@30.0.3.2:8888

Client visit Internet:
# laptop run proxy_2_http_proxy.py*
                  python3 proxy_2_http_proxy.py -r 30.0.3.2 - p 8888 -c 10.0.0.2
# client config http_proxy*
 http_porxy=http://user:pass@20.0.0.2:8888
https_proxy=http://user:pass@20.0.0.2:8888
```
