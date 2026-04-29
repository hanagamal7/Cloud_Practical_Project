import tkinter as tk
from tkinter import messagebox
from models import Currency, Account


def ChangeCurrencyFunc_Screen(content_frame, is_logged_in, current_account, Account, update_screen, login_screen, operation_screen):
    if not is_logged_in or not current_account:
        messagebox.showwarning("Access Denied", "You must log in first to perform this operation.")
        update_screen(login_screen)
        return

    # Clear previous content in the content frame
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Customize content_frame size and styling
    content_frame.config(width=800, height=380, bg="white")
    content_frame.pack_propagate(False)  # Prevent resizing based on content
    content_frame.grid_propagate(False)  # Prevent resizing in grid layout

    # Add title
    title_label = tk.Label(
        content_frame,
        text="Change Currency",
        font=("Helvetica", 30, "bold"),
        fg="black"
    )
    title_label.grid(row=0, column=0, columnspan=2, pady=20)

    # Select Currency Label and Dropdown
    currency_label = tk.Label(
        content_frame,
        text="Select Currency:",
        font=("Helvetica", 20),
        anchor="w"
    )
    currency_label.grid(row=1, column=0, sticky="e", padx=20, pady=10)

    currency_var = tk.StringVar()
    currencies = Currency.get_all_currencies()
    if currencies:
        currency_var.set("Select Currency")  # Set default value
        currency_dropdown = tk.OptionMenu(content_frame, currency_var, *currencies)
        currency_dropdown.config(font=("Helvetica", 15))
        currency_dropdown.grid(row=1, column=1, padx=20, pady=10)

    # Enter Amount Label and Entry
    amount_label = tk.Label(
        content_frame,
        text="Enter Amount",
        font=("Helvetica", 20),
        anchor="w"
    )
    amount_label.grid(row=2, column=0, sticky="e", padx=20, pady=10)

    amount_entry = tk.Entry(content_frame, font=("Helvetica", 18), width=20)
    amount_entry.grid(row=2, column=1, padx=20, pady=10)

    # Perform Change Currency Logic
    def perform_ChangeCurrency(selected_currency, amount):
        if not is_logged_in:
            messagebox.showwarning("Access Denied", "You must log in first to perform this operation.")
            update_screen(login_screen)
            return

        if selected_currency == "Select Currency" or not selected_currency:
            messagebox.showerror("Currency Error", "Please select a valid currency type.")
            return

        try:
            amount_float = float(amount)
            if amount_float <= 0:
                raise ValueError("Amount must be greater than zero.")
        except ValueError as e:
            messagebox.showerror("Input Error", f"Enter a valid numeric amount. {str(e)}")
            return

        conversion_rate = Currency.get_conversion_rate(selected_currency)
        if conversion_rate is None:
            messagebox.showerror("Currency Error", "Selected currency not found.")
            return

        try:
            egp_amount = amount_float * conversion_rate
        except ValueError:
            messagebox.showerror("Conversion Error", "Failed to calculate the EGP equivalent.")
            return

        result = Account.update_account_balance(current_account[0], egp_amount)
        if result:
            messagebox.showinfo(
                "Success",
                f"Transferred {amount_float} {selected_currency} to your balance.\nConverted Amount: {egp_amount:.2f} EGP."
            )
            update_screen(operation_screen)
        else:
            messagebox.showerror("Error", "Failed to update the balance.")

    # Submit Button
    submit_button = tk.Button(
        content_frame,
        text="Change Currency",
        width=20,
        font=("Helvetica", 14, "bold"),
        bg="green",
        fg="white",
        activebackground="darkgreen",
        activeforeground="white",
        command=lambda: perform_ChangeCurrency(currency_var.get(), amount_entry.get())
    )
    submit_button.grid(row=3, column=0, columnspan=2, pady=20)

    # Add spacing for responsiveness
    content_frame.grid_rowconfigure(4, weight=1)
    content_frame.grid_columnconfigure(0, weight=1)
    content_frame.grid_columnconfigure(1, weight=1)
