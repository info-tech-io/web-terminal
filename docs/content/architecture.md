---
title: "Architecture"
description: "Technical architecture and implementation details of Web Terminal system"
date: 2024-09-23
draft: false
weight: 4
---

# Architecture

This document provides detailed technical information about Web Terminal's architecture, design decisions, and implementation details.

## System Overview

Web Terminal implements a real-time, browser-based terminal interface using a multi-layer architecture that seamlessly connects web clients to Docker containers.

### High-Level Architecture

```
┌─────────────────┐    ┌────────────────────┐    ┌─────────────────┐    ┌──────────────────┐
│                 │    │                    │    │                 │    │                  │
│  Browser Client │◄──►│  Flask Backend     │◄──►│  Docker Daemon  │◄──►│  Docker Container│
│  (xterm.js)     │    │  (Gevent + Sockets)│    │  (dockerd)      │    │  (bash + tools)  │
│                 │    │                    │    │                 │    │                  │
└─────────────────┘    └────────────────────┘    └─────────────────┘    └──────────────────┘
       │                         │                         │                        │
       │ WebSocket               │ Docker Python API       │ Docker API             │ Process I/O
       │ (ws://)                 │                         │ (HTTP/Unix Socket)     │ (stdin/stdout)
       │                         │                         │                        │
       └─────────────────────────┼─────────────────────────┼────────────────────────┘
                                 │                         │
                           ┌─────▼─────┐           ┌─────▼─────┐
                           │  Session  │           │ Container │
                           │ Management│           │ Lifecycle │
                           └───────────┘           └───────────┘
```

## Component Architecture

### Frontend Layer (Browser)

**Technology Stack:**
- **xterm.js** - Professional terminal emulator
- **xterm-addon-fit** - Responsive terminal sizing
- **WebSocket API** - Real-time bidirectional communication

**Key Responsibilities:**
- Terminal rendering and display
- Keyboard input capture and processing
- WebSocket connection management
- Screen size adaptation
- User interaction handling

**Data Flow:**
```javascript
// Input: User keystrokes → xterm.js → WebSocket → Backend
terminal.onData(data => {
    ws.send(JSON.stringify({type: 'input', data: data}));
});

// Output: Backend → WebSocket → xterm.js → Terminal display
ws.onmessage = event => {
    const message = JSON.parse(event.data);
    terminal.write(message.data);
};
```

### Backend Layer (Python Flask)

**Technology Stack:**
- **Flask** - Lightweight web framework
- **Gevent** - Asynchronous WSGI server
- **flask-sock** - WebSocket integration
- **docker-py** - Docker API client

**Core Components:**

#### 1. WebSocket Handler
```python
@sock.route('/terminal')
def terminal(ws):
    """Main WebSocket endpoint for terminal sessions"""
    container = get_or_create_container()

    # Bidirectional data forwarding
    greenlets = [
        gevent.spawn(read_from_container, container, ws),
        gevent.spawn(write_to_container, container, ws)
    ]

    gevent.joinall(greenlets)
```

#### 2. Container Manager
```python
class ContainerManager:
    """Manages Docker container lifecycle"""

    def get_or_create_container(self):
        """Returns running container or creates new one"""

    def cleanup_inactive_containers(self):
        """Removes containers after timeout"""

    def handle_container_exit(self, container):
        """Cleanup when container stops"""
```

#### 3. Session Manager
```python
class SessionManager:
    """Tracks active WebSocket sessions"""

    def register_session(self, ws, container):
        """Associates WebSocket with container"""

    def cleanup_session(self, ws):
        """Cleanup on disconnect"""
```

### Container Layer (Docker)

**Base Image Configuration:**
```dockerfile
FROM ubuntu:22.04

# Essential packages for terminal functionality
RUN apt-get update && apt-get install -y \
    bash \
    coreutils \
    util-linux \
    procps \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Configure terminal environment
ENV TERM=xterm-256color
ENV SHELL=/bin/bash

# Set working directory
WORKDIR /workspace

# Default command
CMD ["/bin/bash"]
```

**Container Features:**
- Isolated execution environment
- Standard Linux command-line tools
- Configurable resource limits
- Automatic cleanup on session end

## Data Flow Architecture

### Input Processing Chain

1. **User Input Capture**
   ```
   Keyboard Event → xterm.js onData → WebSocket send()
   ```

2. **Backend Processing**
   ```
   WebSocket receive → JSON parse → Container stdin write
   ```

3. **Container Execution**
   ```
   stdin → bash process → command execution
   ```

### Output Processing Chain

1. **Container Output**
   ```
   bash stdout/stderr → Docker API streams
   ```

2. **Backend Forwarding**
   ```
   Stream read → WebSocket send → JSON format
   ```

3. **Frontend Rendering**
   ```
   WebSocket receive → xterm.js write() → Terminal display
   ```

## Concurrency Model

### Gevent Architecture

Web Terminal uses Gevent's cooperative multitasking for high-performance concurrent connections:

```python
# Greenlet-based concurrency
def handle_session(ws):
    container = create_container()

    # Concurrent I/O operations
    input_greenlet = gevent.spawn(handle_input, ws, container)
    output_greenlet = gevent.spawn(handle_output, ws, container)

    # Wait for either to complete
    gevent.joinall([input_greenlet, output_greenlet])
```

**Benefits:**
- Single-threaded simplicity
- High concurrency (1000+ connections)
- Low memory overhead
- Automatic I/O multiplexing

### Session Management

