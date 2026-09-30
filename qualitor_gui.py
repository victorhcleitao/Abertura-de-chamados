# Source Generated with Decompyle++
# File: qualitor_gui.pyc (Python 3.12)

'''ServiceFlow GUI ÔÇö Interface gr├ífica moderna para abertura de chamados Qualitor Web.'''
import os
import sys
import re
import threading
import traceback
import math
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    from qualitor_automation import QualitorAutomation, SERVICE_TREE, CRES
    from departamentos_data import DEPARTAMENTOS_POR_CRE, CRE_VALUE_TO_PREFIX
    PRIMARY = '#1a3a6b'
    PRIMARY_LIGHT = '#2a5aab'
    ACCENT = '#e8a020'
    BG_LIGHT = '#f0f2f5'
    BG_WHITE = '#ffffff'
    TEXT_DARK = '#1a1a1a'
    TEXT_GRAY = '#666666'
    
    class QualitorGUI:
        
        def __init__(self):
            self.root = tk.Tk()
            self.root.title('ServiceFlow - Abertura de Chamados')
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            gw = min(int(sw * 0.88), 1300)
            gh = min(int(sh * 0.85), 1000)
            self.root.geometry(f'''{gw}x{gh}''')
            self.root.minsize(600, 500)
            self.root.resizable(True, True)
            icon_path = os.path.join(BASE_DIR, 'serviceflow.ico')
            if os.path.exists(icon_path):
                try:
                    self.root.iconbitmap(icon_path)
                except Exception:
                    pass
            self.running = False
            self.logged_in = False
            self._setup_style()
            self._build_login()


        
        def _setup_style(self):
            style = ttk.Style()
            
            try:
                style.theme_use('clam')
                style.configure('TFrame', background = BG_LIGHT)
                style.configure('TLabel', background = BG_LIGHT, foreground = TEXT_DARK, font = ('Segoe UI', 10))
                style.configure('TButton', font = ('Segoe UI', 10, 'bold'), background = PRIMARY, foreground = 'white')
                style.map('TButton', background = [
                    ('active', PRIMARY_LIGHT)])
                style.configure('Header.TLabel', font = ('Segoe UI', 16, 'bold'), foreground = PRIMARY, background = BG_LIGHT)
                style.configure('SubHeader.TLabel', font = ('Segoe UI', 11, 'bold'), foreground = PRIMARY, background = BG_LIGHT)
                style.configure('White.TFrame', background = BG_WHITE)
                style.configure('White.TLabel', background = BG_WHITE, foreground = TEXT_DARK, font = ('Segoe UI', 10))
                style.configure('Status.TLabel', font = ('Segoe UI', 10), foreground = TEXT_GRAY, background = BG_LIGHT)
                style.configure('Accent.TButton', font = ('Segoe UI', 11, 'bold'), background = ACCENT, foreground = 'white')
                style.map('Accent.TButton', background = [
                    ('active', '#d48f18')])
                style.configure('Treeview', font = ('Segoe UI', 10), rowheight = 26, background = BG_WHITE, fieldbackground = BG_WHITE)
                style.configure('Treeview.Heading', font = ('Segoe UI', 10, 'bold'), background = '#e8eaed', foreground = TEXT_DARK)
                style.map('Treeview', background = [
                    ('selected', PRIMARY)], foreground = [
                    ('selected', 'white')])
                style.configure('Horizontal.TProgressbar', troughcolor = '#e0e0e0', background = PRIMARY)
                style.configure('TLabelframe', background = BG_LIGHT)
                style.configure('TLabelframe.Label', font = ('Segoe UI', 10, 'bold'), foreground = PRIMARY, background = BG_LIGHT)
                return None
            except Exception:
                pass


        
        def _build_login(self):
            self.login_frame = tk.Frame(self.root, bg=BG_LIGHT)
            self.login_frame.pack(fill=tk.BOTH, expand=True)
            self.login_frame.grid_columnconfigure(0, weight=1)
            self.login_frame.grid_rowconfigure(0, weight=1)

            card = tk.Frame(self.login_frame, bg=BG_WHITE, bd=1, relief=tk.SOLID, padx=40, pady=35)
            card.grid(row=0, column=0)

            logo_canvas = tk.Canvas(card, width=80, height=80, bg=BG_WHITE, highlightthickness=0)
            logo_canvas.pack(pady=(0, 10))
            self._draw_logo(logo_canvas, 80)

            lbl_title = tk.Label(card, text="ServiceFlow", font=("Segoe UI", 20, "bold"), fg=PRIMARY, bg=BG_WHITE)
            lbl_title.pack()

            lbl_sub = tk.Label(card, text="Abertura de Chamados", font=("Segoe UI", 11), fg=TEXT_GRAY, bg=BG_WHITE)
            lbl_sub.pack(pady=(0, 20))

            fields = tk.Frame(card, bg=BG_WHITE)
            fields.pack(fill=tk.X, pady=5)

            lbl_u = tk.Label(fields, text="Email corporativo", font=("Segoe UI", 9, "bold"), fg=TEXT_DARK, bg=BG_WHITE)
            lbl_u.pack(anchor="w", pady=(5, 2))

            self.usuario_var = tk.StringVar(value=os.environ.get("QUALITOR_USER", ""))
            self.usuario_entry = tk.Entry(fields, textvariable=self.usuario_var, font=("Segoe UI", 11), width=32, bd=1, relief=tk.SOLID)
            self.usuario_entry.pack(fill=tk.X, ipady=4, pady=(0, 10))

            lbl_p = tk.Label(fields, text="Senha", font=("Segoe UI", 9, "bold"), fg=TEXT_DARK, bg=BG_WHITE)
            lbl_p.pack(anchor="w", pady=(5, 2))

            self.senha_var = tk.StringVar(value=os.environ.get("QUALITOR_PASS", ""))
            self.senha_entry = tk.Entry(fields, textvariable=self.senha_var, show="*", font=("Segoe UI", 11), width=32, bd=1, relief=tk.SOLID)
            self.senha_entry.pack(fill=tk.X, ipady=4, pady=(0, 20))

            self.login_btn = tk.Button(
                card,
                text="ENTRAR",
                font=("Segoe UI", 11, "bold"),
                bg=PRIMARY,
                fg="white",
                activebackground=PRIMARY_LIGHT,
                activeforeground="white",
                cursor="hand2",
                bd=0,
                padx=20,
                pady=8,
                command=self._on_login
            )
            self.login_btn.pack(fill=tk.X, pady=(0, 10))

            self.login_status = tk.Label(card, text="", font=("Segoe UI", 9), fg="#cc3333", bg=BG_WHITE)
            self.login_status.pack()

            self.root.bind("<Return>", lambda event: self._on_login())
            self.usuario_entry.focus_set()

        def _draw_logo(self, canvas, size):
            r = size / 2 - 4
            cx = size / 2
            cy = size / 2
            canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill = PRIMARY, outline = '')
            canvas.create_line(cx - 18, cy, cx + 18, cy, fill = 'white', width = 3)
            canvas.create_line(cx + 8, cy - 10, cx + 18, cy, fill = 'white', width = 3)
            canvas.create_line(cx + 8, cy + 10, cx + 18, cy, fill = 'white', width = 3)

        
        def _on_login(self):
            pass
        # WARNING: Decompyle incomplete

        
        def _login_ok(self):
            self.logged_in = True
            self.login_frame.destroy()
            self._build_main()

        
        def _login_fail(self, msg):
            self.login_btn.config(state = tk.NORMAL)
            self.login_status.config(text = f'''Falha no login: {msg}''', fg = '#cc3333')

        
        def _build_main(self):
            self.root.unbind('<Return>')
            outer = tk.Frame(self.root, bg = BG_LIGHT)
            outer.pack(fill = tk.BOTH, expand = True)
            header = tk.Frame(outer, bg = PRIMARY, height = 50)
            header.pack(fill = tk.X, side = tk.TOP)
            header.pack_propagate(False)
            tk.Label(header, text = 'ServiceFlow  ÔÇö  Abertura de Chamados', font = ('Segoe UI', 13, 'bold'), fg = 'white', bg = PRIMARY).pack(side = tk.LEFT, padx = 20)
            content = tk.Frame(outer, bg = BG_LIGHT, padx = 15, pady = 10)
            content.pack(fill = tk.BOTH, expand = True)
            content.grid_columnconfigure(0, weight = 1)
            content.grid_columnconfigure(1, weight = 1)
            content.grid_rowconfigure(0, weight = 1)
            left_col = tk.Frame(content, bg = BG_LIGHT)
            left_col.grid(row = 0, column = 0, sticky = 'nsew', padx = (0, 10))
            cfg = ttk.LabelFrame(left_col, text = 'Configura├º├Áes', padding = 10)
            cfg.pack(fill = tk.X, pady = (0, 10))
            cfg.grid_columnconfigure(1, weight = 1)
            ttk.Label(cfg, text = 'Quantidade:', style = 'Bold.TLabel').grid(row = 0, column = 0, sticky = 'w', pady = 4)
            self.qtd_var = tk.IntVar(value = 1)
            ttk.Spinbox(cfg, from_ = 1, to = 100, textvariable = self.qtd_var, width = 10).grid(row = 0, column = 1, sticky = 'w', pady = 4)
            ttk.Label(cfg, text = 'Tipo:', style = 'Bold.TLabel').grid(row = 1, column = 0, sticky = 'w', pady = 4)
            self.tipo_var = tk.StringVar(value = '2')
            tf = tk.Frame(cfg, bg = BG_LIGHT)
            tf.grid(row = 1, column = 1, sticky = 'w', pady = 4)
            ttk.Radiobutton(tf, text = 'Requisi├º├úo (REQ)', variable = self.tipo_var, value = '2').pack(side = tk.LEFT, padx = (0, 10))
            ttk.Radiobutton(tf, text = 'Incidente (INC)', variable = self.tipo_var, value = '1').pack(side = tk.LEFT)
            ttk.Label(cfg, text = 'Contato:', style = 'Bold.TLabel').grid(row = 2, column = 0, sticky = 'w', pady = 4)
            self.contato_var = tk.StringVar(value = '261')
            ttk.Entry(cfg, textvariable = self.contato_var, width = 15).grid(row = 2, column = 1, sticky = 'w', pady = 4)
            ttk.Label(cfg, text = 'Execu├º├úo:', style = 'Bold.TLabel').grid(row = 3, column = 0, sticky = 'w', pady = 4)
            pf = tk.Frame(cfg, bg = BG_LIGHT)
            pf.grid(row = 3, column = 1, sticky = 'w', pady = 4)
            self.parallel_var = tk.BooleanVar(value = True)
            ttk.Checkbutton(pf, text = 'Multi-rob├┤s (Paralelo)', variable = self.parallel_var, command = self._on_toggle_parallel).pack(side = tk.LEFT, padx = (0, 10))
            ttk.Label(pf, text = 'Rob├┤s:').pack(side = tk.LEFT, padx = (5, 2))
            self.workers_var = tk.IntVar(value = 10)
            self.workers_spin = ttk.Spinbox(pf, from_ = 1, to = 15, textvariable = self.workers_var, width = 4)
            self.workers_spin.pack(side = tk.LEFT)
            ttk.Label(cfg, text = 'Conclus├úo:', style = 'Bold.TLabel').grid(row = 4, column = 0, sticky = 'w', pady = 4)
            self.fechar_var = tk.BooleanVar(value = False)
            ttk.Checkbutton(cfg, text = 'Fechar chamados em s├®rie ap├│s abrir', variable = self.fechar_var).grid(row = 4, column = 1, sticky = 'w', pady = 4)
            ttk.Label(cfg, text = 'CRE:', style = 'Bold.TLabel').grid(row = 5, column = 0, sticky = 'w', pady = 4)
        # WARNING: Decompyle incomplete

        
        def _populate_service_tree(self):
            pass
        # WARNING: Decompyle incomplete

        
        def _populate_schools(self):
            cre_str = self.cre_var.get()
            if not cre_str:
                return None
            cre_val = cre_str.split(' - ')[0].strip()
            depts = DEPARTAMENTOS_POR_CRE.get(cre_val, [])
            if not depts:
                self._log(f'''Sem escolas cadastradas para CRE {cre_val}''')
                self.school_combo['values'] = []
                return None
        # WARNING: Decompyle incomplete

        
        def _on_cre_change(self, event = (None,)):
            self._populate_schools()

        
        def _get_school_value(self):
            sel = self.school_var.get()
            if sel or '(valor=' not in sel:
                return None
            return sel.split('(valor=')[-1].rstrip(')')

        
        def _get_service_path(self):
            selection = self.svc_tree.selection()
            if not selection:
                raise ValueError('Selecione um servi├ºo na ├írvore')
            item = selection[0]
            if self.svc_tree.get_children(item):
                raise ValueError('O item selecionado ├® uma categoria. Selecione uma op├º├úo folha (servi├ºo final) na ├írvore de servi├ºos.')
            vals = self.svc_tree.item(item, 'values')
            if not vals:
                raise ValueError('Caminho do servi├ºo inv├ílido.')
        # WARNING: Decompyle incomplete

        
        def _on_toggle_parallel(self):
            if self.parallel_var.get():
                self.workers_spin.config(state = 'normal')
                return None
            self.workers_spin.config(state = 'disabled')

        
        def _log(self, msg):
            self.log_text.config(state = tk.NORMAL)
            self.log_text.insert(tk.END, msg + '\n')
            self.log_text.see(tk.END)
            self.log_text.config(state = tk.DISABLED)
            self.root.update_idletasks()

        
        def _clear_log(self):
            self.log_text.config(state = tk.NORMAL)
            self.log_text.delete(1, tk.END)
            self.log_text.config(state = tk.DISABLED)

        
        def _set_progress(self, current, total):
            if total > 0:
                self.progress_bar['value'] = int((current / total) * 100)
            else:
                self.progress_bar['value'] = 0
            self.progress_label.config(text = f'''{current} / {total}''')
            self.root.update_idletasks()

        
        def _run_async(self):
            pass
        # WARNING: Decompyle incomplete

        
        def _on_success(self, fechar_chamado = (False,)):
            self.running = False
            self.run_btn.config(state = tk.NORMAL)
            self.close_btn.config(state = tk.NORMAL)
            self.status_var.set('Conclu├¡do!')
            msg = 'Todos os chamados foram abertos e encerrados com sucesso!' if fechar_chamado else 'Todos os chamados foram abertos com sucesso!'
            messagebox.showinfo('Conclu├¡do', msg)

        
        def _on_error(self, msg):
            self.running = False
            self.run_btn.config(state = tk.NORMAL)
            self.close_btn.config(state = tk.NORMAL)
            self.status_var.set('Erro!')
            self._log(f'''\n*** ERRO: {msg} ***''')

        
        def _open_close_dialog(self):
            """Open a modal dialog to close existing chamados in series."""
            if self.running:
                messagebox.showwarning("Aviso", "Já existe uma automação em execução.")
                return
            user = self.usuario_var.get().strip()
            pwd = self.senha_var.get().strip()
            if not user or not pwd:
                messagebox.showerror("Erro", "Credenciais de usuário e senha necessárias.")
                return

            dialog = tk.Toplevel(self.root)
            dialog.title("Fechar Chamados em Série")
            dialog.geometry("480x400")
            dialog.minsize(420, 320)
            dialog.transient(self.root)
            dialog.grab_set()

            content = tk.Frame(dialog, bg=BG_LIGHT, padx=20, pady=20)
            content.pack(fill=tk.BOTH, expand=True)

            lbl = tk.Label(
                content,
                text="Digite ou cole os números dos chamados que deseja encerrar\n(separados por vírgula, espaço ou linha):",
                bg=BG_LIGHT,
                fg=TEXT_DARK,
                font=("Segoe UI", 10),
                justify=tk.LEFT
            )
            lbl.pack(anchor="w", pady=(0, 10))

            text_area = scrolledtext.ScrolledText(content, height=7, font=("Consolas", 10))
            text_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            text_area.focus_set()

            opts_frame = tk.Frame(content, bg=BG_LIGHT)
            opts_frame.pack(fill=tk.X, pady=(0, 15))

            par_var = tk.BooleanVar(value=True)
            par_cb = ttk.Checkbutton(opts_frame, text="Multi-robôs (Paralelo)", variable=par_var)
            par_cb.pack(side=tk.LEFT)

            w_lbl = tk.Label(opts_frame, text="Robôs:", bg=BG_LIGHT, fg=TEXT_DARK, font=("Segoe UI", 9))
            w_lbl.pack(side=tk.LEFT, padx=(15, 5))

            w_var = tk.StringVar(value="4")
            w_spin = ttk.Spinbox(opts_frame, from_=1, to=10, textvariable=w_var, width=4)
            w_spin.pack(side=tk.LEFT)

            def do_close():
                raw_text = text_area.get("1.0", tk.END)
                ids = re.findall(r'\b\d{4,8}\b', raw_text)
                if not ids:
                    messagebox.showerror("Erro", "Nenhum número de chamado válido encontrado.", parent=dialog)
                    return
                seen = set()
                unique_ids = []
                for item in ids:
                    if item not in seen:
                        seen.add(item)
                        unique_ids.append(item)
                dialog.destroy()
                self._run_close_chamados_async(unique_ids, par_var.get(), int(w_var.get()))

            btn_box = tk.Frame(content, bg=BG_LIGHT)
            btn_box.pack(fill=tk.X)

            btn_run = tk.Button(
                btn_box,
                text="INICIAR ENCERRAMENTO",
                font=("Segoe UI", 10, "bold"),
                bg=PRIMARY,
                fg="white",
                activebackground=PRIMARY_LIGHT,
                activeforeground="white",
                cursor="hand2",
                bd=0,
                padx=15,
                pady=8,
                command=do_close
            )
            btn_run.pack(side=tk.LEFT)

            btn_cancel = tk.Button(
                btn_box,
                text="Cancelar",
                font=("Segoe UI", 10),
                bg="#e8e8e8",
                fg=TEXT_DARK,
                bd=0,
                padx=15,
                pady=8,
                command=dialog.destroy
            )
            btn_cancel.pack(side=tk.RIGHT)

        def _run_close_chamados_async(self, chamados_list, parallel, workers):
            usuario = self.usuario_var.get().strip()
            senha = self.senha_var.get().strip()
            count = len(chamados_list)
            self.running = True
            self.run_btn.config(state=tk.DISABLED)
            self.close_btn.config(state=tk.DISABLED)
            self.status_var.set("Encerrando...")
            self._clear_log()
            self._set_progress(0, count)

            preview = ", ".join(chamados_list[:5])
            if count > 5:
                preview += "..."
            self._log(f"Iniciando encerramento de {count} chamado(s): [{preview}]")

            def progress(msg):
                if msg.startswith("_PROGRESS:"):
                    parts = msg.strip().split(":")
                    if len(parts) == 3:
                        self.root.after(0, lambda: self._set_progress(int(parts[1]), int(parts[2])))
                        return
                self.root.after(0, lambda: self._log(msg.strip()))

            def target():
                try:
                    a = QualitorAutomation(usuario=usuario, senha=senha, headless=True, progress_callback=progress)
                    a.close_multiple_chamados(chamados_list=chamados_list, parallel=parallel, max_workers=workers)
                    a.close()
                    self.root.after(0, self._on_close_success)
                except Exception as e:
                    self.root.after(0, lambda: self._on_error(str(e)))
                    self.root.after(0, lambda: self._log(traceback.format_exc()))

            threading.Thread(target=target, daemon=True).start()

        def _on_close_success(self):
            self.running = False
            self.run_btn.config(state = tk.NORMAL)
            self.close_btn.config(state = tk.NORMAL)
            self.status_var.set('Conclu├¡do!')
            messagebox.showinfo('Conclu├¡do', 'Todos os chamados foram encerrados com sucesso!')

        
        def run(self):
            self.root.mainloop()


    if __name__ == '__main__':
        app = QualitorGUI()
        app.run()
except ImportError as e:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror('Erro de dependencia', f'Falha ao importar modulo: {e}\n\nExecute SERVICEFLOW.bat para instalar as dependencias.')
    sys.exit(1)

