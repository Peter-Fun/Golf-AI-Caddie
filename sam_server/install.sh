## Installation script for the api server. (tested on Ubuntu)

# Install ngrok for tunnelling
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
    sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
    sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && \
    sudo apt install ngrok

# Add the ngrok auth token (Get your own auth token from ngrok)
ngrok config add-authtoken <ngrok authtoken>

# Install SAMAPI
conda install -c conda-forge -y cudatoolkit=11.8
cd samapi; python -m pip install -e .