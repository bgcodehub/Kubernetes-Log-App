# Kubernetes-Log-App

Kubernetes-Log-App is a Python-based application designed to provide a user-friendly interface to interact with Kubernetes clusters. It helps users to track the status of pods, retrieve logs, and generate incident reports based on pod downtimes.

## Table of Contents

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Features](#features)
- [Usage](#usage)
- [Technical Details](#technical-details)

## Installation

Before you start, ensure that you have Python installed on your system. You can download and install Python from the official [Python website](https://www.python.org/).

### Dependencies

Install the required dependencies using pip:

```sh
pip install -r requirements.txt
```

### Setup

Clone the repository:

```sh
git clone https://github.com/yourusername/Kubernetes-Log-App.git
cd Kubernetes-Log-App
```

## Getting Started

To run the application, execute the following command:

```sh
python main.py
```


## Features
- **Namespace Selection**: Switch between Kubernetes namespaces easily.
- **Pod Status Tracking**: Monitor the status of all pods within the selected namespace.
- **Log Retrieval**: Access logs of specific pods for analysis.
- **Incident Reporting**: Automatically generate reports for incidents based on pod downtimes, including timestamps and reasons for downtime.
- **Color-Coded Logs**: View logs with color-coded error, warning, and info messages.
- **Real-Time Updates**: Get real-time updates on pod statuses and logs.
- **Incident Duration Tracking**: Track the duration of ongoing and resolved incidents.
- **User-Friendly Interface**: Intuitive GUI for seamless interaction.
- **Multi-Cluster Support**: Connect to various Kubernetes clusters, whether local or cloud-based.

## Usage
1. **Start the Application**: Run `python main.py`.
2. **Select a Namespace**: Use the dropdown to choose a Kubernetes namespace.
3. **Monitor Pod Status**: Observe the list of pods and their statuses in the selected namespace.
4. **Access Logs**: Click on a pod to retrieve and display its logs.
5. **View Incident Reports**: Incident reports are generated and updated in real-time, displaying ongoing and resolved incidents with their duration.

## Technical Details

- The application is built using `tkinter` for the GUI and the `kubernetes` Python client for interacting with the Kubernetes API.
- It uses threading to handle real-time updates and monitoring without freezing the GUI.
- Logs are color-coded to highlight errors, warnings, and informational messages.
- Incident reports provide insights on pod downtimes, including the start and end times of incidents, their duration, and the number of restarts.
- The application handles events from the Kubernetes cluster in real-time, ensuring that the displayed information is always up to date.
