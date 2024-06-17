import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuração do WebDriver
chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://gizmodo.uol.com.br/tecnologia')
wait = WebDriverWait(driver, 1)
driver.maximize_window()

noticias = []

def extrair_noticias(pagina=1):
    # Esperar até que a seção de posts com as notícias seja carregada
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'posts')))

    # Encontrar todos os artigos de notícias
    artigos = driver.find_elements(By.CLASS_NAME, 'sup-post-card')

    for i, artigo in enumerate(artigos[:5], start=1):
        # Construir o XPath dinamicamente para o título do artigo
        xpath_titulo = f'//*[@id="content"]/section[3]/div/div/div[1]/article[{i}]/div/h2/a'

        # Clicar no título do artigo para abrir a página da notícia
        titulo_link = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_titulo)))
        driver.execute_script("arguments[0].scrollIntoView(true);", titulo_link)  # Scroll into view
        titulo = titulo_link.text
        titulo_link.click()

        # Esperar até que a página individual da notícia seja carregada completamente
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'sup-container')))

        # Construir o XPath para o elemento que contém o resumo da notícia
        xpath_resumo = '//*[@class="sup-container"]/div[@class="content"]/span[@class="cat"]/div[@class="except"]'

        # Encontrar o elemento do resumo da notícia
        resumo_element = wait.until(EC.visibility_of_element_located((By.XPATH, xpath_resumo)))

        # Extrair o texto do resumo
        resumo = resumo_element.text

        # Construir o XPath para encontrar a data da notícia
        xpath_data = '//*[@class="sup-single__postinfo"]/time[@class="date"]'

        # Encontrar o elemento da data da notícia
        data_element = wait.until(EC.visibility_of_element_located((By.XPATH, xpath_data)))

        # Extrair o texto da data
        data = data_element.get_attribute('datetime')

        # Armazenar as informações da notícia em um dicionário
        noticias.append({
            'titulo': titulo,
            'resumo': resumo,
            'data': data
        })

        # Voltar para a página anterior (lista de notícias de tecnologia)
        driver.back()

        # Esperar até que a seção de posts com as notícias seja carregada novamente
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'posts')))

        # Atualizar a lista de artigos após voltar
        artigos = driver.find_elements(By.CLASS_NAME, 'sup-post-card')

    if pagina < 2:
        xpath_proxima_pagina = f'//a[@class="next page-numbers"]'
        proxima_pagina_link = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_proxima_pagina)))
        proxima_pagina_link.click()
        extrair_noticias(pagina + 1)

# Chamar a função que vai receber as informações das 2 páginas
extrair_noticias()

# Escrever as informações coletadas em um arquivo CSV
with open('noticias_gizmodo.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)

    # Escrever cada notícia no arquivo CSV
    for idx, noticia in enumerate(noticias, start=1):
        writer.writerow([f'Notícia {idx}:'])
        writer.writerow(['Título da notícia: ' + noticia['titulo']])
        writer.writerow(['Resumo da notícia: ' + noticia['resumo']])
        writer.writerow(['Data da notícia: ' + noticia['data']])
        writer.writerow([])

# Fechar o navegador ao final do processo
driver.quit()
