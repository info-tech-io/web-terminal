---
title: "User Guide"
description: "Comprehensive guide to using Web Terminal - features, configuration, and best practices"
date: 2024-09-23
draft: false
weight: 3
---

# User Guide

This comprehensive guide covers all aspects of using Web Terminal effectively, from basic operations to advanced configurations.

## Core Features

### Terminal Interface

Web Terminal provides a full-featured bash environment with:

- **Complete keyboard support** including arrow keys, function keys, and shortcuts
- **Copy/paste functionality** with Ctrl+C/Ctrl+V (or Cmd+C/Cmd+V on macOS)
- **Automatic resizing** that adapts to browser window changes
- **Full color support** for colored output and syntax highlighting
- **History navigation** with up/down arrows
- **Tab completion** for commands and file paths

### Container Management

The system automatically handles Docker containers:

- **Persistent sessions** - containers remain active between browser refreshes
- **Automatic cleanup** - inactive containers are terminated after timeout
- **Resource isolation** - each session runs in its own container
- **Fresh environments** - new containers start with clean state

## Configuration

### Application Settings

#### Port Configuration

```bash
# Change default port (8080)
export FLASK_PORT=9000
python app.py
```

#### Debug Mode

```bash
# Enable debug logging
export FLASK_DEBUG=true
python app.py
```

### Container Customization

#### Custom Docker Image

Create a custom Dockerfile for specialized environments:

```dockerfile
FROM ubuntu:22.04

# Install development tools
RUN apt-get update && apt-get install -y \
    build-essential \
    python3 \
    python3-pip \
    nodejs \
    npm \
    git \
    vim \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set up user environment
RUN useradd -m -s /bin/bash developer
USER developer
WORKDIR /home/developer

# Copy custom configurations
COPY .bashrc /home/developer/
COPY .vimrc /home/developer/

CMD ["/bin/bash"]
```

Build and use:

```bash
docker build -t my-custom-terminal .
# Modify app.py to use your image name
```

#### Environment Variables

Pass environment variables to containers:

```python
# In app.py, modify container creation
container = client.containers.run(
    DOCKER_IMAGE_NAME,
    environment={
        'PATH': '/usr/local/bin:/usr/bin:/bin',
        'TERM': 'xterm-256color',
        'USER': 'developer'
    },
    # ... other options
)
```

## Advanced Usage

### Multiple Sessions

Run multiple terminal instances:

```bash
# Start additional instances on different ports
FLASK_PORT=8081 python app.py &
FLASK_PORT=8082 python app.py &
FLASK_PORT=8083 python app.py &
```

Access them at:
- `http://localhost:8080`
- `http://localhost:8081`
- `http://localhost:8082`
- `http://localhost:8083`

### Persistence and Data

#### Volume Mounting

To persist data between sessions, modify the container creation in `app.py`:

```python
container = client.containers.run(
    DOCKER_IMAGE_NAME,
    volumes={
        '/path/on/host': {'bind': '/workspace', 'mode': 'rw'}
    },
    working_dir='/workspace',
    # ... other options
)
```

#### Shared Directories

Mount shared directories for file exchange:

```python
volumes = {
    '/home/user/shared': {'bind': '/shared', 'mode': 'rw'},
    '/tmp/terminal-data': {'bind': '/data', 'mode': 'rw'}
}
```

### Security Considerations

#### Network Isolation

By default, containers have network access. To restrict:

```python
container = client.containers.run(
    DOCKER_IMAGE_NAME,
    network_mode='none',  # No network access
    # or
    network_mode='bridge',  # Limited network
    # ... other options
)
```

#### Resource Limits

Set container resource limits:

```python
container = client.containers.run(
    DOCKER_IMAGE_NAME,
    mem_limit='512m',     # 512MB RAM limit
    cpu_period=100000,    # CPU period
    cpu_quota=50000,      # 50% CPU limit
    # ... other options
)
```

#### User Permissions

Run containers with non-root user:

