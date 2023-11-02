# Kubernetes-Log-App

Kubernetes-Log-App is a Python-based application designed to provide a user-friendly interface to interact with Kubernetes clusters. It helps users to track the status of pods, retrieve logs, and generate incident reports based on pod downtimes.

## Table of Contents

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Features](#features)
- [Usage](#usage)

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
- **Namespace Selection**: Easily switch between different Kubernetes namespaces.
- **Pod Status Tracking**: View the status of all pods within the selected namespace.
- **Log Retrieval**: Access logs of specific pods for troubleshooting and analysis.
- **Incident Reporting**: Generate incident reports based on pod downtimes, including timestamps and reasons for downtime.
- **User-Friendly Interface**: A GUI that provides a straightforward and intuitive user experience.
- **Support for Multiple Clusters**: Connect to and interact with Kubernetes clusters located locally or on cloud providers like Azure and AWS.

## Usage
1. **Start the Application**: Run `python main.py` to start the application.
2. **Select a Namespace**: Use the dropdown menu to select the desired Kubernetes namespace.
3. **View Pod Status**: View the list of pods and their status in the selected namespace.
4. **Retrieve Logs**: Click on a specific pod to retrieve and display its logs.
5. **Generate Incident Reports**: Incident reports are generated automatically based on pod downtimes and are accessible through the application.