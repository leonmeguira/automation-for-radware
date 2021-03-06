
from radware.sdk.beans_common import *


class GslbNewCfgEnhNetAlphaNumRealPrefTable(DeviceBean):
    def __init__(self, **kwargs):
        self.Indx = kwargs.get('Indx', None)
        self.ServerIndx = kwargs.get('ServerIndx', None)
        self.ServerPref = kwargs.get('ServerPref', None)
        self.ServerDelete = kwargs.get('ServerDelete', None)

    def get_indexes(self):
        return self.Indx, self.ServerIndx,
    
    @classmethod
    def get_index_names(cls):
        return 'Indx', 'ServerIndx',

