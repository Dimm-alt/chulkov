import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x600")
        self.expenses = self.load_data()
        self.categories = ["Еда", "Транспорт", "Развлечения", "Жильё", "Прочее"]
        self.setup_ui()

    def setup_ui(self):
        # Панель добавления
        top = tk.Frame(self.root)
        top.pack(pady=10)
        
        tk.Label(top, text="Сумма:").grid(row=0, column=0, padx=5)
        self.amount = tk.Entry(top, width=15)
        self.amount.grid(row=0, column=1, padx=5)
        
        tk.Label(top, text="Категория:").grid(row=0, column=2, padx=5)
        self.category = ttk.Combobox(top, values=self.categories, width=12)
        self.category.grid(row=0, column=3, padx=5)
        
        tk.Label(top, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5)
        self.date = tk.Entry(top, width=12)
        self.date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date.grid(row=0, column=5, padx=5)
        
        tk.Button(top, text="+", command=self.add, bg="#4CAF50", width=5).grid(row=0, column=6, padx=5)
        
        # Панель фильтров
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(pady=5)
        
        tk.Label(filter_frame, text="Фильтр:").pack(side="left", padx=5)
        self.filter_cat = ttk.Combobox(filter_frame, values=["Все"] + self.categories, width=12)
        self.filter_cat.set("Все")
        self.filter_cat.pack(side="left", padx=5)
        
        tk.Label(filter_frame, text="Дата от:").pack(side="left", padx=5)
        self.date_from = tk.Entry(filter_frame, width=12)
        self.date_from.pack(side="left", padx=5)
        
        tk.Label(filter_frame, text="до:").pack(side="left", padx=5)
        self.date_to = tk.Entry(filter_frame, width=12)
        self.date_to.pack(side="left", padx=5)
        
        tk.Button(filter_frame, text="Применить", command=self.filter).pack(side="left", padx=5)
        tk.Button(filter_frame, text="Сброс", command=self.reset_filter).pack(side="left", padx=5)
        
        # Таблица
        cols = ("Сумма", "Категория", "Дата")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings", height=15)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Кнопки действий
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        
        tk.Button(btn_frame, text="Удалить", command=self.delete, bg="#f44336").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Показать сумму", command=self.total).pack(side="left", padx=5)
        
        self.total_label = tk.Label(self.root, text="Общая сумма: 0", font=("Arial", 12, "bold"))
        self.total_label.pack(pady=5)
        
        self.update_table()

    def add(self):
        try:
            amount = float(self.amount.get())
            if amount <= 0: raise ValueError
            datetime.strptime(self.date.get(), "%Y-%m-%d")
            if not self.category.get(): raise ValueError
            
            self.expenses.append({
                "amount": amount,
                "category": self.category.get(),
                "date": self.date.get()
            })
            self.save()
            self.update_table()
            self.amount.delete(0, tk.END)
            self.category.set("")
            messagebox.showinfo("", "Добавлено!")
        except:
            messagebox.showerror("Ошибка", "Проверьте данные")

    def delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("", "Выберите запись")
            return
        if messagebox.askyesno("", "Удалить?"):
            idx = self.tree.index(selected[0])
            del self.expenses[idx]
            self.save()
            self.update_table()

    def filter(self):
        filtered = self.expenses
        
        cat = self.filter_cat.get()
        if cat != "Все":
            filtered = [e for e in filtered if e["category"] == cat]
        
        frm = self.date_from.get()
        to = self.date_to.get()
        
        try:
            if frm:
                frm_date = datetime.strptime(frm, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") >= frm_date]
            if to:
                to_date = datetime.strptime(to, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") <= to_date]
        except:
            messagebox.showerror("Ошибка", "Неверный формат даты")
            return
        
        self.show_filtered(filtered)

    def reset_filter(self):
        self.filter_cat.set("Все")
        self.date_from.delete(0, tk.END)
        self.date_to.delete(0, tk.END)
        self.update_table()

    def show_filtered(self, filtered):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for e in filtered:
            self.tree.insert("", "end", values=(e["amount"], e["category"], e["date"]))
        self.calc_total(filtered)

    def total(self):
        self.calc_total(self.expenses)

    def calc_total(self, expenses=None):
        if expenses is None:
            expenses = self.expenses
        total = sum(e["amount"] for e in expenses)
        self.total_label.config(text=f"Общая сумма: {total:.2f}")

    def update_table(self):
        self.show_filtered(self.expenses)

    def save(self):
        with open("expenses.json", "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=2)

    def load_data(self):
        try:
            with open("expenses.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
