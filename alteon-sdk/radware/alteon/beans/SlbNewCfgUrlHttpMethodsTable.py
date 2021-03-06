
from radware.sdk.beans_common import *


class EnumSlbUrlHttpMethodDelete(BaseBeanEnum):
    other = 1
    delete = 2


class SlbNewCfgUrlHttpMethodsTable(DeviceBean):
    def __init__(self, **kwargs):
        self.Index = kwargs.get('Index', None)
        self.String = kwargs.get('String', None)
        self.Delete = EnumSlbUrlHttpMethodDelete.enum(kwargs.get('Delete', None))

    def get_indexes(self):
        return self.Index,
    
    @classmethod
    def get_index_names(cls):
        return 'Index',