```dockerfile
# In your custom Dockerfile
RUN useradd -m -u 1000 terminal-user
USER terminal-user
```

## Integration Examples

### Embedding in Web Applications

#### Basic Integration

```html
<!DOCTYPE html>
<html>
<head>
    <title>My App with Terminal</title>
    <style>
        #terminal-container {
            width: 100%;
            height: 400px;
            border: 1px solid #ccc;
        }
    </style>
</head>
<body>
    <h1>My Application</h1>
    <div id="terminal-container">
        <iframe src="http://localhost:8080"
                width="100%"
                height="100%"
                frameborder="0">
        </iframe>
    </div>
</body>
</html>
```

#### API Integration

Create a wrapper API for programmatic access:

```python
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

@app.route('/api/terminal/execute', methods=['POST'])
def execute_command():
    command = request.json.get('command')
    # Send command to terminal via WebSocket
    # Return result
    return jsonify({'output': result})
```

### Educational Platforms

For educational use cases:

```python
# Custom container with course materials
FROM ubuntu:22.04

# Install course-specific tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    jupyter \
    && rm -rf /var/lib/apt/lists/*

# Copy course materials
COPY course-materials/ /course/
WORKDIR /course

# Set up student environment
RUN useradd -m student
USER student

CMD ["/bin/bash"]
```

## Performance Optimization

### Connection Management

Optimize WebSocket connections:

```python
# In app.py, tune gevent settings
from gevent.pywsgi import WSGIServer

server = WSGIServer(
    ('0.0.0.0', port),
    app,
    handler_class=WebSocketHandler,
    spawn=1000  # Max concurrent connections
)
```

### Container Lifecycle

Implement container pooling for better performance:

```python
class ContainerPool:
    def __init__(self, size=5):
        self.pool = []
        self.size = size
        self._populate_pool()

    def get_container(self):
        if self.pool:
            return self.pool.pop()
        return self._create_container()

    def return_container(self, container):
        if len(self.pool) < self.size:
            self.pool.append(container)
        else:
            container.remove(force=True)
```

## Monitoring and Logging

### Application Monitoring

Monitor terminal usage:

```python
import logging
from datetime import datetime

# Enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('terminal.log'),
        logging.StreamHandler()
    ]
)

@sock.route('/terminal')
def terminal(ws):
    session_id = str(uuid.uuid4())
    logging.info(f"New session started: {session_id}")
    # ... terminal logic
    logging.info(f"Session ended: {session_id}")
```

### Container Monitoring

Track container resource usage:

```python
def get_container_stats(container):
    stats = container.stats(stream=False)
    return {
        'cpu_usage': stats['cpu_stats']['cpu_usage']['total_usage'],
        'memory_usage': stats['memory_stats']['usage'],
        'network_io': stats['networks']
    }
```

## Troubleshooting

### Common Issues

**Terminal not responding:**
- Check browser console for WebSocket errors
- Verify Docker container is running: `docker ps`
- Restart the application

**Slow performance:**
- Check container resource usage
- Monitor network latency
- Consider container pooling

**Connection drops:**
- Check network stability
- Verify WebSocket support in browser
- Review server logs for errors

### Debug Mode

Enable comprehensive debugging:

```python
# In app.py
import logging
logging.getLogger('werkzeug').setLevel(logging.DEBUG)
logging.getLogger('gevent').setLevel(logging.DEBUG)

app.config['DEBUG'] = True
```

## Best Practices

### Security
- Always run containers with limited privileges
- Implement session timeouts
- Use HTTPS in production
- Validate all user input

### Performance
- Implement connection pooling
- Set appropriate resource limits
- Monitor container lifecycle
- Use caching where appropriate

### Maintenance
- Regularly update base images
- Monitor disk usage for container storage
- Implement log rotation
- Clean up orphaned containers

---

*Need technical details? Check out our [Architecture Guide]({{< ref "architecture" >}}) or explore [Integration Examples]({{< ref "integration" >}}).*