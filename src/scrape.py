import requests
from bs4 import BeautifulSoup
from configparser import ConfigParser
import time


def getCvMarketPageData(page, city, keyword, job_category):

    last_page = 1

    while last_page > page:

        time.sleep(1)

        if page != 0:

            url = ''.join(f"""\
                https://www.cvmarket.lt/joboffers.php?_track=index_click_job_search&op=search&search_location=\
            landingpage&ga_track=homepage&dummy_locations={city_dict[city]}&dummy_categories={job_category_dict[job_category]}&search[keyword]=\
            {keyword}s&mobile_search[keyword]={keyword}&tmp_city=&search[locations][]={city_dict['Vilnius']}&tmp_cat=\
            &search[categories][]={job_category_dict[job_category]}&tmp_city=&dummy_search[locations][]={city_dict[city]}&tmp_category=\
            &dummy_search[categories][]={job_category_dict[job_category]}&search[keyword]={keyword}&search[expires_days]=\
            &search[job_lang]=&search[salary]=&search[job_salary]=3&start={page*30}\
                    """.split())

        else:

            url = ''.join(f"""\
            https://www.cvmarket.lt/joboffers.php?_track=index_click_job_search&op=search&search_location=\
            landingpage&ga_track=homepage&dummy_locations={city_dict[city]}&dummy_categories={job_category_dict[job_category]}&search[keyword]=\
            {keyword}s&mobile_search[keyword]={keyword}&tmp_city=&search[locations][]={city_dict[city]}&tmp_cat=\
            &search[categories][]={job_category_dict[job_category]}&tmp_city=&dummy_search[locations][]={city_dict[city]}&tmp_category=\
            &dummy_search[categories][]={job_category_dict[job_category]}&search[keyword]={keyword}&search[expires_days]=\
            &search[job_lang]=&search[salary]=&search[job_salary]=3\
            """.split())

        r = requests.get(url).text
        soup = BeautifulSoup(r, 'lxml')
        job_rows = soup.find_all('tr', {'class': 'f_job_row2'})

        end = soup.find('ul', {'class': 'pagination'})

        if end != None:

            lis = end.findAll('a')

            last_index = len(lis)-4
            last_page = int(lis[last_index].text)

        if end == None:
            last_page = 1

        for i in range(len(job_rows)):

            job_title = job_rows[i].find('a', {'class': 'f_job_title'})

            job_company = job_rows[i].find('span', {'class': 'f_job_company'})

            job_salary = job_rows[i].find(
                'span', {'class': 'f_job_salary'}).find('b')

            job_salary_type = job_rows[i].find(
                'span', {'class': 'salary-type'})

            href = job_title.get('href')
            website_from = 'cvmarket'

            job_url = f'https://www.{website_from}.lt{href}'

            # get dates from deeper job posting page
            r2 = requests.get(job_url).text
            soup2 = BeautifulSoup(r2, 'lxml')

            details = soup2.find_all('div', {'class': 'jobdetails_value'})
            posting_date = details[-1] if details[-1] != None else 'Nėra'
            expiration_date = details[-2] if details[-2] != None else 'Nėra'

            writeToData(job_title, job_salary, job_company, job_salary_type,
                        posting_date, expiration_date, url, website_from)

        page += 1


keyword = ''

city_dict = {
    'Vilnius': '134',
    'Kaunas': '135',
    'Klaipėda': '136',
    'Šiauliai': '137',
    'Panevėžys': '138',
    'Alytus': '282',
}

job_category_dict = {
    'Visos kategorijos': '-1',
    'Administravimas': '2',
    'Apsauga': '16',
    'Aptarnavimas': '18',
    'Bankai / Draudimas': '38',
    'Dizainas / Kultūra / Pramogos': '12',
    'Elektronika / Telekomunikacijos': '4',
    'Energetika / Gamtos ištekliai': '5',
    'Finansai': '6',
    'Informacija / Žiniasklaida': '7',
    'Informacinės technologijos': '8',
    'Maitinimas': '20',
    'Marketingas / Reklama / RsV': '23',
    'Mechanika / Inžinerija': '14',
    'Pardavimai / Pirkimai': '15',
    'Personalo valdymas / Mokymai': '11',
    'Pramonė / Gamyba': '24',
    'Savanorystė / Praktika': '37',
    'Statyba / Nekilnojamasis turtas': '3',
    'Sveikata / Medicina / Farmacija': '19',
    'Švietimas / Moksliniai tyrimai': '25',
    'Teisė': '36',
    'Transportas / Logistika / Sandėliavimas': '21',
    'Turizmas / Viešbučiai': '22',
    'Vadovavimas / Verslo vystymas': '9',
    'Valstybinė tarnyba': '17',
    'Žemės ūkis / Miškininkystė / Gyvulininkystė': '13',
}


