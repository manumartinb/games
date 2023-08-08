import json
import random
import re
import time
from datetime import datetime
from threading import Timer
try:
    from bs4 import BeautifulSoup
except ImportError:
    from pip._internal import main as pip
    pip(['install','--upgrade','--user','pip'])
    pip(['install','--user', 'bs4'])
    from bs4 import BeautifulSoup
try:
    import pandas as pd
except ImportError:
    from pip._internal import main as pip
    pip(['install','--upgrade','--user','pip'])
    pip(['install','--user', 'pandas'])
    import pandas as pd
try:
    import tkinter as tk
    from tkinter.filedialog import askopenfilename
except ImportError:
    from pip._internal import main as pip
    pip(['install','--upgrade','--user','pip'])
    pip(['install','--user', 'tkinter'])
    import tkinter as tk
    from tkinter.filedialog import askopenfilename
try:
    from selenium import webdriver
    from selenium.common import exceptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.common.keys import Keys
except ImportError:
    from pip._internal import main as pip
    pip(['install','--upgrade','--user','pip'])
    pip(['install','--user', 'selenium'])
    from selenium import webdriver
    from selenium.common import exceptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.common.keys import Keys
try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.utils import ChromeType
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
except ImportError:
    from pip._internal import main as pip
    pip(['install','--upgrade','--user','pip'])
    pip(['install','--user', 'webdriver_manager'])
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.utils import ChromeType
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
try:
    import gspread
    #from gspread.models import Cell, Spreadsheet
except ImportError:
    from pip._internal import main as pip
    pip(['install','--upgrade','--user','pip'])
    pip(['install','--user', 'gspread'])
    import gspread
    #from gspread.models import Cell, Spreadsheet
try:
    from oauth2client.service_account import ServiceAccountCredentials
except ImportError:
    from pip._internal import main as pip
    pip(['install','--upgrade','--user','pip'])
    pip(['install','--user', 'oauth2client'])
    from oauth2client.service_account import ServiceAccountCredentials
import pprint

browser: webdriver.Chrome = None


current_meeting = None
already_joined_ids = []
active_correlation_id = ""
hangup_thread: Timer = None

uuid_regex = r"\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b"
global config, lista_empresas

import os
# Intentamos buscar el archivo config.json en la ruta del archivo .py que estamos ejecutando
path_json = os.path.dirname(__file__) + '/config.json'
try:
    with open(path_json,"r") as json_data_file:
        config = json.load(json_data_file)
        print(f"Archivo config.json encontrado en la ruta: {path_json}")
except FileNotFoundError:
    print(f"No se ha encontrado el fichero config.json en la ruta: {path_json}")
    print("Por favor ponga el archivo config.json en la ruta donde se está buscando.")
    exit(-1)

path_empresas = os.path.dirname(__file__) + '/empresas.txt'
try:
    with open(path_empresas,"r") as fichero_empresas:
        print(f"Archivo empresas.txt encontrado en la ruta: {path_empresas}")
        lista_empresas = [empresa.rstrip() for empresa in fichero_empresas if empresa != ""]
        print(lista_empresas)
except FileNotFoundError:
    print(f"No se ha encontrado el fichero empresas.txt en la ruta: {path_empresas}")
    print("Por favor ponga el archivo empresas.txt en la ruta donde se está buscando.")
    exit(-1)

def cambiar_fecha(fecha):
    primera_fecha = "30/12/1899"
    b = datetime.strptime(primera_fecha, "%d/%m/%Y")
    a = datetime.strptime(fecha, "%d/%m/%y")
    #print(fecha)
    #print(a)
    #print(b)
    num_days = (a - b).days
    #print(num_days)
    return num_days

def replace_commas(str1): 
    str2 = str1
    for character in str1:
        if character.isalpha():
            return str1
    if '%' in str1:
        str2 = str2.replace(',','.')
        str2 = str2.replace('(','-')
        str2 = str2.replace(')','')
        return str2
    else:
        if ',' in str1:
            str2 = str2.replace('.','')
            str2 = str2.replace(',','.')
            str2 = str2.replace('(','-')
            str2 = str2.replace(')','')
            try:
                str2 = float(str2)
            except ValueError:
                print("Error al pasar a float ("+str1+") el siguiente valor:" + str2)
                exit(-1)
            return str2
        else:
            return str1
    
