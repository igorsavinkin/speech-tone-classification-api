from abc import ABC, abstractmethod
from typing import List, Optional

from app.schemas import Label


class AggregationStrategy(ABC):
    @abstractmethod
    def aggregate(self, labels: List[Label]) -> Optional[Label]:
        raise NotImplementedError
