from src.levels.Chatterbox import ChatterboxLevel
from src.levels.PrecisionPerformer import PrecisionPerformerLevel
from src.levels.Fibonacci import FibonacciLevel
from src.levels.YesNo import YesNoLevel
from src.levels.Family import FamilyLevel

levels = {
    1: ChatterboxLevel(),
    2: PrecisionPerformerLevel(),
    3: FibonacciLevel(),
    4: YesNoLevel(),
    5: FamilyLevel(),
}
max_level = max(levels.keys())
