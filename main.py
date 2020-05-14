"""
method.me documentation url: https://wwwcdn.method.me/wp-content/uploads/2020/02/26151906/MethodAPI-DocumentationvV24.pdf
"""

from zeep import Client
from json import load as load_json
from xml.etree import ElementTree as EET

class InvalidMethodAPIOperation(AttributeError):
    pass


class MethodAPIClientOperationProxy(object):
    def __init__(self, proxy, operation, *args, **kwargs):
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
        self.operations = []
        for m in dir(self.service):
            if "__" not in m:
                self.operations.append(m)
    
    def __getattr__(self, attr):
        if attr in dir(self):
            return getattr(self, attr)
        elif attr not in self.operations:
            raise InvalidMethodAPIOperation(f"Method API Operation '{attr}' does not exist.")
        else:
            return MethodAPIClientOperationProxy(self.service, attr)
    
    @staticmethod
    def xml_response_to_array(xml_response):
        root = EET.fromstring(xml_response)    
        results = []
        for child in root:
            for ii, record in enumerate(child):
                result = {}
                for i, element in enumerate(record):
                    result[element.tag] = element.text
                    
                results.append(result)    
        return results 
    
 
    def to_compatible_array(self, values):
        empty_array_of_str = self.get_type('ns0:ArrayOfString')
        return empty_array_of_str(values)
    
    def insert_record(self, table_str, field_value_dict):
        fields, values = list(field_value_dict.keys()), list(field_value_dict.values())
        fields, values = self.to_compatible_array(fields), self.to_compatible_array(values)
        response = self.MethodAPIInsertV2(self.strCompanyAccount, 
                                            self.strLogin, 
                                            self.strPassword, 
                                            self.strSessionID, 
                                            table_str, 
                                            fields, values)
        return response 
    
    def update_record(self, record_id_int, table_str, field_value_dict):
        assert isinstance(record_id_int, int) == True
        
        fields, values = list(field_value_dict.keys()), list(field_value_dict.values())
        fields, values = self.to_compatible_array(fields), self.to_compatible_array(values)
        
        response = self.MethodAPIUpdateV2(self.strCompanyAccount, 
                                            self.strLogin, 
                                            self.strPassword, 
                                            self.strSessionID, 
                                            record.strTable, 
                                            fields, 
                                            values, 
                                            record_id_int
                                            )
        return response 

    def get_records_from_table(self, strTable, fields=["ProjectId"], where_clause=None):
        fields_array = ",".join(fields)
        if where_clause:
            xml_response = self.MethodAPISelect_XMLV2(self.strCompanyAccount, self.strLogin, self.strPassword, self.strSessionID,
                                                    strTable, fields_array, where_clause)
        else:
            xml_response = self.MethodAPISelect_XMLV2(self.strCompanyAccount, self.strLogin, self.strPassword, self.strSessionID,
                                                    strTable, fields_array)

        return MethodAPIClient.xml_response_to_array(xml_response)



if __name__ == '__main__':
    # example
    credentials = load_json(open("credentials.json"))
    client = MethodAPIClient(strCompanyAccount=credentials['strCompanyAccount'],
                            strLogin=credentials['strLogin'],
                            strPassword=credentials['strPassword'],
                            strSessionID=credentials['strSessionID'])
    result = client.MethodAPIFieldListV2(client.strCompanyAccount, client.strLogin, client.strPassword, client.strSessionID, "Contacts")