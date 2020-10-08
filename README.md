# proxy_2_http_proxy
```
usage: proxy_2_http_proxy.py [-h] [-l LOCAL_IP_PORT] -c CLIENT_IP -p PROXY_IP_PORT

proxy_2_http_proxy: forward http(s) to http_proxy server. qinhuawei@outlook.com

  Client_PC ---->  Laptop     ---->     HTTP_PROXY    ---->   Internet
   10.0.0.2        20.0.0.2             30.0.0.2:8888
-c 10.0.0.2      -l 0.0.0.0:1234     -p 30.0.0.2:8888

EXAMPLE: python proxy_2_http_proxy.py -c 10.0.0.2 -p 30.0.0.2:8888
On client_PC:
export http_proxy=http://20.0.0.2:1234
If HTTP_PROXY need password authentication, please put your password on client_PC as example:
export http_proxy=http://username:password@20.0.0.2:1234

HTTPS cert issue, please visit https://github.com/qin-neo/proxy_2_http_proxy

optional arguments:
  -h, --help        show this help message and exit
  -l LOCAL_IP_PORT  local IP Port for client visit, default 0.0.0.0:1234
  -c CLIENT_IP      client IP, example: 10.0.0.2,10.0.0.3
  -p PROXY_IP_PORT  The Real HTTP_PROXY IP:PORT, example:30.0.0.2:8888

HTTPS cert issue, please visit https://github.com/qin-neo/proxy_2_http_proxy
```

## On Client, if met SSL: CERTIFICATE_VERIFY_FAILED or simular error,
Please import HTTP_PROXY certificate into client OS.
1. Find root ca. On Windows, the root path is: 
> iexplore -> Internet选项 -> 内容 -> 证书 -> 受信任的根证书颁发机构 -> (your http_proxy cert)
2. Export it, then copy to Client.
3. Import Client. On Linux, the cert should be .crt format.
```
openssl x509 -inform DER -in http_proxy_cert.cer -out http_proxy_cert.crt
yum install ca-certificates -y
cp http_proxy_cert.crt /etc/pki/ca-trust/source/anchors/
update-ca-trust
```
