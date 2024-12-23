# Start the api servers:

# Start the SAM API server.
uvicorn samapi.main:app --workers 1 --port 3000

# Start ngrok to tunnel local API on public network.
ngrok http --url=<fill-w-perm-ngrok-addr>.ngrok-free.app 3000 --host-header="localhost:3000"