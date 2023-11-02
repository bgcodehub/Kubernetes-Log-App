import subprocess
import json

def run_kubectl_command(command):
    process = subprocess.run(["kubectl"] + command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if process.returncode != 0:
        print("Error executing kubectl command:", process.stderr)
        return None
    return process.stdout

def get_namespaces():
    output = run_kubectl_command(["get", "namespaces", "-o", "json"])
    if output is None:
        return []
    data = json.loads(output)
    return [item['metadata']['name'] for item in data['items']]

def get_pods(namespace):
    output = run_kubectl_command(["get", "pods", "-n", namespace, "-o", "json"])
    if output is None:
        return []
    data = json.loads(output)
    return [(item['metadata']['name'], item['status']['phase']) for item in data['items']]

def get_logs(pod_name, namespace):
    output = run_kubectl_command(["logs", pod_name, "-n", namespace])
    if output is None:
        return "Could not retrieve logs."
    return output