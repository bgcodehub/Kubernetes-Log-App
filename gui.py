import tkinter as tk
import k8s_interaction

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.namespace_label = tk.Label(self, text="Namespaces")
        self.namespace_label.pack(side="top")

        self.namespace_listbox = tk.Listbox(self)
        self.namespace_listbox.pack(side="left", fill="both", expand=True)
        self.namespace_listbox.bind('<<ListboxSelect>>', self.on_namespace_select)

        self.namespace_scrollbar = tk.Scrollbar(self, orient="vertical", command=self.namespace_listbox.yview)
        self.namespace_scrollbar.pack(side="left", fill="y")
        self.namespace_listbox.configure(yscrollcommand=self.namespace_scrollbar.set)

        self.pod_label = tk.Label(self, text="Pods")
        self.pod_label.pack(side="top")

        self.pod_listbox = tk.Listbox(self)
        self.pod_listbox.pack(side="left", fill="both", expand=True)
        self.pod_listbox.bind('<<ListboxSelect>>', self.on_pod_select)

        self.pod_scrollbar = tk.Scrollbar(self, orient="vertical", command=self.pod_listbox.yview)
        self.pod_scrollbar.pack(side="left", fill="y")
        self.pod_listbox.configure(yscrollcommand=self.pod_scrollbar.set)

        self.log_text = tk.Text(self, wrap='word', height=10)
        self.log_text.pack(side="bottom", fill="both", expand=True)

        self.log_scrollbar = tk.Scrollbar(self, orient="vertical", command=self.log_text.yview)
        self.log_scrollbar.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=self.log_scrollbar.set)

        self.update_namespaces()

    def update_namespaces(self):
        self.namespace_listbox.delete(0, tk.END)
        namespaces = k8s_interaction.get_namespaces()
        for namespace in namespaces:
            self.namespace_listbox.insert(tk.END, namespace)

    def on_namespace_select(self, event):
        widget = event.widget
        selection = widget.curselection()
        if selection:
            index = selection[0]
            namespace = widget.get(index)
            self.update_pods(namespace)

    def update_pods(self, namespace):
        self.pod_listbox.delete(0, tk.END)
        pods = k8s_interaction.get_pods(namespace)
        for pod, status in pods:
            self.pod_listbox.insert(tk.END, f"{pod} ({status})")

    def on_pod_select(self, event):
        namespace_index = self.namespace_listbox.curselection()
        pod_index = self.pod_listbox.curselection()
        if namespace_index and pod_index:
            namespace = self.namespace_listbox.get(namespace_index)
            pod, status = self.pod_listbox.get(pod_index).split(" (")
            pod_status = status[:-1]  # Remove trailing )
            if pod_status == "Running":
                logs = k8s_interaction.get_logs(pod, namespace)
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, logs)
            else:
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, "Pod is not running. Logs are not available.")