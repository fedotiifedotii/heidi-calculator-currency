#!/usr/bin/env python3
"""
Калькулятор + Конвертер валют и криптовалют
Автор: Хайди (для тебя)
Требования: Python 3 + tkinter + requests
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime

# ==================== НАСТРОЙКИ ====================
# Список валют (фиат + крипта)
CURRENCIES = {
    # Фиат
    "USD": "🇺🇸 Доллар США",
    "EUR": "🇪🇺 Евро",
    "RUB": "🇷🇺 Рубль",
    "CNY": "🇨🇳 Юань",
    "GBP": "🇬🇧 Фунт",
    "JPY": "🇯🇵 Иена",
    "KZT": "🇰🇿 Тенге",
    "UAH": "🇺🇦 Гривна",
    # Крипта
    "BTC": "₿ Bitcoin",
    "ETH": "Ξ Ethereum",
    "USDT": "₮ Tether",
    "BNB": "🟡 BNB",
    "SOL": "◎ Solana",
    "XRP": "✕ XRP",
    "TON": "💎 TON",
    "DOGE": "🐶 Dogecoin",
}

# Список криптовалют (для форматирования)
CRYPTO = {"BTC", "ETH", "USDT", "BNB", "SOL", "XRP", "TON", "DOGE"}


class CurrencyConverter:
    """Класс для получения живых курсов (frankfurter.dev + Coinbase)"""

    def __init__(self):
        self.cache = {}
        self.last_update = None

    def get_rates(self, base="USD"):
        """Получить курсы относительно base (всегда через USD внутри)"""
        try:
            rates = {"USD": 1.0}

            # 1. Фиат через frankfurter.dev (надёжный бесплатный API)
            fiat_url = "https://api.frankfurter.dev/v1/latest?from=USD"
            fiat_resp = requests.get(fiat_url, timeout=8)
            fiat_data = fiat_resp.json()
            rates.update(fiat_data.get("rates", {}))

            # 2. Крипта + дополнительные валюты через Coinbase
            cb_url = "https://api.coinbase.com/v2/exchange-rates?currency=USD"
            cb_resp = requests.get(cb_url, timeout=8)
            cb_data = cb_resp.json()
            cb_rates = cb_data.get("data", {}).get("rates", {})

            # Добавляем крипту и те валюты, которых нет у frankfurter (RUB, KZT, UAH и т.д.)
            wanted = list(CRYPTO) + ["RUB", "KZT", "UAH", "CNY"]
            for symbol in wanted:
                if symbol in cb_rates:
                    # Coinbase отдаёт "сколько этой валюты за 1 USD"
                    rates[symbol] = float(cb_rates[symbol])

            self.cache = rates
            self.last_update = datetime.now()
            return rates
        except Exception as e:
            print(f"Ошибка получения курсов: {e}")
            return self.cache or {}

    def convert(self, amount, from_cur, to_cur):
        """Конвертировать amount из from_cur в to_cur"""
        if from_cur == to_cur:
            return amount

        rates = self.get_rates("USD")

        if not rates:
            raise ValueError("Не удалось получить курсы. Проверь интернет.")

        # Приводим всё к USD
        if from_cur not in rates:
            raise ValueError(f"Неизвестная валюта: {from_cur}")
        if to_cur not in rates:
            raise ValueError(f"Неизвестная валюта: {to_cur}")

        amount_in_usd = amount / rates[from_cur] if from_cur != "USD" else amount
        result = amount_in_usd * rates[to_cur] if to_cur != "USD" else amount_in_usd
        return result


class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Хайди • Калькулятор + Конвертер")
        self.root.geometry("420x680")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        # Стиль
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#1e1e2e")
        style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4")
        style.configure("TButton", font=("Segoe UI", 11))
        style.configure("TCombobox", fieldbackground="#313244", foreground="#cdd6f4")

        self.converter = CurrencyConverter()
        self.expression = ""
        self.create_widgets()

    def create_widgets(self):
        # ========== ЗАГОЛОВОК ==========
        header = tk.Label(
            self.root,
            text="✨ Хайди Калькулятор",
            font=("Segoe UI", 16, "bold"),
            bg="#1e1e2e",
            fg="#cba6f7"
        )
        header.pack(pady=(15, 5))

        # ========== КАЛЬКУЛЯТОР ==========
        calc_frame = ttk.Frame(self.root)
        calc_frame.pack(padx=15, pady=5, fill="x")

        self.display = tk.Entry(
            calc_frame,
            font=("Consolas", 22),
            justify="right",
            bg="#313244",
            fg="#a6e3a1",
            insertbackground="#a6e3a1",
            relief="flat",
            bd=10
        )
        self.display.pack(fill="x", pady=(0, 10))
        self.display.insert(0, "0")

        # Кнопки калькулятора
        buttons = [
            ["C", "⌫", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "−"],
            ["1", "2", "3", "+"],
            ["±", "0", ".", "="],
        ]

        btn_frame = tk.Frame(calc_frame, bg="#1e1e2e")
        btn_frame.pack()

        for r, row in enumerate(buttons):
            for c, text in enumerate(row):
                color = "#45475a"
                fg = "#cdd6f4"
                if text in "÷×−+":
                    color = "#89b4fa"
                    fg = "#1e1e2e"
                elif text == "=":
                    color = "#a6e3a1"
                    fg = "#1e1e2e"
                elif text in ("C", "⌫"):
                    color = "#f38ba8"
                    fg = "#1e1e2e"

                btn = tk.Button(
                    btn_frame,
                    text=text,
                    width=5,
                    height=1,
                    font=("Segoe UI", 14, "bold"),
                    bg=color,
                    fg=fg,
                    activebackground="#585b70",
                    relief="flat",
                    command=lambda t=text: self.on_button(t)
                )
                btn.grid(row=r, column=c, padx=3, pady=3)

        # ========== РАЗДЕЛИТЕЛЬ ==========
        tk.Label(
            self.root,
            text="─────────── Конвертер валют ───────────",
            font=("Segoe UI", 10),
            bg="#1e1e2e",
            fg="#6c7086"
        ).pack(pady=(15, 8))

        # ========== КОНВЕРТЕР ==========
        conv_frame = ttk.Frame(self.root)
        conv_frame.pack(padx=15, fill="x")

        # Сумма
        tk.Label(conv_frame, text="Сумма:", font=("Segoe UI", 10), bg="#1e1e2e", fg="#cdd6f4").grid(row=0, column=0, sticky="w")
        self.amount_entry = tk.Entry(conv_frame, font=("Segoe UI", 12), bg="#313244", fg="#cdd6f4", relief="flat")
        self.amount_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=4, padx=5)
        self.amount_entry.insert(0, "100")

        # Из
        tk.Label(conv_frame, text="Из:", font=("Segoe UI", 10), bg="#1e1e2e", fg="#cdd6f4").grid(row=1, column=0, sticky="w")
        self.from_cur = ttk.Combobox(conv_frame, values=list(CURRENCIES.keys()), state="readonly", width=12)
        self.from_cur.grid(row=1, column=1, sticky="w", pady=4, padx=5)
        self.from_cur.set("USD")

        # В
        tk.Label(conv_frame, text="В:", font=("Segoe UI", 10), bg="#1e1e2e", fg="#cdd6f4").grid(row=2, column=0, sticky="w")
        self.to_cur = ttk.Combobox(conv_frame, values=list(CURRENCIES.keys()), state="readonly", width=12)
        self.to_cur.grid(row=2, column=1, sticky="w", pady=4, padx=5)
        self.to_cur.set("RUB")

        # Кнопка конвертации
        convert_btn = tk.Button(
            conv_frame,
            text="🔄 Конвертировать",
            font=("Segoe UI", 11, "bold"),
            bg="#cba6f7",
            fg="#1e1e2e",
            relief="flat",
            command=self.do_convert
        )
        convert_btn.grid(row=3, column=0, columnspan=3, sticky="ew", pady=10)

        # Результат
        self.result_label = tk.Label(
            conv_frame,
            text="Результат появится здесь",
            font=("Segoe UI", 12),
            bg="#313244",
            fg="#a6e3a1",
            wraplength=360,
            justify="center",
            pady=10
        )
        self.result_label.grid(row=4, column=0, columnspan=3, sticky="ew")

        # Время обновления
        self.update_label = tk.Label(
            conv_frame,
            text="",
            font=("Segoe UI", 8),
            bg="#1e1e2e",
            fg="#6c7086"
        )
        self.update_label.grid(row=5, column=0, columnspan=3, pady=5)

        conv_frame.columnconfigure(1, weight=1)

        # Подсказка
        tk.Label(
            self.root,
            text="Курсы: frankfurter.dev + Coinbase (живые)",
            font=("Segoe UI", 8),
            bg="#1e1e2e",
            fg="#585b70"
        ).pack(side="bottom", pady=8)

    def on_button(self, char):
        if char == "C":
            self.expression = ""
            self.display.delete(0, tk.END)
            self.display.insert(0, "0")
        elif char == "⌫":
            self.expression = self.expression[:-1]
            self.display.delete(0, tk.END)
            self.display.insert(0, self.expression if self.expression else "0")
        elif char == "=":
            try:
                # Заменяем символы на Python-операторы
                expr = self.expression.replace("×", "*").replace("÷", "/").replace("−", "-")
                result = eval(expr)
                self.display.delete(0, tk.END)
                self.display.insert(0, str(round(result, 10)).rstrip("0").rstrip(".") if isinstance(result, float) else str(result))
                self.expression = str(result)
            except:
                self.display.delete(0, tk.END)
                self.display.insert(0, "Ошибка")
                self.expression = ""
        elif char == "±":
            if self.expression and self.expression[0] == "-":
                self.expression = self.expression[1:]
            else:
                self.expression = "-" + self.expression
            self.display.delete(0, tk.END)
            self.display.insert(0, self.expression)
        elif char == "%":
            try:
                val = float(self.expression) / 100
                self.expression = str(val)
                self.display.delete(0, tk.END)
                self.display.insert(0, self.expression)
            except:
                pass
        else:
            if self.display.get() == "0" and char not in ".÷×−+":
                self.expression = char
            else:
                self.expression += char
            self.display.delete(0, tk.END)
            self.display.insert(0, self.expression)

    def do_convert(self):
        try:
            amount = float(self.amount_entry.get().replace(",", "."))
            from_c = self.from_cur.get()
            to_c = self.to_cur.get()

            result = self.converter.convert(amount, from_c, to_c)

            # Красивое форматирование
            if to_c in CRYPTO:
                formatted = f"{result:.8f}".rstrip("0").rstrip(".")
            else:
                formatted = f"{result:,.2f}".replace(",", " ")

            from_name = CURRENCIES.get(from_c, from_c)
            to_name = CURRENCIES.get(to_c, to_c)

            self.result_label.config(
                text=f"{amount} {from_c}  →  {formatted} {to_c}\n{from_name} → {to_name}"
            )

            if self.converter.last_update:
                self.update_label.config(
                    text=f"Обновлено: {self.converter.last_update.strftime('%H:%M:%S')}"
                )
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Что-то пошло не так:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()
