import kubernetes
from kubernetes import client

def initialize_k8s_api():
    kubernetes.config.load_kube_config()
    v1 = client.CoreV1Api()
    return v1

def get_namespaces(api_instance):
    namespaces = []
    try:
        for ns in api_instance.list_namespace().items:
            namespaces.append(ns.metadata.name)
    except Exception as e:
        print("Error getting namespaces:", str(e))
    return namespaces

def get_pods(api_instance, namespace):
    pods = []
    try:
        for pod in api_instance.list_namespaced_pod(namespace).items:
            pods.append((pod.metadata.name, pod.status.phase))
    except Exception as e:
        print(f"Error getting pods in namespace {namespace}:", str(e))
    return pods

def get_pod_logs(api_instance, namespace, pod_name):
    logs = ""
    try:
        logs = api_instance.read_namespaced_pod_log(name=pod_name, namespace=namespace)
    except Exception as e:
        print(f"Error getting logs for pod {pod_name} in namespace {namespace}:", str(e))
    return logs