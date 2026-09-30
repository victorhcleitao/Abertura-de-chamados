# Source Generated with Decompyle++
# File: qualitor_automation.pyc (Python 3.12)

'''Qualitor Web Automation ÔÇö Core module
Headless Selenium automation for opening chamados on qualitor web
'''
import os
import sys
import time
import json
import threading
import traceback
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
from selenium import webdriver
import selenium.webdriver.edge.webdriver as selenium
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException
from webdriver_manager.microsoft import EdgeChromiumDriverManager
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = BASE_DIR
URL_BASE = 'https://helpdesk-sme.netcenter.com.br'
URL_LOGIN = f'''{URL_BASE}/login.php'''
from service_tree import SERVICE_TREE
from cres_list import CRES

class QualitorAutomation:
    
    def __init__(self, usuario, senha, headless, output_dir, progress_callback, user_data_dir, driver_path, worker_name = (None, None, True, 'services_dump_v9', None, None, None, '')):
        if not usuario:
            usuario
        self.usuario = os.environ.get('QUALITOR_USER', '')
        if not senha:
            senha
        self.senha = os.environ.get('QUALITOR_PASS', '')
        if not self.usuario or self.senha:
            raise ValueError('Credenciais nao fornecidas. Defina QUALITOR_USER e QUALITOR_PASS ou passe usuario/senha.')
        self.headless = headless
        self.output_dir = os.path.join(DATA_DIR, output_dir)
        self.progress = progress_callback
        self.user_data_dir = user_data_dir
        self.driver_path = driver_path
        self.worker_name = worker_name
        self.driver = None
        self.main_handle = None
        self.form_handle = None
        self._log_file = None
        self._setup_log_file()
        self._log('QualitorAutomation inicializado')

    
    def _setup_log_file(self):
        try:
            log_dir = os.path.join(DATA_DIR, 'logs')
            os.makedirs(log_dir, exist_ok=True)
            ts = time.strftime('%Y%m%d_%H%M%S')
            log_path = os.path.join(log_dir, f'serviceflow_{ts}.log')
            self._log_file = open(log_path, 'w', encoding='utf-8')
        except Exception:
            pass

    def _log(self, msg):
        ts = time.strftime('%H:%M:%S')
        prefix = f'{self.worker_name} ' if self.worker_name else ''
        full = f'[{ts}] {prefix}{msg}\n'
        if self._log_file:
            try:
                self._log_file.write(full)
                self._log_file.flush()
            except Exception:
                pass
        if self.progress:
            try:
                self.progress(full)
            except Exception:
                pass
        print(full, end='')

    def _wait_for_condition(self, fn, timeout=30, interval=0.5, desc=''):
        for _ in range(int(timeout / interval)):
            try:
                res = fn()
                if res:
                    return res
            except Exception:
                pass
            time.sleep(interval)
        return None

    def start_browser(self):
        opts = EdgeOptions()
        if self.headless:
            opts.add_argument('--headless=new')
        opts.add_argument('--window-size=1920,1080')
        opts.add_argument('--disable-blink-features=AutomationControlled')
        opts.add_argument('--no-first-run')
        opts.add_argument('--no-default-browser-check')
        opts.add_argument('--disable-gpu')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('--disable-popup-blocking')
        opts.add_argument('--disable-notifications')
        opts.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        if self.user_data_dir:
            opts.add_argument(f'--user-data-dir={self.user_data_dir}')
        prefs = {
            'profile.default_content_settings.popups': 1,
            'download.default_directory': self.output_dir
        }
        opts.add_experimental_option('prefs', prefs)

        if self.driver_path:
            svc = EdgeService(self.driver_path)
            self.driver = webdriver.Edge(service=svc, options=opts)
        else:
            try:
                svc = EdgeService(EdgeChromiumDriverManager().install())
                self.driver = webdriver.Edge(service=svc, options=opts)
            except Exception:
                self.driver = webdriver.Edge(options=opts)

        self.driver.set_script_timeout(30)
        self.main_handle = self.driver.current_window_handle
        self._log('Navegador iniciado' + (' (headless)' if self.headless else ''))

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
            self._log('Navegador fechado')
        if self._log_file:
            try:
                self._log_file.close()
            except Exception:
                pass
            self._log_file = None

    def login(self):
        self._log('Login...')
        self.driver.get(URL_LOGIN)
        self._wait_for_condition(
            lambda: len(self.driver.find_elements(By.ID, 'cdusuario')) > 0,
            timeout=15,
            desc='pagina login'
        )

        user_el = self.driver.find_element(By.ID, 'cdusuario')
        user_el.click()
        user_el.send_keys(self.usuario)
        ActionChains(self.driver).send_keys(Keys.TAB).perform()

        self._wait_for_condition(
            lambda: self.driver.find_element(By.ID, 'cdsenha').get_attribute('disabled') is None,
            timeout=10,
            desc='campo senha'
        )

        try:
            sel = Select(self.driver.find_element(By.ID, 'cdconexao'))
            for opt in sel.options:
                if 'SME' in opt.text.upper():
                    sel.select_by_visible_text(opt.text.strip())
                    self._log(f'Conexao: {opt.text.strip()}')
                    break
        except Exception:
            pass

        pwd_el = self.driver.find_element(By.ID, 'cdsenha')
        pwd_el.click()
        pwd_el.send_keys(self.senha)

        self.driver.find_element(By.ID, 'btnLogin').click()

        login_ok = self._wait_for_condition(
            lambda: 'login' not in self.driver.current_url.lower(),
            timeout=20,
            desc='redirect pos-login'
        )
        if not login_ok:
            raise RuntimeError('Login falhou!')

        self.main_handle = self.driver.current_window_handle
        self._log('Login OK')

    def menu_navigate(self):
        self._log('Navegando menu do portal...')
        self.driver.switch_to.default_content()
        try:
            parent_menu = self.driver.find_element(By.ID, 'mnuHd_Solicitacao')
            ActionChains(self.driver).move_to_element(parent_menu).perform()
            time.sleep(0.5)
            nova_req = self.driver.find_element(By.XPATH, "//a[contains(text(),'Nova requisição de serviço')]")
            nova_req.click()
        except Exception:
            js = """
                var links = document.querySelectorAll('a.menu-label');
                for (var i = 0; i < links.length; i++) {
                    if (links[i].textContent.trim() === 'Nova requisição de serviço') {
                        links[i].click();
                        return;
                    }
                }
                var li = document.querySelector('li[nrmenu="730"]');
                if (li) li.click();
            """
            self.driver.execute_script(js)

        time.sleep(2.0)
        iframe = self.driver.find_element(By.ID, 'framePrincipal')
        self.driver.switch_to.frame(iframe)
        self._log('Menu navegado com sucesso')
        return True

    def set_contact_and_load_services(self, contact_id = ('261',)):
        self._log(f'''Configurando contato {contact_id}...''')
        contato_ok = False
        for attempt in range(5):
            self.driver.execute_script(f'''\n                var c = document.getElementById(\'cdcontato\');\n                if (c) {{\n                    c.value = \'{contact_id}\';\n                    c.dispatchEvent(new Event(\'blur\'));\n                    if (typeof objcdcontato !== \'undefined\' && objcdcontato.searchMultiValues)\n                        objcdcontato.searchMultiValues();\n                }}\n            ''')
            time.sleep(1)
            val = self.driver.execute_script("return document.getElementById('cdcontato') ? document.getElementById('cdcontato').value : null;")
            if not str(val) == str(contact_id):
                continue
            contato_ok = True
            range(5)
        if not contato_ok:
            self._log('AVISO: nao foi possivel definir contato, tentando mesmo assim...')
        self.driver.execute_script("if (typeof processPesquisa === 'function') processPesquisa();")
        svc_count = 0
        for _ in range(30):
            time.sleep(1)
            svc_count = self.driver.execute_script('\n                var div = document.getElementById(\'divServicos\');\n                if (!div) return -1;\n                return div.querySelectorAll(\'[id^="btnActionService"]\').length;\n            ')
            if not svc_count:
                continue
            if not svc_count > 0:
                continue
            self._log(f'''{svc_count} servicos carregados''')
            
            return range(30), svc_count
        raise RuntimeError('Nenhum servico carregado apos contato')

    
    def click_service_by_id(self, service_cd):
        '''Click a service button by its cd (e.g. 5 = Manutencao de Ambiente).'''
        self.driver.execute_script(f'''\n            var btn = document.getElementById(\'btnActionService{service_cd}\');\n            if (btn) {{\n                eval(btn.getAttribute(\'onclick\'));\n            }}\n        ''')
        time.sleep(1.5)

    
    def click_service_path(self, service_path):
        '''Navigate service tree by path, clicking parent nodes to expand to leaf.'''
        pass
    # WARNING: Decompyle incomplete

    
    def open_form_for_leaf(self, leaf_cd):
        '''Click leaf service and switch to the viewQForm popup window.'''
        pass
    # WARNING: Decompyle incomplete

    
    def fill_form(self, tipo, cre_value, school_value, titulo, descricao):
        '''Fill viewQForm fields with full AJAX request synchronization.'''
        pass
    # WARNING: Decompyle incomplete

    
    def _detect_dialog(self):
        '''Detect confirmation dialog.'''
        return self.driver.execute_script('\n            var qalert = document.querySelector(\'#divAlert\');\n            if (qalert && qalert.style.display !== \'none\' && qalert.offsetParent !== null && qalert.innerText.trim().length > 0) {\n                return qalert.innerText.trim();\n            }\n            var all = document.querySelectorAll(\'.modal.show, .modal:not([style*="display: none"]), [class*="alert"]\');\n            for (var i = 0; i < all.length; i++) {\n                if (all[i].innerText.trim().length > 0) return all[i].innerText.trim();\n            }\n            return null;\n        ')

    
    def _click_dialog_confirm(self):
        '''Click Sim or OK on confirmation dialog.'''
        return self.driver.execute_script('\n            var btn = document.getElementById(\'btnYES\');\n            if (btn && btn.offsetParent !== null) {\n                btn.disabled = false;\n                btn.removeAttribute(\'disabled\');\n                eval(btn.getAttribute(\'onclick\'));\n                return true;\n            }\n            var dialog = document.querySelector(\'#divAlert, .modal.show, .modal:not([style*="display: none"]), [id*="Alert"], [id*="Dialog"]\');\n            if (dialog && dialog.offsetParent !== null) {\n                var btns = dialog.querySelectorAll(\'button, a, input[type="button"], input[type="submit"]\');\n                for (var i = 0; i < btns.length; i++) {\n                    var t = (btns[i].innerText || btns[i].value || \'\').trim().toLowerCase();\n                    if (t === \'sim\' || t === \'ok\' || t === \'confirmar\') {\n                        btns[i].disabled = false;\n                        btns[i].removeAttribute(\'disabled\');\n                        btns[i].click();\n                        return true;\n                    }\n                }\n            }\n            var all = document.querySelectorAll(\'button, a, input[type="button"], input[type="submit"]\');\n            for (var i = 0; i < all.length; i++) {\n                var t = (all[i].innerText || all[i].value || \'\').trim().toLowerCase();\n                if ((t === \'sim\' || t === \'confirmar\') && all[i].offsetParent !== null) {\n                    all[i].disabled = false;\n                    all[i].removeAttribute(\'disabled\');\n                    all[i].click();\n                    return true;\n                }\n            }\n            return false;\n        ')

    
    def _find_chamado_window(self):
        '''Find the cadastro_chamado window.'''
        for _ in range(30):
            time.sleep(0.5)
            for h in self.driver.window_handles:
                if not h != self.main_handle:
                    continue
                if not h != self.form_handle:
                    continue
                self.driver.switch_to.window(h)
                if 'cadastro_chamado' in self.driver.current_url:
                    
                    
                    return range(30), self.driver.window_handles, h
        pass

    
    def submit_and_confirm(self, fechar_chamado, service_name = (False, '')):
        '''Submit form, handle confirmation dialog, switch to chamado window, click Iniciar, optionally close.'''
        pass
    # WARNING: Decompyle incomplete

    
    def close_chamado_in_window(self, service_name = ('',)):
        '''Close/conclude currently open chamado in cadastro_chamado.php.'''
        pass
    # WARNING: Decompyle incomplete

    
    def close_existing_chamado(self, cdchamado, service_name = ('',)):
        '''Navigate to an existing chamado by ID, start attendance if needed, and close it.'''
        pass
    # WARNING: Decompyle incomplete

    
    def _reload_root_services(self, contact_id):
        '''Clean reload of framePrincipal to reset gateway flags and return to root service tree.'''
        self.driver.switch_to.default_content()
        self.driver.execute_script("\n            var f = document.getElementById('framePrincipal');\n            if (f) {\n                f.contentWindow.hasGatewayServicoBefore = false;\n                f.contentWindow.hasGatewayServicoAfter = false;\n                f.contentWindow.location.reload();\n            }\n        ")
        time.sleep(2.5)
        iframe = self.driver.find_element(By.ID, 'framePrincipal')
        self.driver.switch_to.frame(iframe)
        self.set_contact_and_load_services(contact_id)

    
    def create_chamado(self, service_path, school_value, titulo, descricao, tipo, cre_value, contact_id, fechar_chamado, service_name = ('2', '6', '261', False, '')):
        '''Full flow to create one chamado.'''
        leaf_cd = service_path[-1]
        self.set_contact_and_load_services(contact_id)
        self.click_service_path(service_path)
        self.open_form_for_leaf(leaf_cd)
        self.fill_form(tipo, cre_value, school_value, titulo, descricao)
        self.submit_and_confirm(fechar_chamado = fechar_chamado, service_name = service_name)
        self.driver.switch_to.window(self.main_handle)
        self.driver.switch_to.default_content()
        
        try:
            iframe = self.driver.find_element(By.ID, 'framePrincipal')
            self.driver.switch_to.frame(iframe)
        except Exception:
            pass


    
    def create_multiple(self, count, service_path, school_value, titulo, descricao, tipo, cre_value, contact_id, parallel, max_workers, fechar_chamado, service_name = ('2', '6', '261', False, 2, False, '')):
        '''Create multiple chamados ÔÇö sequential (default) or parallel.'''
        if parallel and count > 1:
            return self._create_multiple_parallel(count, service_path, school_value, titulo, descricao, tipo, cre_value, contact_id, max_workers, fechar_chamado = fechar_chamado, service_name = service_name)
        return self._create_multiple_sequential(count, service_path, school_value, titulo, descricao, tipo, cre_value, contact_id, fechar_chamado = fechar_chamado, service_name = service_name)

    
    def _create_multiple_sequential(self, count, service_path, school_value, titulo, descricao, tipo, cre_value, contact_id, fechar_chamado=False, service_name=''):
        """Create multiple chamados sequentially in one browser session."""
        self.start_browser()
        self.login()
        self.menu_navigate()
        self.set_contact_and_load_services(contact_id)

        completed = []
        failed = []
        leaf_cd = service_path[-1]

        for i in range(1, count + 1):
            item_titulo = f"{titulo} ({i}/{count})" if count > 1 else titulo
            self._log(f"\n--- Chamado {i}/{count} ---")
            try:
                if i > 1:
                    try:
                        self._reload_root_services(contact_id)
                    except Exception as e:
                        self._log(f"AVISO: reload servicos falhou: {e}, tentando re-navegar...")
                        try:
                            self.menu_navigate()
                            self.set_contact_and_load_services(contact_id)
                        except Exception as e2:
                            self._log(f"Falha na recuperacao do menu: {e2}")

                self.click_service_path(service_path)
                self.open_form_for_leaf(leaf_cd)
                self.fill_form(tipo, cre_value, school_value, item_titulo, descricao)
                self.submit_and_confirm(fechar_chamado=fechar_chamado, service_name=service_name)
                completed.append(i)
                if self.progress:
                    self.progress(f"_PROGRESS:{len(completed)}:{count}")
            except Exception as e:
                self._log(f"Chamado {i} FALHOU: {e}")
                failed.append(i)
                if self.driver:
                    for h in list(self.driver.window_handles):
                        if h != self.main_handle:
                            try:
                                self.driver.switch_to.window(h)
                                self.driver.close()
                            except Exception:
                                pass
                    try:
                        self.driver.switch_to.window(self.main_handle)
                    except Exception:
                        pass

        success = len(completed)
        action_res = "criado(s) e encerrado(s)" if fechar_chamado else "criado(s)"
        self._log(f"\n*** TOTAL: {success}/{count} chamado(s) {action_res} com sucesso! ***")
        if failed:
            self._log(f"Chamados que falharam: {failed}")
            raise RuntimeError(f"{len(failed)} chamado(s) falharam: {failed}")
        return success

    def _create_multiple_parallel(self, count, service_path, school_value, titulo, descricao, tipo, cre_value, contact_id, max_workers=2, fechar_chamado=False, service_name=''):
        """Create multiple chamados in parallel using worker threads."""
        n_workers = min(count, max_workers)
        action_desc = "abertura e encerramento" if fechar_chamado else "abertura"
        self._log(f"Iniciando {action_desc} de {count} chamado(s) com {n_workers} robô(s) simultâneo(s)...")

        driver_path = None
        try:
            driver_path = EdgeChromiumDriverManager().install()
        except Exception as e:
            self._log(f"Aviso ao instalar driver: {e}")

        work_queue = queue.Queue()
        for i in range(1, count + 1):
            work_queue.put(i)

        completed = []
        failed = []
        lock = threading.Lock()

        def worker_task(wid):
            worker_profile = tempfile.mkdtemp(prefix=f"sf_worker_{wid}_")
            wname = f"[Robô {wid}]"
            worker = QualitorAutomation(
                usuario=self.usuario,
                senha=self.senha,
                headless=self.headless,
                output_dir=self.output_dir,
                progress_callback=self.progress,
                user_data_dir=worker_profile,
                driver_path=driver_path,
                worker_name=wname
            )
            try:
                worker._log("Iniciando navegador e realizando login...")
                worker.start_browser()
                worker.login()
                worker.menu_navigate()
                worker.set_contact_and_load_services(contact_id)
                worker._log("Pronto para processar chamados.")
                first_chamado = True

                while True:
                    try:
                        i = work_queue.get_nowait()
                    except queue.Empty:
                        break

                    try:
                        if not first_chamado:
                            try:
                                worker._reload_root_services(contact_id)
                            except Exception as e:
                                worker._log(f"Aviso reload: {e}, tentando re-navegar...")
                                worker.menu_navigate()
                                worker.set_contact_and_load_services(contact_id)

                        item_titulo = f"{titulo} ({i}/{count})" if count > 1 else titulo
                        worker._log(f"Iniciando Chamado {i}/{count}...")
                        leaf_cd = service_path[-1]
                        worker.click_service_path(service_path)
                        worker.open_form_for_leaf(leaf_cd)
                        worker.fill_form(tipo, cre_value, school_value, item_titulo, descricao)
                        worker.submit_and_confirm(fechar_chamado=fechar_chamado, service_name=service_name)

                        with lock:
                            completed.append(i)
                            if self.progress:
                                self.progress(f"_PROGRESS:{len(completed)}:{count}")
                        action_res = "aberto e encerrado com sucesso!" if fechar_chamado else "aberto e atribuído com sucesso!"
                        worker._log(f"Chamado {i}/{count} {action_res}")

                    except Exception as e:
                        worker._log(f"Chamado {i}/{count} FALHOU: {e}")
                        with lock:
                            failed.append(i)
                        if worker.driver:
                            for h in list(worker.driver.window_handles):
                                if h != worker.main_handle:
                                    try:
                                        worker.driver.switch_to.window(h)
                                        worker.driver.close()
                                    except Exception:
                                        pass
                            try:
                                worker.driver.switch_to.window(worker.main_handle)
                            except Exception:
                                pass
                    finally:
                        first_chamado = False
            except Exception as e:
                worker._log(f"Exceção no robô: {e}")
            finally:
                try:
                    worker.close()
                except Exception:
                    pass
                try:
                    shutil.rmtree(worker_profile, ignore_errors=True)
                except Exception:
                    pass

        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            futures = [executor.submit(worker_task, wid) for wid in range(1, n_workers + 1)]
            for f in as_completed(futures):
                try:
                    f.result()
                except Exception as e:
                    self._log(f"Exceção no robô: {e}")

        success = len(completed)
        action_res = "criado(s) e encerrado(s)" if fechar_chamado else "criado(s)"
        self._log(f"\n*** TOTAL: {success}/{count} chamado(s) {action_res} com sucesso! ***")
        if failed:
            self._log(f"Chamados que falharam: {failed}")
            raise RuntimeError(f"{len(failed)} chamado(s) falharam: {failed}")
        return success

    def close_multiple_chamados(self, chamados_list, parallel=False, max_workers=2):
        """Close multiple existing chamados sequentially or in parallel."""
        count = len(chamados_list)
        if count == 0:
            return 0
        if parallel and count > 1:
            return self._close_multiple_parallel(chamados_list, max_workers)
        return self._close_multiple_sequential(chamados_list)

    def _close_multiple_sequential(self, chamados_list):
        count = len(chamados_list)
        self._log(f"Iniciando encerramento sequencial de {count} chamado(s)...")
        self.start_browser()
        self.login()
        completed = []
        failed = []
        for i, cd in enumerate(chamados_list, 1):
            self._log(f"\n--- Encerrando chamado {cd} ({i}/{count}) ---")
            try:
                self.close_existing_chamado(cd)
                completed.append(cd)
                if self.progress:
                    self.progress(f"_PROGRESS:{len(completed)}:{count}")
            except Exception as e:
                self._log(f"Falha ao encerrar chamado {cd}: {e}")
                failed.append(cd)

        self._log(f"\n*** TOTAL: {len(completed)}/{count} chamado(s) encerrado(s) com sucesso! ***")
        if failed:
            self._log(f"Chamados que falharam: {failed}")
            raise RuntimeError(f"{len(failed)} chamado(s) falharam ao encerrar: {failed}")
        return len(completed)

    def _close_multiple_parallel(self, chamados_list, max_workers=2):
        count = len(chamados_list)
        n_workers = min(count, max_workers)
        self._log(f"Iniciando encerramento de {count} chamado(s) com {n_workers} robô(s)...")

        driver_path = None
        try:
            driver_path = EdgeChromiumDriverManager().install()
        except Exception as e:
            self._log(f"Aviso ao instalar driver: {e}")

        work_queue = queue.Queue()
        for cd in chamados_list:
            work_queue.put(cd)

        completed = []
        failed = []
        lock = threading.Lock()

        def worker_task(wid):
            worker_profile = tempfile.mkdtemp(prefix=f"sf_close_worker_{wid}_")
            wname = f"[Robô {wid}]"
            worker = QualitorAutomation(
                usuario=self.usuario,
                senha=self.senha,
                headless=self.headless,
                output_dir=self.output_dir,
                progress_callback=self.progress,
                user_data_dir=worker_profile,
                driver_path=driver_path,
                worker_name=wname
            )
            try:
                worker.start_browser()
                worker.login()
                while True:
                    try:
                        cd = work_queue.get_nowait()
                    except queue.Empty:
                        break

                    try:
                        worker._log(f"Encerrando chamado {cd}...")
                        worker.close_existing_chamado(cd)
                        with lock:
                            completed.append(cd)
                            if self.progress:
                                self.progress(f"_PROGRESS:{len(completed)}:{count}")
                    except Exception as e:
                        worker._log(f"Falha ao encerrar chamado {cd}: {e}")
                        with lock:
                            failed.append(cd)
            except Exception as e:
                worker._log(f"Exceção no robô de encerramento: {e}")
            finally:
                try:
                    worker.close()
                except Exception:
                    pass
                try:
                    shutil.rmtree(worker_profile, ignore_errors=True)
                except Exception:
                    pass

        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            futures = [executor.submit(worker_task, wid) for wid in range(1, n_workers + 1)]
            for f in as_completed(futures):
                try:
                    f.result()
                except Exception as e:
                    self._log(f"Exceção no robô de encerramento: {e}")

        success = len(completed)
        self._log(f"\n*** TOTAL: {success}/{count} chamado(s) encerrado(s) com sucesso! ***")
        if failed:
            self._log(f"Chamados que falharam ao encerrar: {failed}")
            raise RuntimeError(f"{len(failed)} chamado(s) falharam ao encerrar: {failed}")
        return success
