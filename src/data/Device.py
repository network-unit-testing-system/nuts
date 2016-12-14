class Device:

    def __init__(self, name, os, destination, username, password):
        self.name = name
        self.os = os
        self.destination = destination
        self.username = username
        self.password = password

    def __str__(self):
        return "Name: {0}, OS: {1}, Destination: {2}, Username: {3}, Password: {4}".format(self.name, self.os, self.destination, self.username, self.password)