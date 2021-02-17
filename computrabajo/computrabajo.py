import requests
import lxml.html as html
import pandas as pd
from datetime import datetime

MAIN_URL = 'https://www.computrabajo.com.co/ofertas-de-trabajo/?by=publicationtime&pubdate=1&sal=5'
SLICE_URL = 'https://www.computrabajo.com.co'
XPATH_link = '//div[@class="gO"]/div//h2/a/@href'
XPATH_name = '//div[@class="gO"]/div//h2/a/text()'
XPATH_city = '//div[@class="gO"]/div//div//span[@itemprop="addressLocality"]//text()'
XPATH_city2 = '//div[@class="gO"]/div//div//span[@itemprop="addressRegion"]/a/text()'
XPATH_summary = '//div[@class="gO"]/div//p/text()'
XPATH_company = '//div[@class="gO"]/div//div//span[@itemprop="name"]'
XPATH_company2 = '//div[@class="gO"]/div//div//span[@itemprop="name"]/a/text()'
XPATH_next_pag = '//div[@class="paginas paginasCenter"]//li[@title="Siguiente"]/a/@href'
MAIN = 'Computrabajo'


def balance_cities(city, city2):
    ciudades = ['Bogotá, D.C.','Antioquia', 'Valle del Cauca', 'Cundinamarca', 'Atlántico', 'Santander',
         'Risaralda', 'Bolívar', 'Boyacá', 'Tolima', 'Caldas', 'Meta', 'Norte de Santander', 'Huila',
         'Quindio', 'Nariño', 'Cauca', 'Cesar', 'Magdalena', 'Córdoba', 'Sucre', 'Casanare', 'La Guajira',
         'Caquetá', 'Archipiélago de San Andrés, Providencia y Santa Catalina', 'Chocó', 'Putumayo', 'Amazonas',
         'Arauca', 'Vichada', 'Guainía', 'Guaviare', 'Extranjero', 'Vaupés']
    j = 0
    departamento = []
    for i in city:
        if (i in ciudades) & (j < len(city2)):
            departamento.append(city2[j])
            j += 1
        elif j >= len(city2)-1:
            departamento.append("")
            print('Error de Ciudad')
        else:
            departamento.append(i)
    return departamento


def extract_data(parsed):
    link = parsed.xpath(XPATH_link)
    link = [SLICE_URL + i for i in link]
    name = parsed.xpath(XPATH_name)
    city = parsed.xpath(XPATH_city)
    city2 = parsed.xpath(XPATH_city2)
    summary = parsed.xpath(XPATH_summary)
    company = company_extract(parsed.xpath(XPATH_company), parsed.xpath(XPATH_company2))
    date = [f'{datetime.today().day}-{datetime.today().month}-{datetime.today().year}' for _ in range(len(link))]
    source = [MAIN for _ in range(len(link))]
    vacantes = []
    if len(city) > len(city2):
        city2 = balance_cities(city, city2)
    
    for i in range(len(link)):
        vacantes.append([name[i], date[i], company[i], link[i], summary[i], source[i], city[i], city2[i]])
    return vacantes


def company_extract(first, second):
    companies = []
    j = 0
    for i in first:
        company = i.xpath('text()')[0].replace('\r', '').replace('\n', '').strip()
        if company:
            companies.append(company.strip())
        else:
            companies.append(second[j])
            j += 1
    return companies


def parse_home(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            home = response.content.decode('utf-8')
            parsed = html.fromstring(home)
            data = extract_data(parsed)
            next_link = parsed.xpath(XPATH_next_pag)
            print(next_link)
        else:
            raise ValueError(f'Error: {response.status_code}')
    except ValueError as ve:
        print(ve)
    return data, next_link


def run():
    data = []
    link = MAIN_URL
    while len(link) != 0:
        transitoria, link = parse_home(link)
        data.extend(transitoria)
        if len(link) != 0:
            link = link[0]
    data = pd.DataFrame(data, columns=['Vacante', 'Fecha', 'Compania', 'Link', 'Informacion_Adicional',
                                       'Fuente', 'Departamento', 'Ciudad'])
    data.to_excel(f'Computrabajo_{data.iloc[0, 1]}.xlsx', index=False)
    return data


if __name__ == '__main__':
    data = run()
    print(data)