def copy_spreadsheet(sheet_origin_name, sheet_copy_name):
    #Authorize the API
    scope = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/spreadsheets'
        ]
    
    #file_name = 'C:/Users/Usuario/Documents/Python/Python Sheets-b5d77b15d520.json'
    #file_name = config['path_credentials']
    file_name = os.path.dirname(__file__) + '/pollas.json'
    try:
        f = open(file_name,"r")
        f.close()
    except FileNotFoundError:
        print("Archivo "+file_name+" no accesible, por favor pon el archivo de credenciales pollas.json junto con el .py")
        exit(1)

    print("Generamos credenciales")
    creds = ServiceAccountCredentials.from_json_keyfile_name(file_name,scope)
    print("Creamos el cliente")
    client = gspread.authorize(creds)
    #spreadsheet = client.open('Plantilla_Manu')
    print("Abrimos el fichero de origen")
    spreadsheet = client.open(sheet_origin_name)
    #new_spreadsheet = client.copy(spreadsheet.id,'Plantilla_Manu_v2')
    print("Copiamos el fichero de origen")
    return client.copy(spreadsheet.id, sheet_copy_name, copy_permissions=True)

def automatic_extraction():
    init_browser() # Abrimos el navegador
    # USUARIO Y CONTRASEÑA PARA LOGUEARSE A LA WEB
    #config['email'] = No es necesario si está en el archivo config.json
    #config['password'] = No es necesario si está en el archivo config.json
    # CARGAMOS EN EL NAVEGADOR LA DIRECCION DE LA WEB DONDE VAMOS A LOGUEARNOS
    browser.get("https://app.tikr.com/login")
    

    if config['email'] != "" and config['password'] != "":
        # METEMOS EL USUARIO
        login_email = wait_until_found_xpath("//main/div/div/div/div/div/div/div/div/div/div/div/div/input[starts-with(@id,'input') and @type='email']", 30)
        if login_email is not None:
            login_email.send_keys(config['email'])
        else:
            print("No se ha podido ingresar el usuario")
            exit(1)
        # find the element again to avoid StaleElementReferenceException
        #login_email = wait_until_found("input[type='email']", 5)
        #if login_email is not None:
        #login_email.send_keys(Keys.ENTER)
        # METEMOS EL PASSWORD
        login_pwd = wait_until_found_xpath("//main/div/div/div/div/div/div/div/div/div/div/div/div/input[starts-with(@id,'input') and @type='password']", 30)
        if login_pwd is not None:
            login_pwd.send_keys(config['password'])
        else:
            print("No se ha podido ingresar el password")
            exit(1)
        # find the element again to avoid StaleElementReferenceException
        #login_pwd = wait_until_found("input[type='password']", 5)
        #if login_pwd is not None:
        #    login_pwd.send_keys(Keys.ENTER)
        #'//tr[@class="title"]/td'
        # PULSAMOS EN EL BOTON DE LOGUEARSE
        login_btn = wait_until_found_xpath("//main/div/div/div/div/div/div/div/button[contains(@class, 'primaryAction') and @type='button']", 20)
        if login_btn is not None:
            login_btn.click()
        else:
            print("No se ha podido pulsar el botón ingresar")
            print("Login Unsuccessful, recheck entries in config.json")
            exit(1)
        #use_web_instead = wait_until_found(".use-app-lnk", 5, print_error=False)
        #if use_web_instead is not None:
        #    use_web_instead.click()
        print("Login Successful!")
        ## NUEVA TASK +--> VAMOS A LOS PUTOS AJUSTES A CAMBIAR EL PUTO IDIOMA PUTO COÑAZO PUTO MANU
        # Buscamos y pulsamos en el icono de ajustes
        icon_settings = wait_until_found_xpath("//header/div/button/span/i[@class='v-icon notranslate material-icons theme--light']", 30)
        if icon_settings is not None:
            icon_settings.click()
        else:
            print("No se ha podido pulsar en el icono de ajustes")
            print("No se encuentra el icono de los ajustes dentro de la pagina https://app.tikr.com/markets, revisa el codigo de la web para encontrar el icono de ajustes")
            exit(1)
        # Pulsamos en el menu de ajustes
        div_settings = wait_until_found_xpath("//body/div/div/div/div/div/a/div/div[@class='v-list-item__title' and contains(string(), 'Configuraciones de la cuenta')]", 30)
        if div_settings is not None:
            div_settings.click()
        else:
            print("No se ha podido pulsar en el menu de ajustes")
            print("No se encuentra el menu de los ajustes despues de pulsar el icono de ajustes en la pagina https://app.tikr.com/markets, revisa el codigo de la web para encontrar el menu de ajustes")
            exit(1)
        # Pulsamos en el menu ajustes del lenguaje
        div_settings_lang = wait_until_found_xpath("//main/div/div/div/div/div/div/div/div/div/div/div/div[@class='v-select__slot']/label[@class='v-label theme--light' and contains(string(), 'ES')]/..", 30)
        if div_settings_lang is not None:
            div_settings_lang.click()
        else:
            print("No se ha podido pulsar en los ajustes de idioma")
            print("Revisa donde se encuentra el div de ajustes en la página web https://app.tikr.com/account/")
            exit(1)
        # Buscamos el idioma ingles en la lista para pulsarlo
        lang_en = wait_until_found_xpath("//body/div/div/div/div/div/div/div/div[@class='v-list-item__title' and contains(string(), 'en')]", 30)
        if lang_en is not None:
            lang_en.click()
        else:
            print("No se ha podido pulsar en el idioma deseado")
            print("Revisa donde se encuentra el idioma 'en' dentro de los ajustes de idioma la página web https://app.tikr.com/account/")
            exit(1)
        
        datos = {}
        for nombre_empresa in lista_empresas:
            datos[nombre_empresa] = []
        for nombre_empresa in lista_empresas:
            div_buscador = wait_until_found_xpath("//header/div/div/div/div/div/div[@class='v-select__selections']", 30)
            if div_buscador is not None:
                print("Pulsamos click")
                div_buscador.click()
                buscador = wait_until_found_xpath("//header/div/div/div/div/div/div[@class='v-select__selections']/input[starts-with(@id,'input') and @type='text']", 30)
                if buscador is not None:
                    print("******* PONEMOS LA EMPRESA ("+nombre_empresa+") *************")
                    buscador.send_keys(Keys.BACKSPACE)
                    print("Borrado introducido")
                    buscador.send_keys(nombre_empresa)
                    print("Empresa introducida")
                    time.sleep(1)
                    primero_de_la_lista = wait_until_found_xpath("//body/div/div/div/div/div/div[starts-with(@id,'list-item-') and '-0' = substring(@id, string-length(@id) - string-length('-0') +1) and contains(@class, 'v-list-item')]", 30)
                    if primero_de_la_lista is not None:
                        print("Pulsamos en el primero de la lista")
                        primero_de_la_lista.click()
                    else:
                        print("No se ha podido encontrar el primero de la lista")
                        exit(1)
                else:
                    print("No se ha podido ingresar la empresa en el buscador")
                    exit(1)
            else:
                print("No se ha podido encontrar el buscador")
                exit(1)
            print("Ahora buscamos el boton de Financials")
            finanzas = wait_until_found_xpath("//main/div/div/div/div/div/div/div/div/div/a[starts-with(@href,'/stock/financials')]", 20)
            if finanzas is not None:
                print("Pulsamos en Financials")
                finanzas.click()
            else:
                print("No se ha podido pulsar en Financials")
                exit(1)

            print("Ya estamos en Financials")

            print("Ahora buscamos el slider")
            #slider_fechas = wait_until_found_xpath("//main/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div[@class='v-slider__thumb primaryAction']", 20)      
            #if slider_fechas is not None:
                #from selenium.webdriver import ActionChains
                ## create action chain object
                #action_chains = ActionChains(browser)
                #print("Ahora buscamos una sección de la página que esté a la izquierda para desplazar hasta allí el slider")
                ##slider_fin = wait_until_found_xpath("//main/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/span[@class='v-slider__tick']", 20)
                #slider_fin = wait_until_found_xpath("//nav/div/div/div/div[@class='v-list-group__items']", 20)
                #if slider_fin is not None:
                    #action_chains.drag_and_drop(slider_fechas, slider_fin).perform()
                #else:
                    #print("No se ha encontrado el slider_fin -> es un div con class: v-list-group__items")            
            #else:
                #print("No se ha encontrado slider_fechas -> es un div con class: v-slider__thumb primaryAction")
            #slider_fechas = wait_until_found_xpath("//main/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/span[@class='v-slider__tick' and @style='width: 5px; height: 5px; left: calc(0% - 2.5px); top: calc(50% - 2.5px);']", 20)      
            #15
            time.sleep(1)
            slider_fechas = wait_until_found_xpath("//main/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/span[@class='v-slider__tick' and @style='width: 5px; height: 5px; left: calc(0% - 2.5px); top: calc(50% - 2.5px);']/div[@class='v-slider__tick-label']", 20)
            if slider_fechas is not None:
                print("Pulsamos al principio del slider.")
                try:
                    slider_fechas.click()
                    time.sleep(1)
                except:
                    print("Fallo al pulsar al principio del slider, suponemos que es por empresa con poco tiempo y pasamos.")
            else:
                print("No se ha encontrado el principio del slider -> es un span con class: v-slider__tick y style: width: 5px; height: 5px; left: calc(0% - 2.5px); top: calc(50% - 2.5px);") 
                exit(1)

            print("Ahora buscamos la pestaña de Income Statement")
            
            income_activo = wait_until_found_xpath("//main/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div[@class='v-tab v-tab--active' and contains(string(), 'Income Statement')]", 2)
            if income_activo is None:
                income = wait_until_found_xpath("//main/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div[@class='v-tab' and contains(string(), 'Income Statement')]", 20)
                if income is not None:
                    print("Pulsamos en Income Statement")
                    income.click()
                else:
                    print("No se ha podido pulsar Income Statement")
                    exit(1)
                print("Ya estamos en Income Statement")

            # Sacamos el código de la página
            html_income = browser.page_source
            # Le damos un formato bonito
            soup_income=BeautifulSoup(html_income,'html.parser')
            # Sacamos de la página la tabla Income Statement y la guardamos en table_income
            table_income = soup_income.find('table', attrs={ "class" : "fintab"})
            #table_income=pd.read_html(str(div))
            print(type(table_income))
            # Guardamos la cabecera de la tabla en headers_income
            headers_income = [header.text.strip() for header in table_income.find_all('th')]
            headers_income = [header if "/" not in header else cambiar_fecha(header) for header in headers_income]
            print(headers_income)


            print("Ahora buscamos la pestaña de Balance Sheet")
            balance = wait_until_found_xpath("//main/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div[@class='v-tab' and contains(text(), 'Balance Sheet')]", 20)
            if balance is not None:
                print("Pulsamos en Balance Sheet")
                balance.click()
            else:
                print("No se ha podido pulsar Balance Sheet")
                exit(1)
            print("Ya estamos en Balance Sheet")
            # Sacamos el código de la página
            html_balance = browser.page_source
            # Le damos un formato bonito
            soup_balance=BeautifulSoup(html_balance,'html.parser')
            # Sacamos de la página la tabla Balance Sheet y la guardamos en table_balance
            table_balance = soup_balance.find('table', attrs={ "class" : "fintab"})
            #table_balance=pd.read_html(str(div))
            print(type(table_balance))
            # Guardamos la cabecera de la tabla en headers_balance
            #headers_balance = [header.text.strip() for header in table_balance.find_all('th')]
            #print(headers_balance)

            print("Ahora buscamos la pestaña de Cash Flow Statement")
            cash_flow = wait_until_found_xpath("//main/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div[@class='v-tab' and contains(text(), 'Cash Flow Statement')]", 20)
            if cash_flow is not None:
                print("Pulsamos en Cash Flow Statement")
                cash_flow.click()
            else:
                print("No se ha podido pulsar Cash Flow Statement")
                exit(1)
            print("Ya estamos en Cash Flow Statement")
            # Sacamos el código de la página
            html_cash = browser.page_source
            # Le damos un formato bonito
            soup_cash=BeautifulSoup(html_cash,'html.parser')
            # Sacamos de la página la tabla Cash Flow Statement y la guardamos en table_cash
            table_cash = soup_cash.find('table', attrs={ "class" : "fintab"})
            #table_cash=pd.read_html(str(div))
            print(type(table_cash))
            # Guardamos la cabecera de la tabla en headers_cash
            #headers_cash = [header.text.strip() for header in table_cash.find_all('th')]
            #print(headers_cash)

            datos[nombre_empresa] = []
            # Añadimos la tabla table_income a la hoja de excel de google 
            datos[nombre_empresa].append(headers_income)
            for row in table_income.find_all('tr'):
                row_to_append_income = [replace_commas(val.text.strip()) for val in row.find_all('td')]
                if len(row_to_append_income) > 0:
                    datos[nombre_empresa].append(row_to_append_income)

             # Añadimos la tabla table_balance a la hoja de excel de google 
            #datos[nombre_empresa].append(headers_balance)
            for row in table_balance.find_all('tr'):
                row_to_append_balace = [replace_commas(val.text.strip()) for val in row.find_all('td')]
                if len(row_to_append_balace) > 0:
                    datos[nombre_empresa].append(row_to_append_balace)

            # Añadimos la tabla table_cash a la hoja de excel de google 
            #datos[nombre_empresa].append(headers_cash)
            for row in table_cash.find_all('tr'):
                row_to_append_cash = [replace_commas(val.text.strip()) for val in row.find_all('td')]
                if len(row_to_append_cash) > 0:
                    datos[nombre_empresa].append(row_to_append_cash)

            #print(type(datos[nombre_empresa]))
            #print(type(datos[nombre_empresa][0]))

            #from . import example_google_sheets_v3
            print("Comenzamos con gshit..")
            #gs = Gshit()
            #spreadsheet = gs.copy_spreadsheet('Plantilla_Manu', 'Plantilla_Manu_v2')
            from datetime import date
            today = date.today()
            fecha = today.strftime("%y%m%d")
            #print("d1 =", d1)
            if not (config['template'] and config['template'] != ""):
                config['template'] = "Plantilla_Manu"
            nuevo_nombre = config['template']+nombre_empresa+"_"+fecha
            spreadsheet = copy_spreadsheet(config['template'], nuevo_nombre)
            print("Copia creada de la plantilla: "+config['template']+" con el nuevo nombre: "+nuevo_nombre)
            sheet = spreadsheet.sheet1
            print("Insertando filas...")
            print(datos[nombre_empresa][0])
            print(datos[nombre_empresa][1])
            #for r in datos[nombre_empresa][1]:
                #print(r.isnumeric())
            sheet.insert_rows(datos[nombre_empresa])
            print("Terminó la inserción")

    print("Terminando ejecución...", end='')


