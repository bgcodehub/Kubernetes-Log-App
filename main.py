import tkinter as tk
from tkinter import ttk
from kubernetes import client, config
import threading
import datetime
import time
import queue

class KubernetesLogApp:
    def __init__(self, root):
        self.root = root
        root.title("Kubernetes Log App")

        self.setup_kubernetes_client()

        self.namespaces = ["All"] + self.get_namespaces()

        self.namespace_var = tk.StringVar()
        self.namespace_var.set(self.namespaces[0] if self.namespaces else "")

        self.namespace_label = ttk.Label(root, text="Namespace", foreground="white", background="#2e2e2e")
        self.namespace_label.pack(pady=5, padx=10, side=tk.TOP, fill=tk.X)

        self.namespace_dropdown = ttk.Combobox(root, textvariable=self.namespace_var, values=self.namespaces)
        self.namespace_dropdown.pack(pady=5, padx=10, side=tk.TOP, fill=tk.X)
        self.namespace_dropdown.bind("<<ComboboxSelected>>", self.update_pods)

        self.pane = ttk.PanedWindow(root, orient=tk.VERTICAL)
        self.pane.pack(padx=10, pady=5, expand=True, fill=tk.BOTH)

        self.pods_listbox = tk.Listbox(self.pane, height=10, bg="#2e2e2e", fg="white")
        self.pods_listbox.pack(fill=tk.BOTH, expand=True)
        self.pods_listbox.bind("<<ListboxSelect>>", self.show_pod_logs)
        self.pane.add(self.pods_listbox)

        self.log_text = tk.Text(self.pane, wrap='word', height=10, bg="#2e2e2e", fg="white")
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.pane.add(self.log_text)

        # Configure tags for color coding
        self.log_text.tag_configure("error", background="#ff6666", foreground="black")
        self.log_text.tag_configure("warning", background="#ffd700", foreground="black")
        self.log_text.tag_configure("info", background="#90ee90", foreground="black")

        self.incident_text = tk.Text(self.pane, wrap='word', height=5, bg='#4e4e4e', fg='white')
        self.incident_text.pack(fill=tk.BOTH, expand=True)
        self.pane.add(self.incident_text)

        self.incident_report = {}
        
        self.event_queue = queue.Queue()
        self.process_k8s_events()

        self.update_pods()
        self.monitor_pods()
        self.monitor_logs()

    def setup_kubernetes_client(self):
        config.load_kube_config()
        self.v1 = client.CoreV1Api()

    def get_namespaces(self):
        namespaces = [namespace.metadata.name for namespace in self.v1.list_namespace().items]
        return namespaces

    def update_pods(self, event=None):
        selected_namespace = self.namespace_var.get()
        if selected_namespace:
            if selected_namespace == "All":
                pods = self.v1.list_pod_for_all_namespaces().items
            else:
                pods = self.v1.list_namespaced_pod(namespace=selected_namespace).items
            self.pods_listbox.delete(0, tk.END)
            for pod in pods:
                pod_info = f"{pod.metadata.namespace}/{pod.metadata.name} ({pod.status.phase})"
                self.pods_listbox.insert(tk.END, pod_info)

    def show_pod_logs(self, event=None):
        selected_pod_info = self.pods_listbox.get(self.pods_listbox.curselection())
        if selected_pod_info:
            namespace, pod_name = selected_pod_info.split("/")[0], selected_pod_info.split("/")[1].split(" ")[0]
            logs = self.v1.read_namespaced_pod_log(name=pod_name, namespace=namespace)
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, logs)
            self.color_code_logs(logs)

    def color_code_logs(self, logs):
        for index, line in enumerate(logs.split("\n"), start=1):
            if "error" in line.lower():
                self.log_text.tag_add("error", f"{index}.0", f"{index}.end")
            elif "warn" in line.lower():
                self.log_text.tag_add("warning", f"{index}.0", f"{index}.end")
            elif "info" in line.lower():
                self.log_text.tag_add("info", f"{index}.0", f"{index}.end")

    def monitor_pods(self):
        threading.Thread(target=self._monitor_pods_thread, daemon=True).start()

    def _monitor_pods_thread(self):
        while True:
            self.check_for_incidents()
            time.sleep(30)  # Adjust the sleep time as necessary

    def check_for_incidents(self):
        selected_namespace = self.namespace_var.get()
        if selected_namespace:
            if selected_namespace == "All":
                pods = self.v1.list_pod_for_all_namespaces().items
            else:
                pods = self.v1.list_namespaced_pod(namespace=selected_namespace).items
            for pod in pods:
                pod_name = f"{pod.metadata.namespace}/{pod.metadata.name}"
                pod_phase = pod.status.phase
                restart_count = sum(container_state.restart_count for container_state in pod.status.container_statuses)
                start_time = pod.status.start_time

                if pod_phase not in ("Running", "Succeeded") or restart_count > 0:
                    if pod_name not in self.incident_report:
                        self.incident_report[pod_name] = {
                            "start_time": start_time,
                            "phase": pod_phase,
                            "restart_count": restart_count
                        }
                        self.event_queue.put(('INCIDENT', pod_name))
                    else:
                        if pod_phase != self.incident_report[pod_name]["phase"] or restart_count != self.incident_report[pod_name]["restart_count"]:
                            self.incident_report[pod_name]["end_time"] = start_time
                            self.event_queue.put(('INCIDENT', pod_name))
                            self.incident_report[pod_name]["start_time"] = start_time
                            self.incident_report[pod_name]["phase"] = pod_phase
                            self.incident_report[pod_name]["restart_count"] = restart_count
                            self.event_queue.put(('INCIDENT', pod_name))

                elif pod_name in self.incident_report and "end_time" not in self.incident_report[pod_name]:
                    self.incident_report[pod_name]["end_time"] = start_time
                    self.event_queue.put(('INCIDENT', pod_name))

    def update_incident_report(self):
        self.incident_text.delete(1.0, tk.END)
        for pod_name, incident in self.incident_report.items():
            if "end_time" in incident:
                duration = incident["end_time"] - incident["start_time"]
                restart_count = incident["restart_count"]
                self.incident_text.insert(tk.END, f"{pod_name}: Incident resolved. Duration: {duration}. Restarts: {restart_count}\n")
            else:
                duration = datetime.datetime.now(datetime.timezone.utc) - incident["start_time"]
                self.incident_text.insert(tk.END, f"{pod_name}: Incident ongoing. Start Time: {incident['start_time']}. Current Phase: {incident['phase']}. Restart Count: {incident['restart_count']}. Duration: {duration}\n")

    def monitor_logs(self):
        threading.Thread(target=self._monitor_logs_thread, daemon=True).start()

    def _monitor_logs_thread(self):
        while True:
            self.update_pod_logs()
            time.sleep(5)  # Adjust the sleep time as necessary

    def update_pod_logs(self):
        selected_pod_info = self.pods_listbox.get(self.pods_listbox.curselection())
        if selected_pod_info:
            namespace, pod_name = selected_pod_info.split("/")[0], selected_pod_info.split("/")[1].split(" ")[0]
            logs = self.v1.read_namespaced_pod_log(name=pod_name, namespace=namespace)
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, logs)
            self.color_code_logs(logs)

    def process_k8s_events(self):
        try:
            while True:
                event_type, obj = self.event_queue.get_nowait()
                if event_type == 'POD':
                    self.update_pod_in_listbox(obj)
                elif event_type == 'LOG':
                    self.update_pod_logs(obj)
                elif event_type == 'INCIDENT':
                    self.update_incident_report()
        except queue.Empty:
            pass
        self.root.after(1000, self.process_k8s_events)

    def update_pod_in_listbox(self, pod_event):
        selected_namespace = self.namespace_var.get()
        if selected_namespace:
            if selected_namespace == "All":
                pods = self.v1.list_pod_for_all_namespaces().items
            else:
                pods = self.v1.list_namespaced_pod(namespace=selected_namespace).items
            self.pods_listbox.delete(0, tk.END)
            for pod in pods:
                pod_info = f"{pod.metadata.namespace}/{pod.metadata.name} ({pod.status.phase})"
                self.pods_listbox.insert(tk.END, pod_info)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    app = KubernetesLogApp(root)
    root.mainloop()