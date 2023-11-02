import tkinter as tk
from tkinter import ttk
import kubernetes
from kubernetes import client, config
import threading
import time

class KubernetesLogApp:
    def __init__(self, root):
        self.root = root
        root.title("Kubernetes Log App")
        
        self.setup_kubernetes_client()
        
        self.namespaces = self.get_namespaces()
        
        self.namespace_var = tk.StringVar()
        self.namespace_var.set(self.namespaces[0] if self.namespaces else "")
        
        self.namespace_label = tk.Label(root, text="Namespace")
        self.namespace_label.pack()
        self.namespace_dropdown = ttk.Combobox(root, textvariable=self.namespace_var, values=self.namespaces)
        self.namespace_dropdown.pack()
        self.namespace_dropdown.bind("<<ComboboxSelected>>", self.update_pods)
        
        self.pods_listbox = tk.Listbox(root)
        self.pods_listbox.pack()
        self.pods_listbox.bind("<<ListboxSelect>>", self.show_pod_logs)
        
        self.log_text = tk.Text(root, wrap='word', height=10)
        self.log_text.pack(expand=1, fill=tk.BOTH)
        
        self.incident_text = tk.Text(root, wrap='word', height=5, bg='light yellow')
        self.incident_text.pack(expand=1, fill=tk.BOTH)
        
        self.update_pods()
        self.monitor_pods()
    
    def setup_kubernetes_client(self):
        config.load_kube_config()
        self.v1 = client.CoreV1Api()
    
    def get_namespaces(self):
        namespaces = [namespace.metadata.name for namespace in self.v1.list_namespace().items]
        return namespaces
    
    def update_pods(self, event=None):
        selected_namespace = self.namespace_var.get()
        if selected_namespace:
            pods = self.v1.list_namespaced_pod(namespace=selected_namespace).items
            self.pods_listbox.delete(0, tk.END)
            for pod in pods:
                pod_info = f"{pod.metadata.name} ({pod.status.phase})"
                self.pods_listbox.insert(tk.END, pod_info)
    
    def show_pod_logs(self, event=None):
        selected_namespace = self.namespace_var.get()
        selected_pod_index = self.pods_listbox.curselection()
        if selected_namespace and selected_pod_index:
            selected_pod = self.pods_listbox.get(selected_pod_index)
            pod_name = selected_pod.split(" ")[0]
            logs = self.v1.read_namespaced_pod_log(name=pod_name, namespace=selected_namespace)
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, logs)
    
    def monitor_pods(self):
        self.incident_report = {}
        threading.Thread(target=self._monitor_pods_thread).start()
    
    def _monitor_pods_thread(self):
        while True:
            self.check_for_incidents()
            time.sleep(30)  # Adjust the sleep time as necessary
    
    def check_for_incidents(self):
        selected_namespace = self.namespace_var.get()
        if selected_namespace:
            pods = self.v1.list_namespaced_pod(namespace=selected_namespace).items
            for pod in pods:
                if pod.status.phase not in ("Running", "Succeeded"):
                    incident_key = f"{selected_namespace}/{pod.metadata.name}"
                    if incident_key not in self.incident_report:
                        self.incident_report[incident_key] = {
                            "start_time": pod.status.start_time,
                            "reason": pod.status.reason,
                            "message": pod.status.message
                        }
                    else:
                        self.incident_report[incident_key]["end_time"] = pod.status.start_time
                else:
                    incident_key = f"{selected_namespace}/{pod.metadata.name}"
                    if incident_key in self.incident_report and "end_time" not in self.incident_report[incident_key]:
                        self.incident_report[incident_key]["end_time"] = pod.status.start_time
                        self.update_incident_report()
    
    def update_incident_report(self):
        self.incident_text.delete(1.0, tk.END)
        for incident, data in self.incident_report.items():
            start_time = data.get("start_time", "N/A")
            end_time = data.get("end_time", "Ongoing")
            reason = data.get("reason", "Unknown")
            message = data.get("message", "No additional information")
            report = f"Incident: {incident}\nStart Time: {start_time}\nEnd Time: {end_time}\nReason: {reason}\nMessage: {message}\n\n"
            self.incident_text.insert(tk.END, report)

# Create the main window
root = tk.Tk()
app = KubernetesLogApp(root)
root.mainloop()