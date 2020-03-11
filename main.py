"""
method.me documentation url: https://wwwcdn.method.me/wp-content/uploads/2020/02/26151906/MethodAPI-DocumentationvV24.pdf
"""

from zeep import Client
from json import load as load_json


class InvalidMethodAPIOperation(AttributeError):
    pass


class MethodAPIClientOperationProxy(object):
    def __init__(self, proxy, operation):
        self.proxy = proxy
        self.operation = operation
    
    def __call__(self, *args, **kwargs):
        return getattr(self.proxy, self.operation)(*args, **kwargs)


class MethodAPIClient(Client):
    def __init__(self, strCompanyAccount=None,
                        strLogin=None, strPassword=None,
                        strSessionID="", 
                        url='https://www.methodintegration.com/MethodAPI/service.asmx?wsdl'):
        super().__init__(url)
        self.strCompanyAccount = strCompanyAccount
        self.strLogin = strLogin
        self.strPassword = strPassword
        self.strSessionID = strSessionID
        # print('service attrs: ', dir(self.service))
        self.operations = []
        for m in dir(self.service):
            if "__" not in m:
                self.operations.append(m)
    

    def __getattr__(self, attr):
        if attr in dir(self):
            result = getattr(self, attr)
        elif attr not in self.operations:
            raise InvalidMethodAPIOperation(f"Method API Operation '{attr}' does not exist.")
        else:
            return MethodAPIClientOperationProxy(self.service, attr)


if __name__ == '__main__':
    # example
    credentials = load_json(open("credentials.json"))
    client = MethodAPIClient(strCompanyAccount=credentials['strCompanyAccount'],
                            strLogin=credentials['strCompanyAccount'],
                            strPassword=credentials['strCompanyAccount'],
                            strSessionID=credentials['strSessionID'])
    result = client.MethodAPIFieldListV2(client.strCompanyAccount, client.strLogin, client.strPassword, client.strSessionID, "Contacts")
