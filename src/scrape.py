import requests
from bs4 import BeautifulSoup
from configparser import ConfigParser
from search_variables import city_dict_cvMarket, job_category_dict_cvMarket, job_category_dict_cvOnline, city_dict_cvOnline
import time
import logging


def getCvMarketPageData(page, city, keyword, job_category):

    last_page = 1
    global cvMarket_postings
    cvMarket_postings = 0

    while last_page > page:

        time.sleep(1)

        if page != 0:

            url = ''.join(f"""\
                https://www.cvmarket.lt/joboffers.php?_track=index_click_job_search&op=search&search_location=\
            landingpage&ga_track=homepage&dummy_locations={city_dict_cvMarket[city]}&dummy_categories={job_category_dict_cvMarket[job_category]}&search[keyword]=\
            {keyword}s&mobile_search[keyword]={keyword}&tmp_city=&search[locations][]={city_dict_cvMarket['Vilnius']}&tmp_cat=\
            &search[categories][]={job_category_dict_cvMarket[job_category]}&tmp_city=&dummy_search[locations][]={city_dict_cvMarket[city]}&tmp_category=\
            &dummy_search[categories][]={job_category_dict_cvMarket[job_category]}&search[keyword]={keyword}&search[expires_days]=\
            &search[job_lang]=&search[salary]=&search[job_salary]=3&start={page*30}\
                    """.split())

        else:

            url = ''.join(f"""\
            https://www.cvmarket.lt/joboffers.php?_track=index_click_job_search&op=search&search_location=\
            landingpage&ga_track=homepage&dummy_locations={city_dict_cvMarket[city]}&dummy_categories={job_category_dict_cvMarket[job_category]}&search[keyword]=\
            {keyword}s&mobile_search[keyword]={keyword}&tmp_city=&search[locations][]={city_dict_cvMarket[city]}&tmp_cat=\
            &search[categories][]={job_category_dict_cvMarket[job_category]}&tmp_city=&dummy_search[locations][]={city_dict_cvMarket[city]}&tmp_category=\
            &dummy_search[categories][]={job_category_dict_cvMarket[job_category]}&search[keyword]={keyword}&search[expires_days]=\
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
                'span', {'class': 'f_job_salary'})

            job_salary_type = job_rows[i].find(
                'span', {'class': 'salary-type'}).text.lstrip().strip()

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
            cvMarket_postings += 1
        page += 1


def getCvOnlineData(city, keyword, job_category):

    global cvOnline_postings
    cvOnline_postings = 0

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
        salary_type = 'Neatskaičiavus mokesčių'
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

        cvOnline_postings += 1


def writeToData(title, salary, company, salary_type, posting_date,
                expiration_date, url, website_from):

    global rejected_postings

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
        logging.info(f'job posting added. {len(data)} job postings scraped')

    else:
        rejected_postings += 1
        logging.info(
            f'duplicate posting found and rejected. total {rejected_postings} rejected')

    print(f'parsing: postings parsed {len(data) + rejected_postings}')


f = './config/config.ini'
config = ConfigParser()
config.read(f)

log_level = getattr(logging, config['log_level']['level'])

logging.basicConfig(
    level=log_level,
    format='[%(levelname)s] - %(asctime)s - %(message)s',
    filename=config['log_file']['fname'],
    filemode=config['log_file_mode']['fmode']
)

data = []
page = 0

rejected_postings = 0

# categories can be found in search_variables.py
city = 'Vilnius'
keyword = 'vadovas'
job_category = 'Informacinės technologijos'


getCvMarketPageData(page, city, keyword, job_category)
getCvOnlineData(city, keyword, job_category)

logging.info(f'{cvMarket_postings} postings found in cvmarket.lt')
logging.info(f'{cvOnline_postings} postings found in cvonline.lt')
logging.info(f'{rejected_postings} postings rejected')

for job in data:
    print(
        f'{job["title"]} --- {job["company"]} --- {job["salary"]} {job["salary_type"]}')
