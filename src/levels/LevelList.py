from src.levels.Chatterbox import ChatterboxLevel
from src.levels.PrecisionPerformer import PrecisionPerformerLevel
from src.levels.Fibonacci import FibonacciLevel
from src.levels.YesNo import YesNoLevel
from src.levels.Family import FamilyLevel
from src.levels.XMLEngineering import XMLEngineeringLevel

levels = {
    1: ChatterboxLevel(),
    2: PrecisionPerformerLevel(),
    3: FibonacciLevel(),
    4: XMLEngineeringLevel(),
    5: YesNoLevel(),
    6: FamilyLevel(),
}
max_level = max(levels.keys())
