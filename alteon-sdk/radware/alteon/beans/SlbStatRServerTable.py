
from radware.sdk.beans_common import *


class SlbStatRServerTable(DeviceBean):
    def __init__(self, **kwargs):
        self.Index = kwargs.get('Index', None)
        self.CurrSessions = kwargs.get('CurrSessions', None)
        self.TotalSessions = kwargs.get('TotalSessions', None)
        self.Failures = kwargs.get('Failures', None)
        self.HighestSessions = kwargs.get('HighestSessions', None)
        self.HCOctetsLow32 = kwargs.get('HCOctetsLow32', None)
        self.HCOctetsHigh32 = kwargs.get('HCOctetsHigh32', None)
        self.HCOctets = kwargs.get('HCOctets', None)
        self.UpTime = kwargs.get('UpTime', None)
        self.DownTime = kwargs.get('DownTime', None)
        self.LastFailureTime = kwargs.get('LastFailureTime', None)

    def get_indexes(self):
        return self.Index,
    
    @classmethod
    def get_index_names(cls):
        return 'Index',

