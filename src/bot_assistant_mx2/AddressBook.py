from datetime import timedelta, datetime
from collections import UserList
import pickle
from enum import Enum

from .info import *
import os


class LoggerInterface(ABC):
    @abstractmethod
    def log(self, message):
        pass


class LoggerStudy(LoggerInterface):
    def log(self, action):
        current_time = dt.strftime(dt.now(), '%H:%M:%S')
        message = f'[{current_time}] {action}'
        with open('logs.txt', 'a') as file:
            file.write(f'{message}\n')


class DataManagerInterface(ABC):
    @abstractmethod
    def save_data(self, file_name):
        pass

    @abstractmethod
    def load_data(self, file_name):
        pass


class LocalDataManager(DataManagerInterface):
    def __init__(self, logger: LoggerInterface):
        self.logger = logger

    def save_data(self, file_name):
        with open(file_name + '.bin', 'wb') as file:
            pickle.dump(self.data, file)
        self.logger.log("Addressbook has been saved!")

    def load_data(self, file_name):
        file_path = file_name + '.bin'
        if not os.path.exists(file_path):
            self.data = {}  # or initialize the data in any desired way
            with open(file_path, 'wb') as file:
                pickle.dump(self.data, file)
            self.logger.log('Address book has been created!')
        else:
            with open(file_path, 'rb') as file:
                self.data = pickle.load(file)
            self.logger.log('Address book has been loaded!')
        return self.data


class Weekday(Enum):
    MONDAY = 'Monday'
    TUESDAY = 'Tuesday'
    WEDNESDAY = 'Wednesday'
    THURSDAY = 'Thursday'
    FRIDAY = 'Friday'
    SATURDAY = 'Saturday'
    SUNDAY = 'Sunday'


class DateTimeManager:
    @staticmethod
    def get_current_week():
        now = dt.now()
        current_weekday = now.weekday()
        if current_weekday < 5:
            week_start = now - timedelta(days=2 + current_weekday)
        else:
            week_start = now - timedelta(days=current_weekday - 5)
        return [week_start.date(), week_start.date() + timedelta(days=7)]


class CongratulateInterface(ABC):
    @abstractmethod
    def value_of(self, data):
        pass


class CongratulateBirthday:
    @staticmethod
    def value_of(data):
        current_year = datetime.now().year
        current_week_start, current_week_end = DateTimeManager.get_current_week()
        congratulate = {day.value: [] for day in Weekday}
        for account in data:
            if account['birthday']:
                new_birthday = account['birthday'].replace(year=current_year)
                if current_week_start <= new_birthday.date() < current_week_end:
                    weekday = Weekday(new_birthday.strftime(
                        "%A")).value
                    congratulate[weekday].append(account['name'])
        return '\n'.join(
            [f"{day}: {' '.join(names)}" for day, names in congratulate.items()
             if names]) \
            if any(congratulate.values()) else ''


class AddressBook(UserList):
    def __init__(
            self, logger: LoggerInterface, data_manager: LocalDataManager,
            birthday: CongratulateBirthday
    ):
        super().__init__()
        self.data = []
        self.counter = -1
        self.logger = logger
        self.data_manager = data_manager
        self.birthday = birthday

    def __str__(self):
        result = []
        for account in self.data:
            if account['birthday']:
                birth = account['birthday'].strftime("%d/%m/%Y")
            else:
                birth = ''
            if account['phones']:
                new_value = []
                for phone in account['phones']:
                    print(phone)
                    if phone:
                        new_value.append(phone)
                phone = ', '.join(new_value)
            else:
                phone = ''
            result.append(
                "_" * 50 + "\n" + f"Name: {account['name']} \nPhones: {phone} \nBirthday: {birth} \nEmail: {account['email']} \nStatus: {account['status']} \nNote: {account['note']}\n" + "_" * 50 + '\n')
        return '\n'.join(result)

    def __next__(self):
        phones = []
        self.counter += 1
        if self.data[self.counter]['birthday']:
            birth = self.data[self.counter]['birthday'].strftime("%d/%m/%Y")
        if self.counter == len(self.data):
            self.counter = -1
            raise StopIteration
        for number in self.data[self.counter]['phones']:
            if number:
                phones.append(number)
        result = "_" * 50 + "\n" + f"Name: {self.data[self.counter]['name']} \nPhones: {', '.join(phones)} \nBirthday: {birth} \nEmail: {self.data[self.counter]['email']} \nStatus: {self.data[self.counter]['status']} \nNote: {self.data[self.counter]['note']}\n" + "_" * 50
        return result

    def __iter__(self):
        return self

    def __setitem__(self, index, record):
        self.data[index] = {'name': record.name,
                            'phones': record.phones,
                            'birthday': record.birthday}

    def __getitem__(self, index):
        return self.data[index]

    def add(self, record):
        account = {'name': record.name,
                   'phones': record.phones,
                   'birthday': record.birthday,
                   'email': record.email,
                   'status': record.status,
                   'note': record.note}
        self.data.append(account)
        self.logger.log(f"Contact {record.name} has been added.")

    def search(self, pattern, category):
        result = []
        category_new = category.strip().lower().replace(' ', '')
        pattern_new = pattern.strip().lower().replace(' ', '')

        for account in self.data:
            if category_new == 'phones':

                for phone in account['phones']:

                    if phone.lower().startswith(pattern_new):
                        result.append(account)
            elif account[category_new].lower().replace(' ', '') == pattern_new:
                result.append(account)
        if not result:
            print('There is no such contact in address book!')
        return result

    def edit(self, contact_name, parameter, new_value):
        names = []
        try:
            for account in self.data:
                names.append(account['name'])
                if account['name'] == contact_name:
                    if parameter == 'birthday':
                        new_value = Birthday(new_value).value
                    elif parameter == 'email':
                        new_value = Email(new_value).value
                    elif parameter == 'status':
                        new_value = Status(new_value).value
                    elif parameter == 'phones':
                        new_contact = new_value.split(' ')
                        new_value = []
                        for number in new_contact:
                            new_value.append(Phone(number).value)
                    if parameter in account.keys():
                        account[parameter] = new_value
                    else:
                        raise ValueError
            if contact_name not in names:
                raise NameError
        except ValueError:
            print('Incorrect parameter! Please provide correct parameter')
        except NameError:
            print('There is no such contact in address book!')
        else:
            self.logger.log(f"Contact {contact_name} has been edited!")
            return True
        return False

    def remove(self, pattern):
        flag = False
        for account in self.data:
            if account['name'] == pattern:
                self.data.remove(account)
                self.logger.log(f"Contact {account['name']} has been removed!")
                flag = True
            '''if pattern in account['phones']:
                        account['phones'].remove(pattern)
                        self.log.log(f"Phone number of {account['name']} has been removed!")'''
        return flag

    def congratulate_birthday(self):
        return self.birthday.value_of(data=self.data)

