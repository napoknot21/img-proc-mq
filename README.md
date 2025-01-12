# Image compressor

Final [CALC](https://moodle.imt-atlantique.fr/course/view.php?id=1091) project.

This project recreates a image processor app with a client where it's possible to updloads images/photos and server side with a distributed logic



## Project structure

This the current project structure

```
/
├── src/                               # Main source code
│   ├── server/                        # Server-side logic
│   │   ├── app.py                     # Entry point for Flask
│   │   ├── config.py                  # Configuration settings
│   │   ├── uploads/                   # Folder for storing uploaded images
│   │   ├── consumers/                 # RabbitMQ consumers
│   │   │   ├── compression.py         # Consumer for image compression
│   │   │   ├── detection.py           # Consumer for object detection
│   │   │   └── report.py              # Consumer for report generation
│   │   ├── pipeline/                  # Business logic
│   │   │   ├── compression_task.py    # Logic for image compression
│   │   │   ├── detection_task.py      # Logic for object detection
│   │   │   └── report_task.py         # Logic for report generation
│   │   └── utils/                     # Utility modules
│   │       ├── rabbitmq.py            # RabbitMQ connection and management
│   │       └── file_handler.py        # File management utilities
│   │
│   ├── client/                        # Client-side application
│   │   ├── index.html                 # Main HTML page
│   │   ├── styles.css                 # CSS file for styling
│   │   ├── app.js                     # JavaScript logic for the client
│   │   └── assets/                    # Static assets like images or icons
│   │
│   └── tests/                         # Unit and integration tests
│       ├── test_server.py             # Tests for server logic
│       ├── test_consumers.py          # Tests for RabbitMQ consumers
│       ├── test_pipeline.py           # Tests for business logic
│       └── fixtures/                  # Test data and configurations
│
├── docker/                            # Dockerfiles and Docker configuration
│   ├── Dockerfile.server              # Dockerfile for the server
│   ├── Dockerfile.consumer            # Dockerfile for RabbitMQ consumers
│   ├── Dockerfile.client              # Dockerfile for the client (optional)
│   └── docker-compose.yml             # Orchestration using Docker Compose
│
├── Makefile                           # Commands to automate tasks
├── README.md                          # Project documentation
└── .env                               # Environment variables
```


## Architecture

```
+------------------+      +---------------------+      +---------------------+
|   Client (UI)    | ---> |    Flask Server     | ---> |    RabbitMQ Queue    |
|  (Upload Image)  |      |   (Task Manager)    |      |  (Task Distribution) |
+------------------+      +---------------------+      +---------------------+
                                                            |
                                                            v
                                                 +-------------------------+
                                                 |        Consumers        |
                                                 |  (Distributed Workers)  |
                                                 +-------------------------+
                                                            |
                                                            v
                                                 +-------------------------+
                                                 |      Results Queue      |
                                                 |   (Processed Outputs)   |
                                                 +-------------------------+
                                                            |
                                                            v
                                              +-----------------------------+
                                              |     Flask Result Store      |
                                              |  (Aggregation & Polling)    |
                                              +-----------------------------+
                                                            |
                                                            v
                                                 +---------------------+
                                                 |       Client         |
                                                 |  (Poll for Results)  |
                                                 +---------------------+

```

## Run the project


There are two ways to run the project, you can run it `local` or with `docker`.


### In localhost (no containers)

FIrst, you have to change some default parameters in the code

You have to change the `RABBITMQ_SERVER` value in the `src/server/config/config.py` file
```
RABBITMQ_SERVER="localhost"
```
> the project assumes that `rabbitmq` uses the default port and settings


Then, change the settings for the `consumer` in the `src/consumer/settings/config.py` file
```
RABBITMQ_SERVER="localhost
...
ROOT_STORAGE_FOLDER="../server/"
```

Check if your `rabbitmq` is active on your device
```
systemctl status rabbitmq
```

You have to get an ouput like this
```
● rabbitmq.service - RabbitMQ broker
     Loaded: loaded (/usr/lib/systemd/system/rabbitmq.service; enabled; preset: disabled)
     Active: active (running) since Sun 2025-01-12 16:36:51 CET; 860ms ago
 Invocation: f948bf6ec2a64587871d7524779dc43b
   Main PID: 28549 (beam.smp)
      Tasks: 37 (limit: 9050)
     Memory: 133.9M (peak: 136.4M)
        CPU: 3.226s
     CGroup: /system.slice/rabbitmq.service
             ├─28549 /usr/lib/erlang/erts-15.1.3/bin/beam.smp -W w -MBas ageffcbf -MHas ageffcbf -MBlmbcs 512 -MHlmbcs 512 -MMmcs 30 -pc unicode -P 1048576 -t 5000000 -stbt db -zdbbl 128000 -sbwt none -sbwtdcpu>
             ├─28560 erl_child_setup 1024
             ├─28600 /usr/lib/erlang/erts-15.1.3/bin/epmd -daemon
             ├─28635 /usr/lib/erlang/erts-15.1.3/bin/inet_gethost 4
             ├─28636 /usr/lib/erlang/erts-15.1.3/bin/inet_gethost 4
             └─28639 /bin/sh -s rabbit_disk_monitor

Jan 12 16:36:50 qwerty rabbitmq[28549]:   Release series support status: supported
Jan 12 16:36:50 qwerty rabbitmq[28549]:   Doc guides:  https://rabbitmq.com/documentation.html
Jan 12 16:36:50 qwerty rabbitmq[28549]:   Support:     https://rabbitmq.com/contact.html
Jan 12 16:36:50 qwerty rabbitmq[28549]:   Tutorials:   https://rabbitmq.com/getstarted.html
Jan 12 16:36:50 qwerty rabbitmq[28549]:   Monitoring:  https://rabbitmq.com/monitoring.html
Jan 12 16:36:50 qwerty rabbitmq[28549]:   Logs: /var/log/rabbitmq/rabbit@qwerty.log
...
```
> It's import to notice the `Active: active (running)` status !


Now, assuming that your `rabbitmq` is fully set up, let's open 2 different terminals. one for the server and the other for the consumer

For the fist terminal; you have to run the `src/server/server.py` file so
```
cd src/server && python3 server.py
```
> Don't forget to check the `src/server/requirements.txt` to install all dependecies

You will get an similar output in a foreground mode
```
 * Serving Flask app 'server'
 * Debug mode: off
[+] Successfully connected to localhost
[*] Waiting for messages in result_queue...
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://10.20.45.5:5000
Press CTRL+C to quit
```

Next, in the second terminal, we need to run the consumer by the `src/consumer/main.py`
```
cd src/consumer && python3 main.py
```
> Don't forget to check the `src/consumer/requirements.txt` to install all dependecies

You will get an similar output in a foreground mode
```
[*] All required environment variables are set.

[+] Successfully connected to localhost

[*] Waiting for messages in image_tasks...
```

The core is ready to use !


### Docker config (containers)

The project is set up to use Docker configuration. So you don't have to modify anithing !


All docker files are availables in the [`docker`](./docker/) directory so

For running the project, let's open three terminals for the `rabbitmq`, `flask_server` and `compressor_consumer_1` containers !


First of all , change the directory to the `docker` directory for all three termminals
```
cd docker
```


Once done, the first terminal will be used as the `rabbitmq` container
```
docker-compose up rabbitmq
```
> The project uses the default rabbitmq settings


The second terminal will be used as the `flask_server` container
```
docker-compose build flask_server
```

Run the container
```
docker-compose up flask_server
```


Next, the third terminal will be used as the `compressor_consumer_1` container
```
docker-compose build compressor_consumer_1
```

Run the container
```
docker-comose up compressor_consumer_1
```

### User Interface 

Finally, open the `src/client/index.html` file with your preferred browser !
```
brave src/client/index.html
```
> Here i put brave, but change it with your preferred browser

The browser should show the following page

![image](./extras/site.png)