def init_browser():
    global browser
    # chrome_type: Valid options: google-chrome, chromium, msedge. By default, google chrome is used, but the script can also be used with 
    # Chromium or Microsoft Edge.
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--use-fake-ui-for-media-stream')
    chrome_options.add_experimental_option('prefs', {
        'credentials_enable_service': False,
        'profile.default_content_setting_values.media_stream_mic': 1,
        'profile.default_content_setting_values.media_stream_camera': 1,
        'profile.default_content_setting_values.geolocation': 1,
        'profile.default_content_setting_values.notifications': 1,
        'profile': {
            'password_manager_enabled': False
        }
    })
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    # headless: If true, runs Chrome in headless mode (does not open GUI window and runs in background).
    if 'headless' in config and config['headless']:
        chrome_options.add_argument('--headless')
        print("Enabled headless mode")
    if 'chrome_type' in config and config['chrome_type'] == "chromium":
            browser = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(), options=chrome_options)
    else:
        browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    # establecemos el tamaño del navegador para que no sea muy chico
    window_size = browser.get_window_size()
    if window_size['width'] < 1200:
        print("Resized window width")
        browser.set_window_size(1200, window_size['height'])
    if window_size['height'] < 850:
        print("Resized window height")
        browser.set_window_size(window_size['width'], 850)

