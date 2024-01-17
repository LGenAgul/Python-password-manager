import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from cryptography.fernet import Fernet,InvalidToken
import os
import sqlite3
#http://sanet.st/
class PasswordManager:
    def __init__(self, db_path="password.db"):
        self.key = None
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

        # Create a table to store passwords if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                site TEXT PRIMARY KEY,
                encrypted_password TEXT
            )
        ''')
        self.connection.commit()

    def create_key(self, path):
        # Check if the key file already exists
        if not os.path.exists(path):
            self.key = Fernet.generate_key()
            with open(path, 'wb') as file:
                file.write(self.key)
            print("Key successfully created")
        else:
            # If the key file exists, load the existing key
            self.load_key(path)
            print("Key already exists, loaded from file")

    def load_key(self, path):
        with open(path, 'rb') as file:
            self.key = file.read()
        print("Key successfully loaded")

    def add_password(self, site, password):
        encrypted = Fernet(self.key).encrypt(password.encode()).decode()
        self.cursor.execute("INSERT OR REPLACE INTO passwords (site, encrypted_password) VALUES (?, ?)", (site, encrypted))
        self.connection.commit()

    def load_passwords_from_database(self):
        self.password_dict = {}
        self.cursor.execute("SELECT site, encrypted_password FROM passwords")
        rows = self.cursor.fetchall()
        for row in rows:
            site, encrypted = row
            decrypted_password = Fernet(self.key).decrypt(encrypted.encode()).decode()
            self.password_dict[site] = decrypted_password
            

    def get_password(self, site):
        return self.password_dict.get(site)

def load_passwords_from_database_handler(password_manager, return_text, search_string=None):
    return_string = ""
    password_manager.load_passwords_from_database()

    if search_string is not None:
        # Filter passwords based on the search string
        filtered_passwords = {site: password for site, password in password_manager.password_dict.items() if search_string.lower() in site.lower()}

        if filtered_passwords:
            # Print or display the filtered passwords
            return_string = " Passwords:\n"
            for site, password in filtered_passwords.items():
                return_string += f"Site: {site}, Password: {password}\n"
        else:
            return_string = "No matching passwords found."
    else:
        # If no search string provided, show all passwords
        passwords = password_manager.password_dict
        return_string = "All Passwords:\n"
        for site, password in passwords.items():
            return_string += f"Site: {site}, Password: {password}\n"

    # Update the return text widget with the result
    return_text.configure(text=return_string)



def add_password_handler(password_manager, site_entry, password_entry, status_label):
    site = site_entry.get()
    password = password_entry.get()
    
    if site and password:
        password_manager.add_password(site, password)
        status_label.configure(text=f"Password added for {site}!")
        site_entry.delete(0, tk.END)  # Clear site input
        password_entry.delete(0, tk.END)  # Clear password input
    else:
        status_label.configure(text="Site and Password fields\n cannot be empty.")


def main():
    passwords = {"test":"test"}

    pm = PasswordManager()
    key_path = "D:\\python\\password manager\\keys\\key.key"
    file_path = "D:\\python\\password manager\\passwords\\passwords.txt"

    # Create directories if they don't exist
    os.makedirs(os.path.dirname(key_path), exist_ok=True)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    #GUI
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
   
    root = ctk.CTk()
    root.geometry("800x600")
    #Program header
    title = ctk.CTkLabel(master=root,text="Password Manager",font=("Segoe UI Black",50))
    title.pack()
    #the program should create and load the key when the program is run
    pm.create_key(key_path)
    pm.load_key(key_path)
   
  
   
    frame1 = ctk.CTkFrame(root,width=200,height=500)
    frame1.place(relx=0,y=100, rely=0, relwidth=0.5, relheight=1)
  
    site_label = ctk.CTkLabel(frame1,text="your prefered site",font=("Segoe UI Black",25))
    site_label.place(relx=0.4, rely=0.05, anchor="center")
  
    site_input = ctk.CTkEntry(frame1,placeholder_text="type your site",font=("Segoe UI Black",20),width=300)
    site_input.place(relx=0.5, rely=0.12, anchor="center")
    password_label = ctk.CTkLabel(frame1,text="your password      ",font=("Segoe UI Black",25))
    password_label.place(relx=0.4, rely=0.19, anchor="center")

    password_input = ctk.CTkEntry(frame1,placeholder_text="type your password",font=("Segoe UI Black",20),width=300)
    password_input.place(relx=0.5, rely=0.26, anchor="center")
    
    status_label =  ctk.CTkLabel(frame1,text="",font=("Segoe UI Black",20))
    status_label.place(relx=0.40, rely=0.45, anchor="n")
    
    button = ctk.CTkButton(frame1,fg_color="grey", text="add password", command=lambda:add_password_handler(pm,site_input,password_input,status_label),font=("Segoe UI Black",25))
    button.place(relx=0.35, rely=0.35, anchor="center")
    
   #frame2
    frame2 = ctk.CTkFrame(root,width=150,height=500)
    frame2.place(relx=0.50,x=50,y=100, rely=0, relwidth=0.75, relheight=1)
 
    search_input = ctk.CTkEntry(frame2,placeholder_text="narrow your search...",font=("Segoe UI Black",20),width=300)
    search_input.place(relx=0.30, rely=0.05, anchor="center")
    
    return_text =  ctk.CTkLabel(frame2,text="",font=("Segoe UI Black",15))
    return_text.place(relx=0.3, rely=0.25, anchor="center")
    
    return_button = ctk.CTkButton(frame2, fg_color="grey", text="get your passwords", 
    command=lambda:load_passwords_from_database_handler(pm,return_text,search_input.get()), font=("Segoe UI Black", 25))
    return_button.place(relx=0.26, rely=0.15, anchor="center")
 
        
    root.mainloop()

if __name__ == "__main__":
    main()

