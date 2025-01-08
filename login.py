import tkinter as tk
from tkinter import messagebox
import os
import subprocess

# Create or open the text file to store user data
USER_DATA_FILE = "users.txt"
if not os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, "w") as file:
        pass

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Variable to track the currently logged-in user
current_user = None

def register_user():
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showerror("Error", "Both username and password are required!")
        return

    with open(USER_DATA_FILE, "r") as file:
        for line in file:
            existing_username, _ = line.strip().split(",")
            if username == existing_username:
                messagebox.showerror("Error", "Username already exists!")
                return

    with open(USER_DATA_FILE, "a") as file:
        file.write(f"{username},{password}\n")

    messagebox.showinfo("Success", "User registered successfully!")
    entry_username.delete(0, tk.END)
    entry_password.delete(0, tk.END)

def login_user():
    global current_user
    username = entry_username.get()
    password = entry_password.get()

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        current_user = username
        show_admin_panel()
        return

    if not username or not password:
        messagebox.showerror("Error", "Both username and password are required!")
        return

    with open(USER_DATA_FILE, "r") as file:
        for line in file:
            existing_username, existing_password = line.strip().split(",")
            if username == existing_username and password == existing_password:
                current_user = username
                messagebox.showinfo("Success", "Login successful!")
                run_gui()
                return

    messagebox.showerror("Error", "Invalid username or password!")

def show_admin_panel():
    clear_main_window()

    def delete_user():
        username_to_delete = entry_delete_username.get()

        if not username_to_delete:
            messagebox.showerror("Error", "Username is required to delete!")
            return

        with open(USER_DATA_FILE, "r") as file:
            lines = file.readlines()

        with open(USER_DATA_FILE, "w") as file:
            user_deleted = False
            for line in lines:
                existing_username, _ = line.strip().split(",")
                if existing_username != username_to_delete:
                    file.write(line)
                else:
                    user_deleted = True

        if user_deleted:
            messagebox.showinfo("Success", "User deleted successfully!")
        else:
            messagebox.showerror("Error", "User not found!")

    def view_users():
        with open(USER_DATA_FILE, "r") as file:
            users = file.readlines()

        users_list = [line.strip() for line in users]

        if users_list:
            users_display.configure(state="normal")
            users_display.delete(1.0, tk.END)
            users_display.insert(tk.END, "\n".join(users_list))
            users_display.configure(state="disabled")
        else:
            users_display.configure(state="normal")
            users_display.delete(1.0, tk.END)
            users_display.insert(tk.END, "No users found.")
            users_display.configure(state="disabled")
    
    def logout():
        show_main_screen()


    label_delete_username = tk.Label(app, text="Enter username to delete:")
    label_delete_username.pack(pady=5)
    entry_delete_username = tk.Entry(app)
    entry_delete_username.pack(pady=5)
    button_delete_user = tk.Button(app, text="Delete User", command=delete_user)
    button_delete_user.pack(pady=5)

    button_view_users = tk.Button(app, text="View Users", command=view_users)
    button_view_users.pack(pady=5)

    users_display = tk.Text(app, height=10, width=40, state="disabled")
    users_display.pack(pady=5)

    button_logout = tk.Button(app, text="Back to Login Screen", command=logout)
    button_logout.pack(pady=10)
    
def clear_main_window():
    for widget in app.winfo_children():
        widget.destroy()

def run_gui():
    if current_user:
        subprocess.run(["python", "gui.py", current_user])

# Create the main application window
app = tk.Tk()
app.title("Login System")

def show_main_screen():
    clear_main_window()

    # Username label and entry
    label_username = tk.Label(app, text="Username:")
    label_username.pack(pady=5)
    global entry_username
    entry_username = tk.Entry(app)
    entry_username.pack(pady=5)

    # Password label and entry
    label_password = tk.Label(app, text="Password:")
    label_password.pack(pady=5)
    global entry_password
    entry_password = tk.Entry(app, show="*")
    entry_password.pack(pady=5)

    # Buttons for register and login
    button_register = tk.Button(app, text="Register", command=register_user)
    button_register.pack(pady=5)

    button_login = tk.Button(app, text="Login", command=login_user)
    button_login.pack(pady=5)

def get_logged_in_user():
    if current_user:
        print(f"The logged-in user is: {current_user}")
    else:
        print("No user is currently logged in.")

show_main_screen()
app.mainloop()
get_logged_in_user()
