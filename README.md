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
                                                 |   TensorFlow Consumers  |
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