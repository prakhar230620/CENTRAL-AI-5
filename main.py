import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import json
import threading
import speech_recognition as sr
import os
from dotenv import load_dotenv

load_dotenv()


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Integration Platform")
        self.geometry("800x600")
        self.create_widgets()
        self.is_listening = False
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:5000")

    def create_widgets(self):
        # Input frame
        input_frame = ttk.Frame(self)
        input_frame.pack(pady=20)

        self.input_entry = ttk.Entry(input_frame, width=50)
        self.input_entry.pack(side=tk.LEFT, padx=5)

        submit_button = ttk.Button(input_frame, text="Submit", command=self.process_input)
        submit_button.pack(side=tk.LEFT)

        self.voice_button = ttk.Button(input_frame, text="Start Voice Input", command=self.toggle_voice_input)
        self.voice_button.pack(side=tk.LEFT, padx=5)

        # Output frame
        output_frame = ttk.Frame(self)
        output_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        self.output_text = tk.Text(output_frame, wrap=tk.WORD, width=80, height=20)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        add_ai_button = ttk.Button(button_frame, text="Add AI", command=self.open_add_ai_window)
        add_ai_button.pack(side=tk.LEFT, padx=5)

        ai_manager_button = ttk.Button(button_frame, text="AI Manager", command=self.open_ai_manager)
        ai_manager_button.pack(side=tk.LEFT, padx=5)

    def process_input(self):
        user_input = self.input_entry.get()
        if user_input:
            try:
                response = requests.post(f"{self.backend_url}/process", json={"input": user_input}, timeout=10)
                response.raise_for_status()
                output = response.json()['output']
                self.output_text.insert(tk.END, f"Input: {user_input}\nOutput: {output}\n\n")
            except requests.RequestException as e:
                messagebox.showerror("Error", f"Failed to process input: {str(e)}")
            finally:
                self.input_entry.delete(0, tk.END)

    def toggle_voice_input(self):
        if self.is_listening:
            self.is_listening = False
            self.voice_button.config(text="Start Voice Input")
        else:
            self.is_listening = True
            self.voice_button.config(text="Stop Voice Input")
            threading.Thread(target=self.voice_input_thread, daemon=True).start()

    def voice_input_thread(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            while self.is_listening:
                try:
                    audio = r.listen(source, timeout=1, phrase_time_limit=5)
                    text = r.recognize_google(audio)
                    self.input_entry.delete(0, tk.END)
                    self.input_entry.insert(0, text)
                    self.process_input()
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    print("Could not understand audio")
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")

    def open_add_ai_window(self):
        AddAIWindow(self)

    def open_ai_manager(self):
        AIManagerWindow(self)

class AddAIWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Add AI")
        self.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="AI Name:").pack(pady=5)
        self.name_entry = ttk.Entry(self, width=50)
        self.name_entry.pack(pady=5)

        ttk.Label(self, text="AI Type:").pack(pady=5)
        self.type_var = tk.StringVar()
        type_options = ["API", "Bot", "Local AI", "Custom AI"]
        self.type_dropdown = ttk.Combobox(self, textvariable=self.type_var, values=type_options, state="readonly")
        self.type_dropdown.pack(pady=5)
        self.type_dropdown.bind("<<ComboboxSelected>>", self.on_type_selected)

        self.details_frame = ttk.Frame(self)
        self.details_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        submit_button = ttk.Button(self, text="Add AI", command=self.submit_ai)
        submit_button.pack(pady=10)

    def on_type_selected(self, event):
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        ai_type = self.type_var.get()
        if ai_type == "API":
            ttk.Label(self.details_frame, text="API Key:").pack()
            self.api_key_entry = ttk.Entry(self.details_frame, width=50, show="*")
            self.api_key_entry.pack()
            ttk.Label(self.details_frame, text="Endpoint URL:").pack()
            self.endpoint_entry = ttk.Entry(self.details_frame, width=50)
            self.endpoint_entry.pack()
        elif ai_type == "Bot":
            ttk.Label(self.details_frame, text="Bot File:").pack()
            self.bot_file_entry = ttk.Entry(self.details_frame, width=40)
            self.bot_file_entry.pack(side=tk.LEFT)
            ttk.Button(self.details_frame, text="Browse", command=self.browse_bot_file).pack(side=tk.LEFT)
        elif ai_type == "Local AI":
            ttk.Label(self.details_frame, text="Command:").pack()
            self.command_entry = ttk.Entry(self.details_frame, width=50)
            self.command_entry.pack()
        elif ai_type == "Custom AI":
            ttk.Label(self.details_frame, text="Custom AI File:").pack()
            self.custom_ai_file_entry = ttk.Entry(self.details_frame, width=40)
            self.custom_ai_file_entry.pack(side=tk.LEFT)
            ttk.Button(self.details_frame, text="Browse", command=self.browse_custom_ai_file).pack(side=tk.LEFT)

        ttk.Label(self.details_frame, text="Description:").pack()
        self.description_text = tk.Text(self.details_frame, width=50, height=5)
        self.description_text.pack()

    def browse_bot_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if filename:
            self.bot_file_entry.delete(0, tk.END)
            self.bot_file_entry.insert(0, filename)

    def browse_custom_ai_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if filename:
            self.custom_ai_file_entry.delete(0, tk.END)
            self.custom_ai_file_entry.insert(0, filename)

    def submit_ai(self):
        name = self.name_entry.get()
        ai_type = self.type_var.get()
        description = self.description_text.get("1.0", tk.END).strip()

        if not name or not ai_type or not description:
            messagebox.showerror("Error", "Please fill all fields")
            return

        details = {"description": description}
        if ai_type == "API":
            details["api_key"] = self.api_key_entry.get()
            details["endpoint"] = self.endpoint_entry.get()
        elif ai_type == "Bot":
            details["file_path"] = self.bot_file_entry.get()
        elif ai_type == "Local AI":
            details["command"] = self.command_entry.get()
        elif ai_type == "Custom AI":
            details["file_path"] = self.custom_ai_file_entry.get()

        try:
            response = requests.post(f"{self.master.backend_url}/add_ai", json={
                "name": name,
                "type": ai_type,
                "details": details
            }, timeout=10)
            response.raise_for_status()
            messagebox.showinfo("Success", f"AI added successfully: {response.json()['message']}")
            self.destroy()
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to add AI: {str(e)}")

class AIManagerWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("AI Manager")
        self.geometry("600x400")
        self.create_widgets()
        self.load_ais()

    def create_widgets(self):
        self.ai_listbox = tk.Listbox(self, width=50)
        self.ai_listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Update", command=self.update_ai).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove", command=self.remove_ai).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.load_ais).pack(side=tk.LEFT, padx=5)

    def load_ais(self):
        try:
            response = requests.get(f"{self.master.backend_url}/list_ais", timeout=10)
            response.raise_for_status()
            ais = response.json()['ais']
            self.ai_listbox.delete(0, tk.END)
            for ai in ais:
                self.ai_listbox.insert(tk.END, f"{ai['name']} ({ai['type']}) - {ai['id']}")
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to load AIs: {str(e)}")

    def update_ai(self):
        selected = self.ai_listbox.curselection()
        if selected:
            ai_id = self.ai_listbox.get(selected[0]).split(" - ")[-1]
            UpdateAIWindow(self, ai_id)
        else:
            messagebox.showwarning("Warning", "Please select an AI to update.")

    def remove_ai(self):
        selected = self.ai_listbox.curselection()
        if selected:
            ai_id = self.ai_listbox.get(selected[0]).split(" - ")[-1]
            if messagebox.askyesno("Confirm", "Are you sure you want to remove this AI?"):
                try:
                    response = requests.post(f"{self.master.backend_url}/remove_ai", json={"id": ai_id}, timeout=10)
                    response.raise_for_status()
                    messagebox.showinfo("Success", f"AI removed successfully: {response.json()['message']}")
                    self.load_ais()
                except requests.RequestException as e:
                    messagebox.showerror("Error", f"Failed to remove AI: {str(e)}")
        else:
            messagebox.showwarning("Warning", "Please select an AI to remove.")

