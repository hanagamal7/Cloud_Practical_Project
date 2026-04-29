import tkinter as tk
from tkinter import messagebox


def balance_screen(content_frame, is_logged_in, current_account, Account, update_screen, login_screen, operation_screen):
    """
    Displays the balance screen for the logged-in user.

    Args:
        content_frame: The Tkinter frame where the content is displayed.
        is_logged_in: Boolean indicating whether a user is logged in.
        current_account: Tuple containing details of the currently logged-in user.
        Account: The Account model for interacting with account-related methods.
        update_screen: Function to update the screen content.
        login_screen: The login screen function to redirect unauthorized users.
    """
    if not is_logged_in or not current_account:
        messagebox.showwarning("Access Denied", "You must log in first to perform this operation.")
        update_screen(login_screen)
        return

    # Clear previous content in the content frame
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Fetch the balance
    balance = Account.view_account_balance(current_account[0])  # `current_account[0]` is the ID of the logged-in user
    if balance is None:
        messagebox.showerror("Error", "Failed to retrieve balance.")
        return

    # Customize content_frame size and styling
    content_frame.config(width=800, height=300, bg="white")
    content_frame.pack_propagate(False)  # Prevent resizing based on content
    content_frame.grid_propagate(False)  # Prevent resizing in grid layout

    # Add a title
    title_label = tk.Label(
        content_frame,
        text="My Balance",
        font=("Helvetica", 30, "bold"),
        fg="black"
    )
    title_label.grid(row=0, column=0, columnspan=2, pady=20)

    # Display the balance
    balance_label = tk.Label(
        content_frame,
        text=f"Your current balance is: {balance:.2f} EGP",
        font=("Helvetica", 18),
        fg="black"
    )
    balance_label.grid(row=1, column=0, columnspan=2, pady=10)

    # Add an OK button to return to the operation screen
    ok_button = tk.Button(
        content_frame,
        text="OK",
        width=15,
        font=("Helvetica", 14, "bold"),
        bg="green",
        fg="white",
        activebackground="darkgreen",
        activeforeground="white",
        command=lambda: update_screen(operation_screen)
    )
    ok_button.grid(row=2, column=0, columnspan=2, pady=30)

    # Add spacing for better layout
    content_frame.grid_rowconfigure(3, weight=1)
    content_frame.grid_columnconfigure(0, weight=1)
    content_frame.grid_columnconfigure(1, weight=1)
