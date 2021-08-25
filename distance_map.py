"""
===== Module Description =====

This module contains the class DistanceMap, which is used to store
and look up distances between cities. This class does not read distances
from the map file. (All reading from files is done in module experiment.)
Instead, it provides public methods that can be called to store and look up
distances.
"""
from typing import Dict, Tuple


class DistanceMap:
    """A distance map which records distance between pairs of cities

    === Private Attributes ===
    _rec: Records the distance between pairs of cities
    """
    # Attribute types
    _rec: Dict[Tuple[str, str], int]

    def __init__(self) -> None:
        """Initialize a new DistanceMap

        >>> d = DistanceMap()
        >>> d._rec
        {}
        """

        self._rec = {}

    def add_distance(self, a: str, b: str, di1: int, di2: int = None) -> None:
        """Record that the distance from city a to city b is di1, and the
        distance from city b to city a is equal to di2. If the value of di2 is
        not specified in the function call, we take di2 = di1.

        If the distance from city a and city b, and from city b to city a has
        already been recorded, update it to di1 and di2 respectively.

        >>> d = DistanceMap()
        >>> d._rec
        {}
        >>> d.add_distance('Toronto', 'Vancouver', 1000, 1001)
        >>> d._rec
        {('Toronto', 'Vancouver'): 1000, ('Vancouver', 'Toronto'): 1001}
        >>> d2 = DistanceMap()
        >>> d2.add_distance('Toronto', 'Vancouver', 1000)
        >>> d2._rec
        {('Toronto', 'Vancouver'): 1000, ('Vancouver', 'Toronto'): 1000}
        """

        self._rec[(a, b)] = di1
        if di2 is None:
            self._rec[(b, a)] = di1
        else:
            self._rec[(b, a)] = di2

    def distance(self, a: str, b: str) -> int:
        """Return the distance from city a and city b. If this distance is not
        recorded, return -1

        >>> d = DistanceMap()
        >>> d.add_distance('Toronto', 'Vancouver', 1000, 1001)
        >>> print(d.distance('Toronto', 'Vancouver'))
        1000
        >>> print(d.distance('Toronto', 'Hamilton'))
        -1
        >>> d.add_distance('Toronto', 'Hamilton', 900)
        >>> print(d.distance('Toronto', 'Hamilton'))
        900
        """

        if (a, b) in self._rec:
            return self._rec[(a, b)]
        return -1


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': ['doctest', 'python_ta', 'typing'],
        'disable': ['E1136'],
        'max-attributes': 15,
    })
    import doctest
    doctest.testmod()
