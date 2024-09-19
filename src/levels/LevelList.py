from src.levels.Chatterbox import ChatterboxLevel
from src.levels.PrecisionPerformer import PrecisionPerformerLevel
from src.levels.Fibonacci import FibonacciLevel
from src.levels.YesNo import YesNoLevel
from src.levels.Family import FamilyLevel
from src.levels.XMLEngineering import XMLEngineeringLevel
from src.levels.MarkdownFormatting import MarkdownFormattingLevel

levels = {
    1: ChatterboxLevel(),
    2: PrecisionPerformerLevel(),
    3: MarkdownFormattingLevel(),
    4: XMLEngineeringLevel(),
    5: FibonacciLevel(),
    6: YesNoLevel(),
    7: FamilyLevel(),
}
max_level = max(levels.keys())
