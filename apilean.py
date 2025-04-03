import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
import os

# Main app window
root = tk.Tk()
root.title("APILean")
root.geometry("800x600")

# URL input
url_label = tk.Label(root, text="URL:")
url_label.pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack()

# HTTP method dropdown
method_label = tk.Label(root, text="Method:")
method_label.pack(pady=5)
method_var = tk.StringVar(value="GET")
method_dropdown = ttk.Combobox(root, textvariable=method_var, values=["GET", "POST", "PUT", "DELETE"])
method_dropdown.pack()

# Headers editor
headers_frame = tk.LabelFrame(root, text="Headers", padx=10, pady=10)
headers_frame.pack(pady=10, fill="x")
headers = []

def add_header():
    header_row = tk.Frame(headers_frame)
    header_row.pack(fill="x", pady=2)
    key_entry = tk.Entry(header_row, width=20)
    key_entry.pack(side="left", padx=5)
    value_entry = tk.Entry(header_row, width=40)
    value_entry.pack(side="left", padx=5)
    remove_btn = tk.Button(header_row, text="X", command=lambda: remove_header(header_row))
    remove_btn.pack(side="left")
    headers.append((key_entry, value_entry, header_row))

def remove_header(row):
    for key_entry, value_entry, r in headers:
        if r == row:
            headers.remove((key_entry, value_entry, r))
            row.destroy()
            break

add_header_btn = tk.Button(headers_frame, text="Add Header", command=add_header)
add_header_btn.pack()
add_header()

# Body input (for POST/PUT)
body_frame = tk.LabelFrame(root, text="Body (JSON)", padx=10, pady=10)
body_frame.pack(pady=10, fill="x")
body_text = scrolledtext.ScrolledText(body_frame, width=70, height=5)
body_text.pack()

# Variables (simple key-value store)
variables = {}

# Response display
response_label = tk.Label(root, text="Response:")
response_label.pack(pady=5)
response_text = scrolledtext.ScrolledText(root, width=90, height=15)
response_text.pack()

# Replace variables in text
def replace_variables(text):
    for key, value in variables.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    return text

# Send request function
def send_request():
    url = replace_variables(url_entry.get())
    method = method_var.get()
    body = replace_variables(body_text.get(1.0, tk.END).strip())
    
    if not url:
        response_text.delete(1.0, tk.END)
        response_text.insert(tk.END, "Please enter a URL.")
        return
    
    headers_dict = {}
    for key_entry, value_entry, _ in headers:
        key = replace_variables(key_entry.get().strip())
        value = replace_variables(value_entry.get().strip())
        if key and value:
            headers_dict[key] = value
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers_dict, timeout=10)
        elif method == "POST":
            json_body = json.loads(body) if body else {}
            response = requests.post(url, headers=headers_dict, json=json_body, timeout=10)
        elif method == "PUT":
            json_body = json.loads(body) if body else {}
            response = requests.put(url, headers=headers_dict, json=json_body, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers_dict, timeout=10)
        
        # Display response
        response_text.delete(1.0, tk.END)
        response_text.insert(tk.END, f"Status: {response.status_code}\n\n")
        try:
            json_data = response.json()
            pretty_json = json.dumps(json_data, indent=2)
            response_text.insert(tk.END, pretty_json)
            # Store response data for chaining
            variables["last_response"] = json.dumps(json_data)
        except json.JSONDecodeError:
            response_text.insert(tk.END, response.text)
            
    except requests.RequestException as e:
        response_text.delete(1.0, tk.END)
        response_text.insert(tk.END, f"Error: {str(e)}")

# Export session
def export_session():
    session = {
        "url": url_entry.get(),
        "method": method_var.get(),
        "headers": [(k.get(), v.get()) for k, v, _ in headers],
        "body": body_text.get(1.0, tk.END).strip(),
        "variables": variables.copy()
    }
    with open("apilean_session.json", "w") as f:
        json.dump(session, f)
    messagebox.showinfo("Export", "Session saved to apilean_session.json")

# Import session
def import_session():
    try:
        with open("apilean_session.json", "r") as f:
            session = json.load(f)
        url_entry.delete(0, tk.END)
        url_entry.insert(0, session["url"])
        method_var.set(session["method"])
        for _ in headers[:]:  # Clear existing headers
            remove_header(headers[0][2])
        for key, value in session["headers"]:
            add_header()
            headers[-1][0].insert(0, key)
            headers[-1][1].insert(0, value)
        body_text.delete(1.0, tk.END)
        body_text.insert(tk.END, session["body"])
        variables.clear()
        variables.update(session["variables"])
        messagebox.showinfo("Import", "Session loaded from apilean_session.json")
    except FileNotFoundError:
        messagebox.showerror("Import", "No session file found.")
    except Exception as e:
        messagebox.showerror("Import", f"Error: {str(e)}")

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)
send_button = tk.Button(button_frame, text="Send", command=send_request)
send_button.pack(side="left", padx=5)
export_button = tk.Button(button_frame, text="Export", command=export_session)
export_button.pack(side="left", padx=5)
import_button = tk.Button(button_frame, text="Import", command=import_session)
import_button.pack(side="left", padx=5)

# Run the app
root.mainloop()