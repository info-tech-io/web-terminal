---
title: "Getting Started"
description: "Complete setup guide for Web Terminal - from installation to first terminal session"
date: 2024-09-23
draft: false
weight: 2
---

# Getting Started with Web Terminal

This guide will walk you through setting up and running your first Web Terminal session in just a few minutes.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed with pip
- **Docker** installed and running
- **User permissions** to run Docker containers
- **Git** for cloning the repository (optional)

### Verify Prerequisites

```bash
# Check Python version
python3 --version

# Check Docker installation
docker --version
docker ps

# Verify Docker permissions
docker run hello-world
```

## Installation

### Option 1: Clone Repository

```bash
git clone https://github.com/info-tech-io/web-terminal.git
cd web-terminal
```

### Option 2: Download Release

Download the latest release from GitHub and extract it to your desired directory.

## Setup

### 1. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

The requirements.txt includes:
- `Flask` - Web framework
- `gevent` - Async server
- `flask-sock` - WebSocket support
- `docker` - Docker API client

### 3. Run the Application

```bash
python app.py
```

**On first run:**
- The application automatically builds the `gemini-terminal-box` Docker image
- This process takes 2-3 minutes and only happens once
- Subsequent runs use the existing image and start immediately

**Expected output:**
```
INFO - Docker image 'gemini-terminal-box' not found. Building...
INFO - Successfully built image 'gemini-terminal-box'
INFO - Web Terminal started successfully
 * Running on http://127.0.0.1:8080
```

### 4. Access Your Terminal

1. Open your browser and navigate to: `http://127.0.0.1:8080`
2. You'll see a full-featured terminal interface
3. Start typing commands - you're now in a containerized bash environment!

## First Commands

Try these commands to verify everything is working:

```bash
# Check the environment
whoami
pwd
ls -la

# System information
uname -a
cat /etc/os-release

# Install and test a package
apt update
apt install curl -y
curl -s https://httpbin.org/ip
```

## Configuration Options

### Environment Variables

You can customize the behavior using environment variables:

```bash
# Change default port
export FLASK_PORT=9000
python app.py

# Enable debug mode
export FLASK_DEBUG=true
python app.py
```

### Docker Image Customization

To modify the container environment, edit the `Dockerfile`:

```dockerfile
FROM ubuntu:22.04

# Add your custom packages here
RUN apt-get update && apt-get install -y \
    bash \
    curl \
    vim \
    git \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Add custom configurations
COPY custom-configs/ /etc/

CMD ["/bin/bash"]
```

Then rebuild the image:

```bash
docker rmi gemini-terminal-box
python app.py  # Will rebuild automatically
```

## Troubleshooting

### Common Issues

**"Permission denied" when running Docker:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in, or run:
newgrp docker
```

**Port 8080 already in use:**
```bash
# Check what's using the port
lsof -i :8080
# Kill the process or use a different port
export FLASK_PORT=9000
```

**Docker image build fails:**
```bash
# Check Docker daemon is running
sudo systemctl status docker
# Try building manually
docker build -t gemini-terminal-box .
```

**WebSocket connection fails:**
```bash
# Check if gevent is installed
pip show gevent
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Logs and Debugging

Enable detailed logging:

```python
# In app.py, change logging level
logging.basicConfig(level=logging.DEBUG)
```

Check Docker container logs:

```bash
docker logs gemini-terminal-instance
```

## Next Steps

Once you have Web Terminal running:

1. **Explore the [User Guide]({{< ref "user-guide" >}})** for advanced usage patterns
2. **Check out [Configuration]({{< ref "configuration" >}})** for customization options
3. **Read [Architecture]({{< ref "architecture" >}})** to understand the technical implementation
4. **See [Integration Examples]({{< ref "integration" >}})** for embedding in your applications

## Support

- **Documentation**: Full documentation available at [terminal.info-tech.io](https://terminal.info-tech.io)
- **Issues**: Report bugs on [GitHub Issues](https://github.com/info-tech-io/web-terminal/issues)
- **Community**: Join discussions in our [GitHub Discussions](https://github.com/info-tech-io/web-terminal/discussions)

---

*Ready for advanced configuration? Check out our [User Guide]({{< ref "user-guide" >}}) next.*