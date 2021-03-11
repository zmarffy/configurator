import argparse
import configparser
from enum import Enum
import os

import str2bool


class ConfigureParserException(Exception):
    pass


class UnknownTypeException(ConfigureParserException):
    pass


class MissingSectionException(ConfigureParserException):
    pass


class MissingKeyException(ConfigureParserException):
    pass


class Types(Enum):
    string = 0
    integer = 1
    float = 2
    boolean = 3


def getbool(o):
    if o is True or o is False:
        return o
    else:
        return str2bool.str2bool_exc(o)


class Configurator():

    types = {
        Types.string: str,
        Types.integer: int,
        Types.float: float,
        Types.boolean: getbool
    }

    def __init__(self, types_mapping, config_file_location):
        self.types_mapping = types_mapping
        self._config_file_location = config_file_location
        self._config_parser = configparser.ConfigParser()
        self.read_config_file()
        self._parser = self._generate_parser()

    def _convert_data(self, data):
        converted_data = {s: {} for s in self.types_mapping.keys()}
        for section_name, keys_and_types in self.types_mapping.items():
            try:
                section = data[section_name]
            except KeyError:
                raise MissingSectionException(section_name) from None
            for key, type_ in keys_and_types.items():
                try:
                    v = section[key]
                except KeyError:
                    raise MissingKeyException(key) from None
                value = self.get_value(v, type_)
                converted_data[section_name][key] = value
        return converted_data

    @classmethod
    def get_value(cls, v, type_):
        try:
            return cls.types[type_](v)
        except KeyError:
            raise UnknownTypeException(v) from None

    def parse_args(self):
        return self._parser.parse_args()

    def _get_dict_from_args(self):
        data = self.parse_args().__dict__
        section = data["section"]
        del data["section"]
        d = {section: {k: v for k, v in data.items()}}
        return d

    def write_file_from_args(self):
        d_ = self.read_config_file()
        d = self._get_dict_from_args()
        d_[list(d.keys())[0]] = list(d.values())[0]
        self.write_config_file(d_)

    def read_config_file(self):
        if not os.path.isfile(self._config_file_location):
            # Should really create the default file here
            raise FileNotFoundError(self._config_file_location)
        self._config_parser.read(self._config_file_location)
        data_from_config = {s: dict(self._config_parser.items(s))
                            for s in self._config_parser.sections()}
        return self._convert_data(data_from_config)

    def write_config_file(self, data):
        data = self._convert_data(data)
        for section_name, keys_and_values in data.items():
            for key, value in keys_and_values.items():
                self._config_parser[section_name][key] = str(value)
        with open(self._config_file_location, "w") as f:
            self._config_parser.write(f)

    def _generate_parser(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="section", required=True)
        for section_name, keys_and_types in self.types_mapping.items():
            subparser = subparsers.add_parser(section_name)
            for key, type_ in keys_and_types.items():
                subparser.add_argument(f"--{key}", type=self.types[type_])
        return parser

    def __str__(self):
        return f"<Configurator object from {self._config_file_location}>"
