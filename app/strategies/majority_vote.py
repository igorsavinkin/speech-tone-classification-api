from collections import Counter
from typing import List, Optional

from app.schemas import Label
from app.strategies.base import AggregationStrategy


class MajorityVoteStrategy(AggregationStrategy):
    def __init__(self, min_votes: int = 3) -> None:
        self.min_votes = min_votes

    def aggregate(self, labels: List[Label]) -> Optional[Label]:
        if len(labels) < self.min_votes:
            return None
        counts = Counter(labels)
        top_two = counts.most_common(2)
        if len(top_two) == 1:
            return top_two[0][0]
        if top_two[0][1] == top_two[1][1]:
            return None
        return top_two[0][0]
