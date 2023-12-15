import datetime
import json
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from fake_headers import Headers

from vars import next_page, main_tag_id, item_tag_value, salary_class, \
    vacancy_title_class, city_data_qa, company_name_class, experience_data_qa, \
    word1, word2, site_address

headers_generator = Headers(os="win", browser="firefox")

def get_desc(addr, word_1, word_2):
    isMatch = False
    response = requests.get(addr, headers=headers_generator.generate())
    if response.status_code == 200:
        cloud_tag_list = []
        all_text = ''
        html_data = response.text
        soup = BeautifulSoup(html_data, 'lxml')
        desc_tag = soup.find('div', {'data-qa':'vacancy-description'})
        tag_cloud = soup.find('div', class_ ="bloko-tag-list")
        if tag_cloud:
            for tag in tag_cloud:
                tag_i = tag.find('span')
                cloud_tag_list.append(tag_i.text.strip())
        if desc_tag:
            all_text = all_text + desc_tag.text
        if (word_1 in all_text) and (word_2 in all_text):
            isMatch = True
        return isMatch
    else:
        print(f'status code: {response.status_code}')


def get_data(web_site, page_count):
    res_list = []
    is_next_page = True
    i = 1
    while is_next_page:
        print(f'Searching on page {i}')
        if i == 1:
            response_page = requests.get(web_site, headers=headers_generator.generate())
        else:
            response_page = requests.get(f'{web_site}{next_page}i',
                                         headers=headers_generator.generate())
        if response_page.status_code == 200:
            html_data = response_page.text
            soup = BeautifulSoup(html_data, "lxml")
            main_tag = soup.find(id=main_tag_id)
            if main_tag:
                items_tag = main_tag.find_all('div', class_=item_tag_value)
                for e in items_tag:
                    link = e.find('a', class_ = 'serp-item__title')
                    salary = e.find('span', class_ = salary_class)
                    vacancy_title = e.find('a', class_ = vacancy_title_class)
                    city = e.find('div', {'data-qa': city_data_qa})
                    company_name = e.find('a', class_ = company_name_class)
                    experience = e.find('div', {'data-qa': experience_data_qa})
                    if salary:
                        salary = salary.text.strip()
                    if get_desc(link['href'], word1, word2):
                        res_list.append({
                            'vacancy_title': vacancy_title.text.strip(),
                            'link' : link['href'],
                            'salary' : salary,
                            'company_name' : company_name.text.strip(),
                            'city' : city.text.strip(),
                            'experience': experience.text.strip()
                        })
                if i == page_count:
                    is_next_page = False
                i += 1
                print(f'{len(res_list)} vacancy(ies) found')
            else:
                print("error with parsing. Let's try again")
        else:
            is_next_page = False
            print(f'response code: {response_page.status_code}')
    print(f'Count of all found vacancy(ies): {len(res_list)}')
    with open('vacancy.json', 'w') as f:
        if len(res_list) > 0:
            json.dump(res_list, f)
        else:
            json.dump(['Nothing found'], f)
    pprint(res_list)


if __name__ == '__main__':
    print("Let's start")
    print()
    start_time = datetime.datetime.now()
    get_data(site_address, 3)
    print(f'Done in {datetime.datetime.now() - start_time}')