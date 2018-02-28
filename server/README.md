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

```

Launch project locally for development:
```bash
# start virtual environment if not yet done
$ source venv/bin/activate

# start server
$ python server.py
```



# Production Server
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

allow 'Nginx Full'
The following has already been done and is only a description of the setup
on the instance.

[Gunicorn](http://gunicorn.org/) is used as http server.

[Nginx](https://www.nginx.com/) acts as a reverse proxy to take in traffic on port 80.
 
There is a systemd unit file in ```/etc/systemd/system/server.service``` that
configures the instance to run gunicorn on startup (0.0.0.0:5000).

Nginx setup is in ```/etc/nginx/sites-available```, symlinked to ```/etc/nginx/sites-enabled```

## Debugging Production
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

Gunicorn logs are in:
