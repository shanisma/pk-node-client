"""
Source : https://github.com/SebastianCzoch/influx-line-protocol
Author : Sebastian Czoch / https://github.com/SebastianCzoch

MIT License

Copyright (c) 2018 Sebastian Czoch

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


class Metric:

    def __init__(self, measurement):
        self.measurement = measurement
        self.values = {}
        self.tags = dict()

    def add_tag(self, name, value):
        self.tags[str(name)] = str(value)

    def add_value(self, name, value):
        self.values[str(name)] = value

    def __str__(self):
        # Escape measurement manually
        escaped_measurement = self.measurement.replace(',', '\\,')
        escaped_measurement = escaped_measurement.replace(' ', '\\ ')
        protocol = escaped_measurement

        # Create tag strings
        tags = []
        for key, value in self.tags.items():
            escaped_name = self.__escape(key)
            escaped_value = self.__escape(value)

            tags.append("%s=%s" % (escaped_name, escaped_value))

        # Concatenate tags to current line protocol
        if len(tags) > 0:
            protocol = "%s,%s" % (protocol, ",".join(tags))

        # Create field strings
        values = []
        for key, value in self.values.items():
            escaped_name = self.__escape(key)
            escaped_value = self.__parse_value(value)
            values.append("%s=%s" % (escaped_name, escaped_value))

        # Concatenate fields to current line protocol
        protocol = "%s %s" % (protocol, ",".join(values))
        return protocol

    def __escape(self, value, escape_quotes=False):
        # Escape backslashes first since the other characters are escaped with
        # backslashes
        new_value = value.replace('\\', '\\\\')
        new_value = new_value.replace(' ', '\\ ')
        new_value = new_value.replace('=', '\\=')
        new_value = new_value.replace(',', '\\,')

        if escape_quotes:
            new_value = new_value.replace('"', '\\"')

        return new_value

    def __parse_value(self, value):
        if type(value) is int:
            return "%di" % value

        if type(value) is float:
            return "%g" % value

        if type(value) is bool:
            return value and "t" or "f"

        return "\"%s\"" % self.__escape(value, True)
