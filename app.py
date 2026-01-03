"""
Yandex Music Discord RPC - Главное приложение с GUI
by @nevercr7
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import threading
import sys
import os
import winreg

from settings import (
    load_settings, save_settings, get_token, set_token,
    is_first_run, DISCORD_CLIENT_ID, is_autostart_enabled, set_autostart_enabled
)
from auth import open_auth_page, extract_token_from_url, OAUTH_URL


class SetupWindow:
    """Окно первоначальной настройки (получение токена)"""
    
    def __init__(self, on_complete):
        self.on_complete = on_complete
        self.root = tk.Tk()
        self.root.title("Yandex Music RPC - Настройка")
        self.root.geometry("550x580")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")
        
        # Центрируем окно
        self.center_window()
        
        self.create_widgets()
    
    def center_window(self):
        self.root.update_idletasks()
        width = 550
        height = 580
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Заголовок
        title = tk.Label(
            self.root,
            text="🎵 Yandex Music RPC",
            font=("Segoe UI", 20, "bold"),
            fg="#e94560",
            bg="#1a1a2e"
        )
        title.pack(pady=15)
        
        subtitle = tk.Label(
            self.root,
            text="by @nevercr7",
            font=("Segoe UI", 10),
            fg="#888888",
            bg="#1a1a2e"
        )
        subtitle.pack()
        
        # Инструкция
        instruction_frame = tk.Frame(self.root, bg="#1a1a2e")
        instruction_frame.pack(pady=15, padx=30, fill="x")
        
        instruction = tk.Label(
            instruction_frame,
            text="Для работы приложения нужна авторизация в Yandex Music.\n\n"
                 "1. Нажмите кнопку «Открыть авторизацию»\n"
                 "2. Войдите в свой Yandex аккаунт\n"
                 "3. После авторизации скопируйте URL из адресной строки\n"
                 "4. Вставьте URL в поле ниже",
            font=("Segoe UI", 11),
            fg="#ffffff",
            bg="#1a1a2e",
            justify="left"
        )
        instruction.pack()
        
        # Кнопка открытия авторизации
        self.auth_btn = tk.Button(
            self.root,
            text="🔑 Открыть авторизацию",
            font=("Segoe UI", 12, "bold"),
            bg="#e94560",
            fg="white",
            activebackground="#c73e54",
            activeforeground="white",
            border=0,
            cursor="hand2",
            width=25,
            command=self.open_auth
        )
        self.auth_btn.pack(pady=15, ipady=10)
        
        # Поле ввода URL/токена
        url_frame = tk.Frame(self.root, bg="#1a1a2e")
        url_frame.pack(pady=10, padx=30, fill="x")
        
        url_label = tk.Label(
            url_frame,
            text="Вставьте URL или токен:",
            font=("Segoe UI", 10),
            fg="#888888",
            bg="#1a1a2e"
        )
        url_label.pack(anchor="w")
        
        self.url_entry = tk.Entry(
            url_frame,
            font=("Segoe UI", 10),
            bg="#16213e",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat"
        )
        self.url_entry.pack(fill="x", pady=5, ipady=8)
        
        # Исправление вставки на русской раскладке
        self.url_entry.bind('<Control-Key>', lambda e: self._on_ctrl_key(e, self.url_entry))
        
        # Подсказка
        hint = tk.Label(
            url_frame,
            text="URL будет выглядеть как: https://oauth.yandex.ru/...#access_token=...",
            font=("Segoe UI", 8),
            fg="#555555",
            bg="#1a1a2e"
        )
        hint.pack(anchor="w")
        
        # Статус
        self.status_label = tk.Label(
            self.root,
            text="",
            font=("Segoe UI", 10),
            fg="#888888",
            bg="#1a1a2e"
        )
        self.status_label.pack(pady=10)
        
        # Кнопка сохранения
        save_btn = tk.Button(
            self.root,
            text="     ✓ Сохранить и продолжить     ",
            font=("Segoe UI", 12, "bold"),
            bg="#4ecca3",
            fg="white",
            activebackground="#3db892",
            activeforeground="white",
            border=0,
            cursor="hand2",
            command=self.save_token
        )
        save_btn.pack(pady=10, ipady=12, ipadx=20)
        
        # Ссылки
        links_frame = tk.Frame(self.root, bg="#1a1a2e")
        links_frame.pack(pady=15)
        
        help_link = tk.Label(
            links_frame,
            text="Как получить токен?",
            font=("Segoe UI", 9, "underline"),
            fg="#888888",
            bg="#1a1a2e",
            cursor="hand2"
        )
        help_link.pack(side="left", padx=15)
        help_link.bind("<Button-1>", lambda e: webbrowser.open(
            "https://github.com/MarshalX/yandex-music-api/discussions/513"
        ))
        
        tg_link = tk.Label(
            links_frame,
            text="Telegram",
            font=("Segoe UI", 9, "underline"),
            fg="#4ecca3",
            bg="#1a1a2e",
            cursor="hand2"
        )
        tg_link.pack(side="left", padx=15)
        tg_link.bind("<Button-1>", lambda e: webbrowser.open("https://t.me/nevercr7"))
        
        gh_link = tk.Label(
            links_frame,
            text="GitHub",
            font=("Segoe UI", 9, "underline"),
            fg="#4ecca3",
            bg="#1a1a2e",
            cursor="hand2"
        )
        gh_link.pack(side="left", padx=15)
        gh_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Nevercr7"))
    
    def _on_ctrl_key(self, event, entry):
        """Обработка Ctrl+клавиша для русской раскладки"""
        # keycode 86 = V на любой раскладке
        if event.keycode == 86:
            self._paste_to_entry(entry)
            return "break"
    
    def _paste_to_entry(self, entry):
        """Вставить текст из буфера обмена в поле ввода"""
        try:
            text = self.root.clipboard_get()
            entry.delete(0, tk.END)
            entry.insert(0, text)
        except tk.TclError:
            pass  # Буфер обмена пуст
        return "break"
    
    def open_auth(self):
        """Открыть страницу авторизации"""
        open_auth_page()
        self.status_label.config(
            text="Браузер открыт. После входа скопируйте URL и вставьте выше.",
            fg="#4ecca3"
        )
    
    def save_token(self):
        """Сохранить токен"""
        url_or_token = self.url_entry.get().strip()
        
        if not url_or_token:
            self.status_label.config(text="✗ Вставьте URL или токен!", fg="#e94560")
            return
        
        # Пробуем извлечь токен
        token = extract_token_from_url(url_or_token)
        
        if not token:
            self.status_label.config(
                text="✗ Не удалось извлечь токен. Проверьте URL.",
                fg="#e94560"
            )
            return
        
        if len(token) < 30:
            self.status_label.config(
                text="✗ Токен слишком короткий. Проверьте URL.",
                fg="#e94560"
            )
            return
        
        # Сохраняем токен
        set_token(token)
        self.status_label.config(text="✓ Токен сохранён!", fg="#4ecca3")
        self.root.update()
        self.root.after(1000, self._complete)
    
    def _complete(self):
        """Завершить настройку"""
        self.root.destroy()
        self.on_complete()
    
    def run(self):
        self.root.mainloop()


class MainWindow:
    """Главное окно приложения"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Yandex Music RPC")
        self.root.geometry("420x420")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")
        
        # Центрируем
        self.center_window()
        
        self.is_running = False
        self.tray_app = None
        
        self.create_widgets()
        
        # Обработчик закрытия
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def center_window(self):
        self.root.update_idletasks()
        width = 420
        height = 420
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Заголовок
        title = tk.Label(
            self.root,
            text="🎵 Yandex Music RPC",
            font=("Segoe UI", 18, "bold"),
            fg="#e94560",
            bg="#1a1a2e"
        )
        title.pack(pady=15)
        
        subtitle = tk.Label(
            self.root,
            text="by @nevercr7",
            font=("Segoe UI", 9),
            fg="#888888",
            bg="#1a1a2e"
        )
        subtitle.pack()
        
        # Статус
        self.status_label = tk.Label(
            self.root,
            text="⏹ Остановлено",
            font=("Segoe UI", 11),
            fg="#888888",
            bg="#1a1a2e"
        )
        self.status_label.pack(pady=15)
        
        # Кнопки
        btn_frame = tk.Frame(self.root, bg="#1a1a2e")
        btn_frame.pack(pady=10)
        
        # Кнопка запуска
        self.start_btn = tk.Button(
            btn_frame,
            text="▶ Запустить",
            font=("Segoe UI", 12, "bold"),
            bg="#4ecca3",
            fg="white",
            activebackground="#3db892",
            activeforeground="white",
            border=0,
            cursor="hand2",
            width=20,
            command=self.start_rpc
        )
        self.start_btn.pack(pady=5, ipady=10)
        
        # Кнопка автозапуска
        self.autostart_var = tk.BooleanVar(value=is_autostart_enabled())
        
        autostart_frame = tk.Frame(self.root, bg="#1a1a2e")
        autostart_frame.pack(pady=10)
        
        self.autostart_btn = tk.Button(
            autostart_frame,
            text="📌 Добавить в автозапуск" if not self.autostart_var.get() else "📌 Убрать из автозапуска",
            font=("Segoe UI", 10),
            bg="#16213e",
            fg="white",
            activebackground="#1f2b47",
            activeforeground="white",
            border=0,
            cursor="hand2",
            width=25,
            command=self.toggle_autostart
        )
        self.autostart_btn.pack(ipady=6)
        
        # Кнопка настроек токена
        settings_btn = tk.Button(
            self.root,
            text="⚙ Изменить токен",
            font=("Segoe UI", 10),
            bg="#16213e",
            fg="#888888",
            activebackground="#1f2b47",
            activeforeground="white",
            border=0,
            cursor="hand2",
            width=25,
            command=self.change_token
        )
        settings_btn.pack(pady=5, ipady=6)
        
        # Ссылки
        links_frame = tk.Frame(self.root, bg="#1a1a2e")
        links_frame.pack(pady=20)
        
        tg_link = tk.Label(
            links_frame,
            text="Telegram",
            font=("Segoe UI", 9, "underline"),
            fg="#4ecca3",
            bg="#1a1a2e",
            cursor="hand2"
        )
        tg_link.pack(side="left", padx=10)
        tg_link.bind("<Button-1>", lambda e: webbrowser.open("https://t.me/nevercr7"))
        
        gh_link = tk.Label(
            links_frame,
            text="GitHub",
            font=("Segoe UI", 9, "underline"),
            fg="#4ecca3",
            bg="#1a1a2e",
            cursor="hand2"
        )
        gh_link.pack(side="left", padx=10)
        gh_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Nevercr7"))
    
    def start_rpc(self):
        """Запустить RPC и свернуть в трей"""
        self.is_running = True
        self.status_label.config(text="▶ Запускается...", fg="#4ecca3")
        self.root.update()
        
        # Скрываем окно
        self.root.withdraw()
        
        # Запускаем tray в отдельном потоке
        def run_tray():
            try:
                from tray_app import YandexMusicRPCTray
                self.tray_app = YandexMusicRPCTray(
                    on_quit=self.on_tray_quit,
                    on_open=self.on_tray_open
                )
                self.tray_app.run()
            except Exception as e:
                self.root.after(0, lambda: self.show_error(str(e)))
        
        thread = threading.Thread(target=run_tray, daemon=True)
        thread.start()
    
    def on_tray_quit(self):
        """Callback при выходе из трея"""
        self.is_running = False
        self.root.after(0, self.quit_app)
    
    def on_tray_open(self):
        """Callback при открытии из трея"""
        self.is_running = False
        self.root.after(0, self.show_window)
    
    def quit_app(self):
        """Полностью закрыть приложение"""
        self.root.destroy()
    
    def show_window(self):
        """Показать главное окно"""
        self.root.deiconify()
        self.status_label.config(text="⏹ Остановлено", fg="#888888")
    
    def show_error(self, error):
        """Показать ошибку"""
        self.root.deiconify()
        self.status_label.config(text="❌ Ошибка", fg="#e94560")
        messagebox.showerror("Ошибка", error)
    
    def toggle_autostart(self):
        """Переключить автозапуск"""
        current = self.autostart_var.get()
        
        if current:
            # Убираем из автозапуска
            if self.remove_from_autostart():
                self.autostart_var.set(False)
                set_autostart_enabled(False)
                self.autostart_btn.config(text="📌 Добавить в автозапуск")
                messagebox.showinfo("Готово", "Приложение убрано из автозапуска")
        else:
            # Добавляем в автозапуск
            if self.add_to_autostart():
                self.autostart_var.set(True)
                set_autostart_enabled(True)
                self.autostart_btn.config(text="📌 Убрать из автозапуска")
                messagebox.showinfo("Готово", "Приложение добавлено в автозапуск")
    
    def add_to_autostart(self) -> bool:
        """Добавить в автозапуск"""
        try:
            # Определяем путь к exe или скрипту
            if getattr(sys, 'frozen', False):
                # Запущено как exe
                app_path = f'"{sys.executable}"'
            else:
                # Запущено как скрипт
                script_path = os.path.abspath(__file__)
                python_path = sys.executable
                pythonw_path = python_path.replace("python.exe", "pythonw.exe")
                if os.path.exists(pythonw_path):
                    app_path = f'"{pythonw_path}" "{script_path}"'
                else:
                    app_path = f'"{python_path}" "{script_path}"'
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "YandexMusicRPC", 0, winreg.REG_SZ, app_path)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить в автозапуск:\n{e}")
            return False
    
    def remove_from_autostart(self) -> bool:
        """Убрать из автозапуска"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            winreg.DeleteValue(key, "YandexMusicRPC")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось убрать из автозапуска:\n{e}")
            return False
    
    def change_token(self):
        """Открыть окно изменения токена"""
        self.root.destroy()
        setup = SetupWindow(on_complete=start_main_window)
        setup.run()
    
    def on_close(self):
        """Обработчик закрытия окна"""
        if self.is_running and self.tray_app:
            # Если RPC работает, просто скрываем окно
            self.root.withdraw()
        else:
            self.root.destroy()
    
    def run(self):
        self.root.mainloop()


def start_main_window():
    """Запустить главное окно"""
    app = MainWindow()
    app.run()


def main():
    """Точка входа"""
    if is_first_run():
        # Первый запуск - показываем настройку
        setup = SetupWindow(on_complete=start_main_window)
        setup.run()
    else:
        # Не первый запуск - главное окно
        start_main_window()


if __name__ == "__main__":
    main()
