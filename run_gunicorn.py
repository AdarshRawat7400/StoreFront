# run_gunicorn.py
import socket

def get_host_ip():
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        return host_ip
    except Exception as e:
        print(f"Error getting host IP: {e}")
        return None

if __name__ == "__main__":
    host_ip = get_host_ip()
    if host_ip:
        print(f"Running Gunicorn on {host_ip}:8000")
        cmd = f"gunicorn -b {host_ip}:8000 storefront.wsgi:application"
        import os
        os.system(cmd)
    else:
        print("Failed to get host IP.")
