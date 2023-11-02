import kubernetes
from kubernetes import client, watch
import threading
import queue

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

def watch_pods(api_instance, namespace, event_queue):
    w = watch.Watch()
    for event in w.stream(api_instance.list_namespaced_pod, namespace):
        event_queue.put(("POD", event))

def watch_pod_logs(api_instance, namespace, pod_name, event_queue):
    w = watch.Watch()
    for event in w.stream(api_instance.read_namespaced_pod_log, name=pod_name, namespace=namespace, _preload_content=False):
        event_queue.put(("LOG", event))

def start_watch_threads(api_instance, namespace, event_queue):
    threading.Thread(target=watch_pods, args=(api_instance, namespace, event_queue)).start()
    pods = get_pods(api_instance, namespace)
    for pod_name, _ in pods:
        threading.Thread(target=watch_pod_logs, args=(api_instance, namespace, pod_name, event_queue)).start()