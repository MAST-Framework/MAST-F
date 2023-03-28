from enum import IntEnum

class RiskLevel(IntEnum):
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    SECURE = 1
    INFO = 0
    
    @staticmethod
    def fromstring(value: str) -> 'RiskLevel':
        for constant in RiskLevel:
            if constant.name == value:
                return constant
        
        raise KeyError(f'Could not find risk level with name: {value}')
    
    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, str):
            return __o.upper() == self.name
        return super().__eq__(__o)
    
    def __str__(self) -> str:
        return self.name