class UpdateAIWindow(tk.Toplevel):
    def __init__(self, master, ai_id):
        super().__init__(master)
        self.title("Update AI")
        self.geometry("400x300")
        self.ai_id = ai_id
        self.create_widgets()
        self.load_ai_details()

    def create_widgets(self):
        ttk.Label(self, text="Description:").pack(pady=5)
        self.description_text = tk.Text(self, width=50, height=5)
        self.description_text.pack(pady=5)

        self.details_frame = ttk.Frame(self)
        self.details_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        submit_button = ttk.Button(self, text="Update AI", command=self.submit_update)
        submit_button.pack(pady=10)

    def load_ai_details(self):
        try:
            response = requests.get(f"{self.master.master.backend_url}/get_ai", params={"id": self.ai_id}, timeout=10)
            response.raise_for_status()
            ai_details = response.json()['ai']
            self.description_text.insert(tk.END, ai_details['details'].get('description', ''))
            self.create_detail_fields(ai_details['type'], ai_details['details'])
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to load AI details: {str(e)}")

    def create_detail_fields(self, ai_type, details):
        if ai_type == "API":
            ttk.Label(self.details_frame, text="API Key:").pack()
            self.api_key_entry = ttk.Entry(self.details_frame, width=50, show="*")
            self.api_key_entry.insert(0, details.get('api_key', ''))
            self.api_key_entry.pack()
            ttk.Label(self.details_frame, text="Endpoint URL:").pack()
            self.endpoint_entry = ttk.Entry(self.details_frame, width=50)
            self.endpoint_entry.insert(0, details.get('endpoint', ''))
            self.endpoint_entry.pack()
        elif ai_type == "Bot":
            ttk.Label(self.details_frame, text="Bot File:").pack()
            self.bot_file_entry = ttk.Entry(self.details_frame, width=40)
            self.bot_file_entry.insert(0, details.get('file_path', ''))
            self.bot_file_entry.pack(side=tk.LEFT)
            ttk.Button(self.details_frame, text="Browse", command=self.browse_bot_file).pack(side=tk.LEFT)
        elif ai_type == "Local AI":
            ttk.Label(self.details_frame, text="Command:").pack()
            self.command_entry = ttk.Entry(self.details_frame, width=50)
            self.command_entry.insert(0, details.get('command', ''))
            self.command_entry.pack()
        elif ai_type == "Custom AI":
            ttk.Label(self.details_frame, text="Custom AI File:").pack()
            self.custom_ai_file_entry = ttk.Entry(self.details_frame, width=40)
            self.custom_ai_file_entry.insert(0, details.get('file_path', ''))
            self.custom_ai_file_entry.pack(side=tk.LEFT)
            ttk.Button(self.details_frame, text="Browse", command=self.browse_custom_ai_file).pack(side=tk.LEFT)

    def browse_bot_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if filename:
            self.bot_file_entry.delete(0, tk.END)
            self.bot_file_entry.insert(0, filename)

    def browse_custom_ai_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if filename:
            self.custom_ai_file_entry.delete(0, tk.END)
            self.custom_ai_file_entry.insert(0, filename)

    def submit_update(self):
        description = self.description_text.get("1.0", tk.END).strip()
        details = {"description": description}

        if hasattr(self, 'api_key_entry'):
            details["api_key"] = self.api_key_entry.get()
            details["endpoint"] = self.endpoint_entry.get()
        elif hasattr(self, 'bot_file_entry'):
            details["file_path"] = self.bot_file_entry.get()
        elif hasattr(self, 'command_entry'):
            details["command"] = self.command_entry.get()
        elif hasattr(self, 'custom_ai_file_entry'):
            details["file_path"] = self.custom_ai_file_entry.get()

        try:
            response = requests.post(f"{self.master.master.backend_url}/update_ai", json={
                "id": self.ai_id,
                "details": details
            }, timeout=10)
            response.raise_for_status()
            messagebox.showinfo("Success", f"AI updated successfully: {response.json()['message']}")
            self.master.load_ais()
            self.destroy()
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to update AI: {str(e)}")

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()