def wait_until_found_xpath(sel, timeout, sel_type=By.XPATH, print_error=True):
    try:
        element_present = EC.visibility_of_element_located((sel_type, sel)) # By.CSS_SELECTOR
        WebDriverWait(browser, timeout).until(element_present)

        return browser.find_element_by_xpath(sel)    
    except exceptions.TimeoutException:
        if print_error:
            print(f"Timeout waiting for element: {sel}")
        return None


def button_execution():
    try:
        automatic_extraction()
    finally:
        if browser is not None:
            browser.quit()
        if hangup_thread is not None:
            hangup_thread.cancel()
 
def clicked():
    # Cambiamos el texto de la etiqueta
    lbl.configure (text="Button was clicked !!")
    # Tomamos el valor del campo de texto
    #name=name_entry.get() 
    if "" != name_entry.get():
        lbl.configure (text="No modificar")
    else:
        button_execution()
    #lbl.configure (text="Fuck!!")

class Window(tk.Tk):
    def __init__(self):
        super(Window,self).__init__()
        # Valores por defecto para cuando se cree una ventana
        self.title("AUTO DATA")
        self.minsize(500,400)

# Creamos la ventana del programa
window = Window()
# Añadimos una etiqueta a la ventana
lbl = tk.Label(window, text="Pulsa el botón")
lbl2 = tk.Label(window, text="")
# Establecemos la posicion de la etiqueta en la ventana (columna 0 fila 0 del grid)
lbl.grid(column=0, row=0)
lbl2.grid(column=0, row=2)
# Añadimos un boton a la ventana
btn = tk.Button(window, text="Click aquí", command=clicked)
# Establecemos la posicion del boton en la ventana (columna 1 fila 0 del grid)
btn.grid(column=0, row=3)

# Declaramos el tipo de la variable name_var a texto
name_var=tk.StringVar() 
# Añadimos una entrada de texto en la ventana
name_entry = tk.Entry(window, textvariable = name_var, font=('calibre',10,'normal')) 
name_entry.grid(row=1,column=0)
name_entry.insert(0,"")


#file = askopenfilename(parent=window,title='Choose a file')
#if file:
    #data = file.read()
    #file.close()
    #print("fichero cerrado")
window.mainloop()