def getCvOnlineData(city, keyword, job_category):

    job_category_dict_cvOnline = {
        'Informacinės technologijos': 'INFORMATION_TECHNOLOGY',
        'Paslaugos / klientų aptarnavimas': 'SERVICE_INDUSTRY',
        'Finansai / apskaita': 'FINANCE_ACCOUNTING',
        'Organizavimas / valdymas': 'ORGANISATION_MANAGEMENT',
        'Gamyba / Pramonė': 'PRODUCTION_MANUFACTURING',
        'Bankai / draudimas': 'BANKING_INSURANCE',
        'Inžinerija': 'TECHNICAL_ENGINEERING',
        'Administravimas': 'ADMINISTRATION',
        'Pardavimai': 'SALES',
        'Prekyba / pirkimai / tiekimas': 'TRADE',
        'Transportas / logistika': 'LOGISTICS_TRANSPORT',
        'Elektronika / telekomunikacijos': 'ELECTRONICS_TELECOM',
        'Žmogiškieji ištekliai': 'HUMAN_RESOURCES',
        'Rinkodara / reklama': 'MARKETING_ADVERTISING',
        'Teisė': 'LAW_LEGAL',
        'Statyba / nekilnojamas turtas': 'CONSTRUCTION_REAL_ESTATE',
        'Energetika': 'ENERGETICS_ELECTRICITY',
        'Valstybinis / viešasis adminstravimas': 'STATE_PUBLIC_ADMIN',
        'Kokybės kontrolė': 'QUALITY_ASSURANCE',
        'Švietimas / mokslas': 'EDUCATION_SCIENCE',
        'Žiniasklaida / ryšys su visuomene': 'MEDIA_PR',
        'Praktika': 'INTERNSHIP',
        'Turizmas / viešbučiai / maitinimas': 'TOURISM_HOTELS_CATERING',
        'Medicina / socialinė rūpyba': 'HEALTH_SOCIAL_CARE',
        'Apsauga / gelbėjimo paslaugos / gynyba': 'SECURITY_RESCUE_DEFENCE',
        'Žemės ūkis / aplinkosauga': 'AGRICULTURE_ENVIRONMENTAL',
        'Kultūra / pramogos / sportas': 'CULTURE_ENTERTAINMENT',
        'Farmacija': 'PHARMACY',
        'Trečiasis sektorius / NVO': 'THIRD_SECTOR',
        'Miškininkystė / medienos apdirbimas': 'FOREST_WOODCUTTING',
        'Sezoninis': 'SEASONAL',
        'Savanoriškas darbas': 'VOLUNTARY',
    }

    city_dict_cvOnline = {
        'Vilnius': '540',
        'Kaunas': '501',
        'Klaipėda': '505',
        'Šiauliai': '528',
        'Panevėžys': '517',
        'Alytus': '488',
    }

    url = ''.join(f"""\
                https://cvonline.lt/lt/search?limit=2000&offset=0&categories%5B0%5D={job_category_dict_cvOnline[job_category]}&\
                keywords%5B0%5D={keyword}&towns%5B0%5D={city_dict_cvOnline[city]}&fuzzy=true&suitableForRefugees=false&isHourlySalary=false&isRemoteWork=false&isQuickApply=false
                    """.split())

    r = requests.get(url).text
    soup = BeautifulSoup(r, 'lxml')

    job_row = soup.find_all('a', {'class': 'vacancy-item'})

    for job in job_row:

        job_title = job.find('span', {'class': 'vacancy-item__title'})
        job_company = job.find(
            'div', {'class': 'vacancy-item__body'}).find('a')
        job_salary = job.find('span', {'class': 'vacancy-item__salary-label'})
        salary_type = 'neatskaičiavus mokesčių'
        job_href = job.get('href')
        posting_date = ''
        job_url = f'https://www.cvonline.lt{job_href}'
        website_from = 'cvonline'

        time.sleep(0.2)

        r2 = requests.get(job_url).text
        soup2 = BeautifulSoup(r2, 'lxml')

        expiration_date = soup2.find(
            'span', {'class': 'vacancy-info__deadline'})

        writeToData(job_title, job_salary, job_company, salary_type,
                    posting_date, expiration_date, url, website_from)


def writeToData(title, salary, company, salary_type, posting_date,
                expiration_date, url, website_from):

    if not any((job['title'] == title.text.lstrip().strip()) &
               (job['company'] == company.text.lstrip().strip()) for job in data):

        data.append(
            {
                'id': len(data),
                'title': title.text.lstrip().strip(),
                'company': company.text.lstrip().strip(),
                'salary': salary.text.lstrip().strip() if salary != None else 'Nėra',
                'salary_type': salary_type,
                'city': city,
                'posting_date': posting_date.text.lstrip().strip() if type(posting_date) != str else '',
                'expiration_date': expiration_date.text.lstrip().strip() if expiration_date != None else 'Nėra',
                'website_from': website_from,
                'url': url.lstrip().strip(),


            }
        )
        print(len(data))
    else:
        print('rejected')


data = []
page = 0

city = 'Vilnius'
keyword = 'vadovas'
job_category = 'Informacinės technologijos'


getCvMarketPageData(page, city, keyword, job_category)
getCvOnlineData(city, keyword, job_category)
