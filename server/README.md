# cpen491/server/
directory for the **webserver** component of the project


## Development and local usage
Setting up dev environment (do once):
```bash
# create virtual environment
$ virtualenv venv

# activate virtual environment (POSIX)
$ source venv/bin/activate

# windows
$ source venv/scripts/activate

# install server dependencies
$ pip install 

# Optionally manually create sqlite database (requires sqlite3 binaries)
$ cd /db
$ sqlite3 [db_name] (this step requires sqlite3 binaries)
$ sqlite> .read [init.sql or init_with_data.sql]
$ sqlite> .quit
```

Launch project locally for development:
```bash
# start virtual environment if not yet done
$ source venv/bin/activate

# start server with the default database
$ python server.py

# start server with a custom database (will create sqlite database file within /db if it does not already exist)
$ python server.py [db_path]
```



# Production Server

## HTTPS setup
ACME.sh is a free Automated Certificate Management Environment that registers certificates through Let's Encrypt Certificate Authority. To install run:

```bash
$ curl https://get.acme.sh | sh
```

Generate SSL certs
```bash
$ sudo su
# service nginx stop
# acme.sh --issue --standalone -d YOUR.DOMAIN.com
# service nginx start
```

copy the SSL certs to ```/var/www/cert``` then edit nginx.conf in ```/etc/nginx/sites-enabled/server```
```bash
# cp -r ~/.acme.sh/YOUR.DOMAIN.com /var/www/cert/
# chmod 660 -R /var/www/cert/YOUR.DOMAIN.com
...
    ##modify nginx.conf
...
# service nginx reload
```

Next change the nginx settings to use the SSL certs and force all http requests to https
```/etc/nginx/sites-enabled/server```:
```
server {                                                                                                  
    listen 80;                                                                                            
    listen [::]:80;                                                                                       
                                                                                                          
    return 301 https://$host$request_uri;                                                                 
}                                                                                                         
                                                                                                          
server {                                                                                                  
    listen 443 default_server ssl;                                                                        
    ssl_certificate /var/www/cert/YOUR.DOMAIN.com/YOUR.DOMAIN.com.cer;    
    ssl_certificate_key /var/www/cert/YOUR.DOMAIN.com/YOUR.DOMAIN.com.key;
                                                                                                          
    server_name YOUR.DOMAIN.com;                                                              
                                                                                                          
    location / {                                                                                          
        include proxy_params;                                                                             
        proxy_pass http://unix:/home/ubuntu/cpen491/server/server.sock;                                   
        proxy_http_version 1.1;                                                                           
        proxy_set_header Upgrade $http_upgrade;                                                           
        proxy_set_header Connection 'upgrade';                                                            
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;                                      
        proxy_set_header Host $host;                                                                      
        proxy_cache_bypass $http_upgrade;                                                                 
    }                                                                                                     
}                                                                                                         
```

To setup certificate auto-renew run the acme script again:
```bash
acme.sh --install-cert -d www.joincartel.com
  --key-file       /var/www/cert/YOUR.DOMAIN.com/YOUR.DOMAIN.com.key
  --fullchain-file /var/www/cert/YOUR.DOMAIN.com/fullchain.cer
  --reloadcmd     "service nginx force-reload"
```
This will auto-renew the certificate every 60 days by default.

## Setup on Ubuntu 16.04 Amazon EC2 instance

[Gunicorn](http://gunicorn.org/) is used as http server.

[Nginx](https://www.nginx.com/) acts as a reverse proxy to take in traffic on port 80.
 
There is a systemd unit file in ```/etc/systemd/system/server.service``` that
configures the instance to run gunicorn on startup (0.0.0.0:5000).

Nginx setup is in ```/etc/nginx/sites-available```, symlinked to ```/etc/nginx/sites-enabled```

## Usage
Contact someone with access to the server to get your RSA public key onto the
server.  SSH into the server with:

```bash
$ ssh ubuntu@ec2-18-216-40-147.us-east-2.compute.amazonaws.com
```

If you need to restart the server (ie. after a ```git pull```) run:

```bash
$ sudo systemctl restart server
```

## Debugging Production Issues

Check that Nginx is up and listening on port 80:
```bash
$ netstat -plnt

# expected output
(Not all processes could be identified, non-owned process info
 will not be shown, you would have to be root to see it all.)
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      -
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -
tcp6       0      0 :::22                   :::*                    LISTEN      -
``` 

Nginx logs are in ```/var/logs/nginx```

You can check Gunicorn status with:
```bash
$ sudo systemctl status server
```

If for any reason Gunicorn is not up and running (it should fire up on boot):
```bash
$ sudo systemctl enable server
$ sudo systemctl start server
```

Gunicorn logs are in ```~/logs/```
