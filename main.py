import requests
import time

from bs4 import BeautifulSoup
from threading import *

from model import Person
from utils import get_multilist



headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    }


def get_pages():
    """
    Function to get link all pages.
    """

    with open('persons_links.txt', 'w') as file:
        for page_number in range(1, 15):
            url = f'https://holisticdental.org/find-a-holistic-dentist/?query&by&sort_field=id&sort_order=desc&page_no={page_number}'
            file.write(f'{url}\n')


def get_profile_link(*args):
    """
    Function to get all profile links.
    """

    for line in args:
        if line is None:
            continue
        page_query = requests.get(line, headers=headers)
        page_soup = BeautifulSoup(page_query.text, 'lxml')
        profile_link = page_soup.find_all('div', class_='pfl_mi')

        with open('links.txt', 'a') as persons_file:
            for link in profile_link:
                clean_link = link.find('a')['href']
                persons_file.write(f'{clean_link}\n')


def get_profile_data(*args):
    """
    Function to get all profiles and save to SqlDatabase.
    """

    for line in args:
        if line is None:
            continue
        profile_query = requests.get(line, headers=headers)
        profile_soup = BeautifulSoup(profile_query.text, 'lxml')

        person_name = profile_soup.find('h1').text
        firstname = person_name.split()[1]
        lastname = person_name.split()[0].strip(',')
        try:
            person_email = profile_soup.find('table').find(string='Email:').find_next('a').text
        except AttributeError:
            person_email = None
        try:
            person_location = profile_soup.find('table').find(string='City, State Zip:').find_next('td').text
        except AttributeError:
            person_location = None
        try:
            person_location_street = profile_soup.find('table').find(string='Street:').find_next('td').text
        except AttributeError:
            person_location_street = None
        try:
            person_phone = profile_soup.find('table').find(string='Phone:').find_next('td').text
        except AttributeError:
            person_phone = None
        person_link = line

        persons = Person(
            person_email=person_email,
            firstname=firstname,
            lastname=lastname,
            person_link=person_link,
            person_location_street=person_location_street,
            person_location=person_location,
            person_phone=person_phone,
        )
        persons.save()



def multi_th(data:str, th:int, func):
    """
    Method for running functions in multithreading.
    """

    with open(f'{data}') as file:
        lines = [line.strip() for line in file.readlines()]

    multilist = list(get_multilist(lines, c_num=th))

    for i in range(th):
        Thread(target=func, args=multilist[i]).start()



def main():
    question = input(f'Start scraping?  \n yes or no \n')
    if question == 'yes':
        get_pages()
        print('Please wait.')
    else:
        exit()

    multi_th(data='persons_links.txt', th=2, func=get_profile_link)
    while active_count() > 1:
        time.sleep(3)
    multi_th(data='links.txt', th=100, func=get_profile_data)
    while active_count() > 1:
        time.sleep(3)
    print('End scraping. Thanks for waiting')


main()