import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import threading
from built_diagram import get_data, build_figure


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Аналіз нерухомості - Детектор шахрайства')
        self.geometry('900x620')
        self.configure(bg='#1e1e2e')
        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self, bg='#1e1e2e')
        header.pack(fill='x', padx=20, pady=(20, 0))

        tk.Label(
            header, text='Аналіз на скам оголошень нерухомості',
            font=('Segoe UI', 18, 'bold'),
            bg='#1e1e2e', fg='#cdd6f4',
        ).pack(side='left')

        self.stat_frame = tk.Frame(self, bg='#313244', pady=10)
        self.stat_frame.pack(fill='x', padx=20, pady=10)

        self.lbl_total    = self._stat_label('Всього: -')
        self.lbl_clean    = self._stat_label('✅ Справжніх: -', '#a6e3a1')
        self.lbl_suspect  = self._stat_label('⚠️ Сумнівних: -', '#f9e2af')
        self.lbl_scam     = self._stat_label('🚨 Шахрайських: -', '#f38ba8')
        self.lbl_avg      = self._stat_label('Середній ризик: -')

        hist_frame = tk.Frame(self, bg='#1e1e2e')
        hist_frame.pack(fill='x', padx=20, pady=(0, 8))

        tk.Label(
            hist_frame, text='Попередні аналізи:',
            font=('Segoe UI', 10), bg='#1e1e2e', fg='#6c7086',
        ).pack(side='left', padx=(0, 10))

        self.history_var = tk.StringVar()
        self.history_box = ttk.Combobox(
            hist_frame, textvariable=self.history_var,
            state='readonly', width=35,
            font=('Segoe UI', 9),
        )
        self.history_box.pack(side='left')
        self.history_box.bind('<<ComboboxSelected>>', self._on_history_select)

        self.canvas_frame = tk.Frame(self, bg='#181825', relief='flat', bd=0)
        self.canvas_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))

        self.status_lbl = tk.Label(
            self.canvas_frame,
            text='Натисни «Згенерувати діаграму» щоб побачити аналіз',
            font=('Segoe UI', 13), bg='#181825', fg='#6c7086',
        )
        self.status_lbl.place(relx=0.5, rely=0.5, anchor='center')

        btn_frame = tk.Frame(self, bg='#1e1e2e')
        btn_frame.pack(fill='x', padx=20, pady=(0, 20))

        self.btn = tk.Button(
            btn_frame,
            text='ЗГЕНЕРУВАТИ',
            font=('Segoe UI', 12, 'bold'),
            bg='#89b4fa', fg='#1e1e2e',
            activebackground='#74c7ec',
            relief='flat', padx=20, pady=10, cursor='hand2',
            command=self._on_generate,
        )
        self.btn.pack(side='left')

        self.progress = ttk.Progressbar(btn_frame, mode='indeterminate', length=200)
        self.progress.pack(side='left', padx=(16, 0))

        self._refresh_history()

    def _stat_label(self, text, fg='#cdd6f4'):
        lbl = tk.Label(
            self.stat_frame, text=text,
            font=('Segoe UI', 10, 'bold'),
            bg='#313244', fg=fg, padx=14,
        )
        lbl.pack(side='left')
        return lbl

    def _refresh_history(self):
        try:
            with sqlite3.connect('result_by_AI.db') as conn:
                dates = conn.execute(
                    "SELECT DISTINCT DATE(analysed_at) FROM results_analyse ORDER BY analysed_at DESC"
                ).fetchall()
            self.history_box['values'] = [row[0] for row in dates]
            if dates:
                self.history_box.current(0)
        except Exception:
            self.history_box['values'] = []

    def _on_history_select(self, _event=None):
        selected_date = self.history_var.get()
        if not selected_date:
            return
        threading.Thread(
            target=self._generate, args=(selected_date,), daemon=True
        ).start()

    def _on_generate(self):
        self.btn.config(state='disabled')
        self.progress.start(12)
        self.status_lbl.config(text='Завантаження даних…', fg='#89b4fa')
        threading.Thread(target=self._generate, daemon=True).start()

    def _generate(self, filter_date=None):
        try:
            data = get_data(filter_date=filter_date)

            if not data:
                self.after(0, lambda: self.status_lbl.config(
                    text='Немає даних для відображення', fg='#f38ba8'))
                return

            self._update_stats(data)
            fig = build_figure(data)

            self.after(0, lambda: self.status_lbl.config(
                text=f'Діаграма відкрита в браузері ({len(data)} оголошень)',
                fg='#a6e3a1',
            ))
            fig.show()

        except Exception as e:
            self.after(0, lambda: messagebox.showerror('Помилка', str(e)))
        finally:
            self.after(0, self._done)

    def _update_stats(self, data):
        total   = len(data)
        clean   = sum(1 for d in data if d['percent_scam'] < 21)
        suspect = sum(1 for d in data if 21 <= d['percent_scam'] <= 50)
        scam    = sum(1 for d in data if d['percent_scam'] > 50)
        avg     = round(sum(d['percent_scam'] for d in data) / total, 1)

        self.after(0, lambda: [
            self.lbl_total.config(text=f'Всього: {total}'),
            self.lbl_clean.config(text=f'✅ Справжніх: {clean}'),
            self.lbl_suspect.config(text=f'⚠️ Сумнівних: {suspect}'),
            self.lbl_scam.config(text=f'🚨 Шахрайських: {scam}'),
            self.lbl_avg.config(text=f'Середній ризик: {avg}%'),
        ])

    def _done(self):
        self.btn.config(state='normal')
        self.progress.stop()
        self._refresh_history()


if __name__ == '__main__':
    app = App()
    app.mainloop()