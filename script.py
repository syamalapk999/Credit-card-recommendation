import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tkcalendar import DateEntry
from PIL import Image, ImageTk

# Theme colors
COLORS = {
    "bg": "#F9F7F1",
    "accent": "#A7C1A8",
    "primary": "#819A91",
    "highlight": "#5F7161",
    "danger": "#C8553D",
    "text": "#333333"
}

# Card configs
cards = {
    "HDFC Regalia Gold": {
        "billing_day": 22,
        "due_offset_days": 20,
        "credit_limit": 300000,
        "reward": {
            "shopping": lambda amt: f"{round((amt / 150) * 4)} RP (~₹{round((amt / 150) * 4 * 0.5)})",
            "groceries": lambda amt: f"{round((amt / 150) * 4)} RP (~₹{round((amt / 150) * 4 * 0.5)})",
            "memberships": lambda amt: f"{round((amt / 150) * 4)} RP (~₹{round((amt / 150) * 4 * 0.5)})"
        }
    },
    "SBI SimplyCLICK": {
        "billing_day": 16,
        "due_offset_days": 20,
        "credit_limit": 30000,
        "reward": {
            "shopping": lambda amt: f"{int(amt / 100 * 10)} RP (~₹{int(amt / 100 * 10 * 0.25)})",
            "groceries": lambda amt: f"{int(amt / 100)} RP (~₹{int(amt / 100 * 0.25)})",
            "memberships": lambda amt: f"{int(amt / 100 * 5)} RP (~₹{int(amt / 100 * 5 * 0.25)})"
        }
    },
    "Flipkart Axis Bank": {
        "billing_day": 10,
        "due_offset_days": 20,
        "credit_limit": 140000,
        "reward": {
            "shopping": lambda amt: f"₹{round(amt * 0.015, 2)} cashback",
            "groceries": lambda amt: f"₹{round(amt * 0.02, 2)} cashback",
            "memberships": lambda amt: f"₹{round(amt * 0.015, 2)} cashback"
        }
    }
}

def get_billing_window(billing_day, ref_date):
    if ref_date.day >= billing_day:
        start = datetime(ref_date.year, ref_date.month, billing_day)
    else:
        prev = ref_date - relativedelta(months=1)
        start = datetime(prev.year, prev.month, billing_day)
    end = start + relativedelta(months=1)
    return start, end

def get_utilization(card_name, ref_date):
    return 0.0  # Simulation only

def recommend_card():
    try:
        amount = float(amount_var.get())
        if amount <= 0:
            raise ValueError
    except ValueError:
        result_label.config(text="❌ Please enter a valid amount.")
        return

    planned_date = datetime.combine(date_entry.get_date(), datetime.min.time())
    category = category_var.get()

    recommendations = []
    for card, info in cards.items():
        start, end = get_billing_window(info["billing_day"], planned_date)
        due = end + timedelta(days=info["due_offset_days"])

        if start <= planned_date <= end:
            util = get_utilization(card, planned_date)
            projected_util = util + amount
            util_percent = (projected_util / info["credit_limit"]) * 100
            reward = info["reward"][category](amount)
            days_to_due = (due - planned_date).days
            warning = f"\n⚠️ Utilization: {util_percent:.1f}% exceeds 30%" if util_percent > 30 else ""

            recommendations.append((
                card, reward, days_to_due, start.strftime("%b %d"),
                end.strftime("%b %d"), due.strftime("%b %d"), util_percent, warning
            ))

    if not recommendations:
        result_label.config(text="⚠️ No cards in active billing cycle.")
        card_image_label.config(image="", text="❌")
        return

    recommendations.sort(key=lambda x: x[2], reverse=True)
    best = recommendations[0]

    output = (
        f"✅ Recommended: {best[0]}\n"
        f"🏆 Reward: {best[1]}\n"
        f"🗓️ Billing: {best[3]} - {best[4]}\n"
        f"📅 Due: {best[5]} (in {best[2]} days)\n"
        f"💳 Utilization: {best[6]:.1f}%{best[7]}"
    )
    result_label.config(text=output)

    # Show image
    image_map = {
        "HDFC Regalia Gold": "hdfc.png",
        "SBI SimplyCLICK": "sbi.png",
        "Flipkart Axis Bank": "flipkart.png"
    }
    try:
        img_path = image_map[best[0]]
        img = Image.open(img_path)
        img = img.resize((300, 180), Image.LANCZOS)
        card_photo = ImageTk.PhotoImage(img)
        card_image_label.config(image=card_photo, text="")
        card_image_label.image = card_photo  # prevent garbage collection
    except Exception as e:
        card_image_label.config(image="", text="📷 Image not found")

# --- UI Setup ---
root = tk.Tk()
root.title("💳 Credit Card Advisor")
root.geometry("640x600")
root.configure(bg=COLORS["bg"])

style = ttk.Style()
style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10, "bold"))

title = ttk.Label(root, text="Smart Credit Card Recommender", font=("Segoe UI", 16, "bold"), foreground=COLORS["highlight"], background=COLORS["bg"])
title.pack(pady=20)

frame = ttk.Frame(root, padding=20)
frame.pack()

# Input variables
category_var = tk.StringVar(value="shopping")
amount_var = tk.StringVar(value="7000")

# Form Fields
ttk.Label(frame, text="Spending Category").grid(row=0, column=0, sticky="w", pady=6, padx=5)
category_dropdown = ttk.Combobox(frame, textvariable=category_var, values=["shopping", "groceries", "memberships"], state="readonly")
category_dropdown.grid(row=0, column=1, sticky="ew", pady=6, padx=5)

ttk.Label(frame, text="Purchase Amount (₹)").grid(row=1, column=0, sticky="w", pady=6, padx=5)
amount_entry = ttk.Entry(frame, textvariable=amount_var)
amount_entry.grid(row=1, column=1, sticky="ew", pady=6, padx=5)

ttk.Label(frame, text="Planned Purchase Date").grid(row=2, column=0, sticky="w", pady=6, padx=5)
date_entry = DateEntry(frame, width=19, background='gray20', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
date_entry.grid(row=2, column=1, sticky="ew", pady=6, padx=5)

frame.columnconfigure(1, weight=1)

# Recommendation Button
submit_btn = ttk.Button(root, text="🚀 Get Recommendation", command=recommend_card)
submit_btn.pack(pady=15)

# Result Output
result_label = ttk.Label(root, text="", wraplength=500, justify="left", font=("Segoe UI", 10, "italic"))
result_label.pack(pady=10)

# Image Display
card_image_label = ttk.Label(root)
card_image_label.pack(pady=10)

root.mainloop()