```python
class SessionTracker:
    def __init__(self):
        self.active_sessions = {}
        self.container_map = {}

    def add_session(self, session_id, ws, container):
        self.active_sessions[session_id] = {
            'websocket': ws,
            'container': container,
            'created_at': time.time(),
            'last_activity': time.time()
        }
```

## Security Architecture

### Container Isolation

**Default Security:**
- No privileged mode
- Limited capabilities
- Network isolation options
- Filesystem isolation
- Process isolation

**Configuration Example:**
```python
container = client.containers.run(
    image_name,
    detach=True,
    tty=True,
    stdin_open=True,
    privileged=False,          # No elevated privileges
    cap_drop=['ALL'],          # Drop all capabilities
    cap_add=['SYS_CHROOT'],    # Add only required caps
    security_opt=['no-new-privileges'],
    user='1000:1000',          # Non-root user
    mem_limit='512m',          # Memory limit
    cpu_shares=512             # CPU limit
)
```

### Network Security

**WebSocket Security:**
- Origin validation
- Connection rate limiting
- Session timeout enforcement
- Input sanitization

```python
@sock.route('/terminal')
def terminal(ws):
    # Validate origin
    if not validate_origin(ws.environ.get('HTTP_ORIGIN')):
        ws.close(code=4003, message='Invalid origin')
        return

    # Rate limiting
    if not rate_limiter.allow(get_client_ip(ws)):
        ws.close(code=4004, message='Rate limit exceeded')
        return
```

## Performance Considerations

### Memory Management

**Container Resource Limits:**
```python
# Prevent memory exhaustion
container_config = {
    'mem_limit': '256m',           # RAM limit
    'memswap_limit': '512m',       # RAM + swap limit
    'oom_kill_disable': False,     # Allow OOM killer
    'mem_swappiness': 10           # Reduce swapping
}
```

**Backend Optimization:**
```python
# Efficient message handling
def handle_messages(ws, container):
    buffer = []

    while True:
        # Batch small messages
        data = container.logs(
            stdout=True,
            stderr=True,
            stream=True,
            since=last_timestamp
        )

        # Send in chunks to reduce WebSocket overhead
        for chunk in data:
            if len(chunk) > CHUNK_SIZE:
                ws.send(chunk)
            else:
                buffer.append(chunk)
                if len(buffer) >= BUFFER_SIZE:
                    ws.send(b''.join(buffer))
                    buffer.clear()
```

### Connection Scaling

**Gevent Configuration:**
```python
from gevent.pywsgi import WSGIServer

# Optimize for high concurrency
server = WSGIServer(
    ('0.0.0.0', port),
    app,
    spawn=gevent.pool.Pool(10000),  # Connection pool
    handler_class=WebSocketHandler,
    log=None,                       # Disable access logs
    error_log=sys.stderr
)
```

## Error Handling

### Graceful Degradation

```python
def handle_container_failure(container, ws):
    try:
        # Attempt container restart
        container.restart(timeout=10)
        ws.send(json.dumps({
            'type': 'system',
            'message': 'Container restarted due to error'
        }))
    except docker.errors.APIError:
        # Create new container if restart fails
        new_container = create_container()
        return new_container
```

### Connection Recovery

```javascript
// Frontend reconnection logic
function setupWebSocket() {
    const ws = new WebSocket('ws://localhost:8080/terminal');

    ws.onclose = function(event) {
        if (event.code !== 1000) { // Not normal closure
            // Attempt reconnection with exponential backoff
            setTimeout(() => {
                setupWebSocket();
            }, Math.min(1000 * Math.pow(2, retryCount), 30000));
        }
    };
}
```

## Monitoring and Observability

### Metrics Collection

```python
import time
from collections import defaultdict

class MetricsCollector:
    def __init__(self):
        self.metrics = defaultdict(list)

    def record_session_duration(self, duration):
        self.metrics['session_duration'].append(duration)

    def record_container_creation_time(self, duration):
        self.metrics['container_creation'].append(duration)

    def get_statistics(self):
        return {
            'active_sessions': len(active_sessions),
            'average_session_duration': statistics.mean(
                self.metrics['session_duration']
            ),
            'containers_created': len(self.metrics['container_creation'])
        }
```

### Health Checks

```python
@app.route('/health')
def health_check():
    try:
        # Check Docker daemon
        client = docker.from_env()
        client.ping()

        # Check container limits
        containers = client.containers.list()
        if len(containers) > MAX_CONTAINERS:
            return {'status': 'degraded', 'reason': 'High container count'}

        return {'status': 'healthy'}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500
```

## Deployment Architecture

### Production Configuration

```python
# Production settings
import os

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MAX_CONNECTIONS = int(os.environ.get('MAX_CONNECTIONS', 1000))
    CONTAINER_TIMEOUT = int(os.environ.get('CONTAINER_TIMEOUT', 3600))
    REDIS_URL = os.environ.get('REDIS_URL')  # For session storage
    LOG_LEVEL = 'INFO'
    SSL_CERT_PATH = os.environ.get('SSL_CERT_PATH')
    SSL_KEY_PATH = os.environ.get('SSL_KEY_PATH')
```

### Scaling Considerations

**Horizontal Scaling:**
- Load balancer with sticky sessions
- Shared Redis for session state
- Container orchestration (Docker Swarm/Kubernetes)

**Resource Planning:**
- ~10MB RAM per active session
- ~50MB per Docker container
- 1 CPU core handles ~100-200 concurrent sessions

---

*For implementation details, see our [Developer Documentation]({{< ref "developer" >}}) or check out [Contributing Guidelines]({{< ref "contributing" >}}).*