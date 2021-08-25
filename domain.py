"""Assignment 1 - Domain classes (Task 2)

CSC148, Winter 2021

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, Ian Berlott-Atwell, Jonathan Calver,
Sophia Huynh, Myriam Majedi, and Jaisie Sin.

All of the files in this directory and all subdirectories are:
Copyright (c) 2021 Diane Horton, Ian Berlott-Atwell, Jonathan Calver,
Sophia Huynh, Myriam Majedi, and Jaisie Sin.

===== Module Description =====

This module contains the classes required to represent the entities
in the simulation: Parcel, Truck and Fleet.
"""
from typing import List, Dict
from distance_map import DistanceMap


class Parcel:
    """A Parcel which is to be delivered from its source to its destination.

    === Public Attributes ===
    par_id: the ID of a parcel. Each parcel has a unique id.
    volume: volume of the parcel, measured in units of cubic centimetres (cc).
    source: the name of the city the parcel came from.
    destination: the name of the city where the parcel must be delivered to.
    """
    # Attribute types
    par_id: int
    volume: int
    source: str
    destination: str

    def __init__(self, par_id: int, volume: int, source: str, des: str) -> None:
        """Initialize a new parcel.

        Precondition: volume > 0.

        >>> p1 = Parcel(1234, 20, 'Toronto', 'Vancouver')
        >>> p1.par_id
        1234
        >>> p1.volume
        20
        >>> p1.source
        'Toronto'
        >>> p1.destination
        'Vancouver'
        """

        self.par_id = par_id
        self.source = source
        self.destination = des
        self.volume = volume


class Truck:
    """A Truck which delivers Parcels.

    === Public Attributes ===
    truck_id: the Truck's unique id
    all_parcels: list of all parcels packed in the truck
    capacity: the volume capacity of the Truck
    route: A list which records the route the Truck takes. The Truck's route \
    ends where it starts.

    === Representation invariants ===
    - capacity > 0
    - capacity >= sum of the volumes of all parcels in the Truck >= 0
    - If len(route) >= 2, route[0] = route[-1]. In other words, if a Truck has
    at least one parcel to deliver, then the Truck's route ends where it starts.
    """

    # Attribute types
    truck_id: int
    all_parcels: List[Parcel]
    capacity: int
    route: List[str]

    def __init__(self, t_id: int, vol_cap: int, depot: str) -> None:
        """ Initialize a new Truck

        <depot> is the city from where the Truck starts.

        Precondition: vol_cap > 0.

        >>> t1 = Truck(1000, 100, 'Toronto')
        >>> t1.truck_id
        1000
        >>> t1.route
        ['Toronto']
        >>> t1.capacity
        100
        >>> t1.all_parcels
        []
        """
        self.truck_id = t_id
        self.capacity = vol_cap
        self.route = [depot]
        self.all_parcels = []

    def sum_vol(self) -> int:
        """Return the sum of the volumes of all parcels packed in this truck

        >>> t1 = Truck(1000, 100, 'Toronto')
        >>> t1.sum_vol()
        0
        >>> p1 = Parcel(1, 5, 'Buffalo', 'Hamilton')
        >>> p2 = Parcel(2, 17, 'Toronto', 'Vancouver')
        >>> t1.pack(p1)
        True
        >>> t1.pack(p2)
        True
        >>> t1.sum_vol()
        22
        """
        sum_all = 0
        for par in self.all_parcels:
            sum_all += par.volume

        return sum_all

    def pack(self, parcel: Parcel) -> bool:
        """Return True if parcel can be packed in <self> , false otherwise.

        <parcel> can be packed to this truck if and only if
        the sum of the volumes of all Parcels packed into this truck till now +
        parcel.volume <= self.capacity. If <parcel> can be
        packed to this truck, self.all_parcels and <self>'s route are updated
        because this truck now has to deliver an additional Parcel.

        >>> t1 = Truck(1000, 20, 'Toronto')
        >>> p1 = Parcel(1, 17, 'Buffalo', 'Hamilton')
        >>> t1.pack(p1)
        True
        >>> t1.route
        ['Toronto', 'Hamilton', 'Toronto']
        >>> t1.sum_vol()
        17
        >>> p2 = Parcel(2, 5, 'Toronto', 'Vancouver')
        >>> t1.pack(p2)
        False
        >>> t1.route
        ['Toronto', 'Hamilton', 'Toronto']
        >>> t1.sum_vol()
        17
        """
        sum_all = self.sum_vol()

        if sum_all + parcel.volume <= self.capacity:
            self.all_parcels.append(parcel)
            if len(self.route) == 1:
                self.route.append(parcel.destination)
                self.route.append(self.route[0])
            elif parcel.destination != self.route[-2]:
                self.route.insert(len(self.route) - 1, parcel.destination)
            return True

        return False

    # This method is written to be used in scheduler.py
    def very_good_truck(self, v_list: List, par: Parcel) -> bool:
        """Return True if at least one parcel has already been packed onto
        this Truck, <par>'s destination is at the end of this Truck's
        route, and <self> has sufficient space to pack <par>.
        In this case, append <self> to <v_list>. Return False otherwise
        and do nothing in this case.

        >>> li = []
        >>> t1 = Truck(1423, 100, 'Toronto')
        >>> p1 = Parcel(1, 20, 'London', 'Hamilton')
        >>> t1.pack(p1)
        True
        >>> p2 = Parcel(1, 50, 'Vancouver', 'Hamilton')
        >>> t1.very_good_truck(li, p2)
        True
        >>> li == [t1]
        True
        """
        if len(self.route) == 1:
            return False
        cond = par.destination == self.route[-2]
        if self.sum_vol() + par.volume <= self.capacity and cond:
            v_list.append(self)
            return True

        return False

    def fullness(self) -> float:
        """Return the percentage of this truck's volume capacity that is full

        >>> t1 = Truck(1000, 20, 'Toronto')
        >>> t1.fullness()
        0.0
        >>> p1 = Parcel(1, 15, 'Buffalo', 'Hamilton')
        >>> t1.pack(p1)
        True
        >>> t1.fullness()
        75.0
        """

        return self.sum_vol() * 100 / self.capacity

    def distance(self, dmap: DistanceMap) -> int:
        """Return the total distance travelled by this truck, according to
        distances in <dmap>.

        Precondition: <dmap> contains all distances required to compute the
                      average distance travelled.

        >>> t1 = Truck(1423, 10, 'Toronto')
        >>> p1 = Parcel(1, 5, 'Toronto', 'Hamilton')
        >>> t1.pack(p1)
        True
        >>> p2 = Parcel(2, 5, 'London', 'Vancouver')
        >>> t1.pack(p2)
        True
        >>> d = DistanceMap()
        >>> d.add_distance('Toronto', 'Hamilton', 100)
        >>> d.add_distance('Hamilton', 'Vancouver', 200)
        >>> d.add_distance('Toronto', 'Vancouver', 200)
        >>> t1.distance(d)
        500

        """
        dist = 0
        if len(self.route) > 1:
            for k in range(len(self.route) - 1):
                dist += dmap.distance(self.route[k], self.route[k + 1])
        return dist

    def __str__(self) -> str:
        """Return a string representation of this Truck

        >>> p1 = Parcel(123, 20, 'Toronto', 'Hamilton')
        >>> p2 = Parcel(1234, 30, 'London', 'Vancouver')
        >>> t1 = Truck(132, 50, 'Toronto')
        >>> print(t1)
        Truck ID = 132, Capacity = 50, Depot is Toronto:
        Empty
        >>> t1.pack(p1)
        True
        >>> t1.pack(p2)
        True
        >>> print(t1)
        Truck ID = 132, Capacity = 50, Depot is Toronto:
        Parcel ID = 123, Volume = 20, Destination is Hamilton
        Parcel ID = 1234, Volume = 30, Destination is Vancouver
        """
        s = 'Truck ID = ' + str(self.truck_id) + ', Capacity = '
        s += str(self.capacity) + ', Depot is ' + self.route[0] + ':\n'
        if len(self.all_parcels) == 0:
            return s + 'Empty'
        for k in range(len(self.all_parcels)):
            a = self.all_parcels[k]
            s += 'Parcel ID = ' + str(a.par_id) + ', Volume = ' + str(a.volume)
            s += ', Destination is ' + a.destination + '\n'

        return s.strip()


class Fleet:
    """ A fleet of trucks for making deliveries.

    ===== Public Attributes =====
    trucks:
      List of all Truck objects in this fleet.
    """
    trucks: List[Truck]

    def __init__(self) -> None:
        """Create a Fleet with no trucks.

        >>> f = Fleet()
        >>> f.num_trucks()
        0
        """
        self.trucks = []

    def add_truck(self, truck: Truck) -> None:
        """Add <truck> to this fleet.

        Precondition: No truck with the same ID as <truck> has already been
        added to this Fleet.

        >>> f = Fleet()
        >>> t = Truck(1423, 1000, 'Toronto')
        >>> f.add_truck(t)
        >>> f.num_trucks()
        1
        >>> f.trucks[0].capacity
        1000
        """
        self.trucks.append(truck)

    # We will not test the format of the string that you return -- it is up
    # to you.
    def __str__(self) -> str:
        """Produce a string representation of this fleet
        >>> p1 = Parcel(123, 20, 'Toronto', 'Hamilton')
        >>> p2 = Parcel(1234, 30, 'London', 'Vancouver')
        >>> p3 = Parcel(12345, 40, 'Vancouver', 'London')
        >>> t1 = Truck(132, 50, 'Toronto')
        >>> t1.pack(p1)
        True
        >>> t1.pack(p2)
        True
        >>> t2 = Truck(133, 50, 'Toronto')
        >>> t2.pack(p3)
        True
        >>> t3 = Truck(134, 100, 'Toronto')
        >>> f = Fleet()
        >>> print(f)
        Trucks in this Fleet:
        This Fleet is empty
        >>> f.add_truck(t1)
        >>> f.add_truck(t2)
        >>> f.add_truck(t3)
        >>> print(f)
        Trucks in this Fleet:
        Truck ID = 132, Capacity = 50, Depot is Toronto:
        Parcel ID = 123, Volume = 20, Destination is Hamilton
        Parcel ID = 1234, Volume = 30, Destination is Vancouver
        Truck ID = 133, Capacity = 50, Depot is Toronto:
        Parcel ID = 12345, Volume = 40, Destination is London
        Truck ID = 134, Capacity = 100, Depot is Toronto:
        Empty
        """
        s = 'Trucks in this Fleet:\n'
        if len(self.trucks) == 0:
            return s + 'This Fleet is empty'
        for truck in self.trucks:
            s += truck.__str__() + '\n'

        return s.strip()

    def num_trucks(self) -> int:
        """Return the number of trucks in this fleet.

        >>> f = Fleet()
        >>> t1 = Truck(1423, 10, 'Toronto')
        >>> f.add_truck(t1)
        >>> f.num_trucks()
        1
        """
        return len(self.trucks)

    def num_nonempty_trucks(self) -> int:
        """Return the number of non-empty trucks in this fleet.

        >>> f = Fleet()
        >>> t1 = Truck(1423, 10, 'Toronto')
        >>> f.add_truck(t1)
        >>> p1 = Parcel(1, 5, 'Buffalo', 'Hamilton')
        >>> t1.pack(p1)
        True
        >>> p2 = Parcel(2, 4, 'Toronto', 'Montreal')
        >>> t1.pack(p2)
        True
        >>> t1.fullness() # percent of the truck that's full
        90.0
        >>> t2 = Truck(5912, 20, 'Toronto')
        >>> f.add_truck(t2)
        >>> p3 = Parcel(3, 2, 'New York', 'Windsor')
        >>> t2.pack(p3)
        True
        >>> t2.fullness()
        10.0
        >>> t3 = Truck(1111, 50, 'Toronto')
        >>> f.add_truck(t3)
        >>> f.num_nonempty_trucks()
        2
        """
        count = 0
        for truck in self.trucks:
            if truck.fullness() > 0:
                count += 1

        return count

    def parcel_allocations(self) -> Dict[int, List[int]]:
        """Return a dictionary in which each key is the ID of a truck in this
        fleet and its value is a list of the IDs of the parcels packed onto it,
        in the order in which they were packed.

        >>> f = Fleet() # 10 is the volume capacity of the truck
        >>> t1 = Truck(1423, 10, 'Toronto') # 1423 is the truck's id
        >>> p1 = Parcel(27, 5, 'Toronto', 'Hamilton') # 27 is the parcel's id
        >>> p2 = Parcel(12, 5, 'Toronto', 'Hamilton')
        >>> t1.pack(p1)
        True
        >>> t1.pack(p2)
        True
        >>> t2 = Truck(1333, 10, 'Toronto')
        >>> p3 = Parcel(28, 5, 'Toronto', 'Hamilton')
        >>> t2.pack(p3)
        True
        >>> f.add_truck(t1)
        >>> f.add_truck(t2)
        >>> f.parcel_allocations() == {1423: [27, 12], 1333: [28]}
        True
        """
        di = {}
        for truck in self.trucks:
            list_par = []
            for parcel in truck.all_parcels:
                list_par.append(parcel.par_id)
            di[truck.truck_id] = list_par

        return di

    def total_unused_space(self) -> int:
        """Return the total unused space, summed over all non-empty trucks in
        the fleet.
        If there are no non-empty trucks in the fleet, return 0.

        >>> f = Fleet()
        >>> f.total_unused_space()
        0
        >>> t = Truck(1423, 1000, 'Toronto')
        >>> p = Parcel(1, 5, 'Buffalo', 'Hamilton')
        >>> t.pack(p)
        True
        >>> f.add_truck(t)
        >>> f.total_unused_space()
        995
        """
        sum_unused = 0
        for truck in self.trucks:
            if truck.sum_vol() > 0:
                sum_unused += truck.capacity - truck.sum_vol()

        return sum_unused

    def _total_fullness(self) -> float:
        """Return the sum of truck.fullness() for each non-empty truck in the
        fleet. If there are no non-empty trucks, return 0.

        >>> f = Fleet()
        >>> f._total_fullness() == 0.0
        True
        >>> t = Truck(1423, 10, 'Toronto')
        >>> f.add_truck(t)
        >>> f._total_fullness() == 0.0
        True
        >>> p = Parcel(1, 5, 'Buffalo', 'Hamilton')
        >>> t.pack(p)
        True
        >>> f._total_fullness()
        50.0
        """
        sum_fullness = 0
        for truck in self.trucks:
            if truck.sum_vol() > 0:
                sum_fullness += truck.fullness()

        return sum_fullness

    def average_fullness(self) -> float:
        """Return the average percent fullness of all non-empty trucks in the
        fleet.

        Precondition: At least one truck is non-empty.

        >>> f = Fleet()
        >>> t = Truck(1423, 10, 'Toronto')
        >>> p = Parcel(1, 5, 'Buffalo', 'Hamilton')
        >>> t.pack(p)
        True
        >>> f.add_truck(t)
        >>> f.average_fullness()
        50.0
        """
        return self._total_fullness() / self.num_nonempty_trucks()

    def total_distance_travelled(self, dmap: DistanceMap) -> int:
        """Return the total distance travelled by the trucks in this fleet,
        according to the distances in <dmap>.

        Precondition: <dmap> contains all distances required to compute the
                      average distance travelled.

        >>> f = Fleet()
        >>> t1 = Truck(1423, 10, 'Toronto')
        >>> p1 = Parcel(1, 5, 'Toronto', 'Hamilton')
        >>> t1.pack(p1)
        True
        >>> t2 = Truck(1333, 10, 'Toronto')
        >>> p2 = Parcel(2, 5, 'Toronto', 'Hamilton')
        >>> t2.pack(p2)
        True
        >>> from distance_map import DistanceMap
        >>> m = DistanceMap()
        >>> m.add_distance('Toronto', 'Hamilton', 9)
        >>> f.add_truck(t1)
        >>> f.add_truck(t2)
        >>> f.total_distance_travelled(m)
        36
        """
        tot_dist = 0
        for truck in self.trucks:
            tot_dist += truck.distance(dmap)

        return tot_dist

    def average_distance_travelled(self, dmap: DistanceMap) -> float:
        """Return the average distance travelled by the trucks in this fleet,
        according to the distances in <dmap>.

        Include in the average only trucks that have actually travelled some
        non-zero distance.

        Preconditions:
        - <dmap> contains all distances required to compute the average
          distance travelled.
        - At least one truck has travelled a non-zero distance.

        >>> f = Fleet()
        >>> t1 = Truck(1423, 10, 'Toronto')
        >>> p1 = Parcel(1, 5, 'Toronto', 'Hamilton')
        >>> t1.pack(p1)
        True
        >>> t2 = Truck(1333, 10, 'Toronto')
        >>> p2 = Parcel(2, 5, 'Toronto', 'Hamilton')
        >>> t2.pack(p2)
        True
        >>> from distance_map import DistanceMap
        >>> m = DistanceMap()
        >>> m.add_distance('Toronto', 'Hamilton', 9)
        >>> f.add_truck(t1)
        >>> f.add_truck(t2)
        >>> f.average_distance_travelled(m)
        18.0
        """
        return self.total_distance_travelled(dmap) / self.num_nonempty_trucks()


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': ['doctest', 'python_ta', 'typing',
                                   'distance_map'],
        'disable': ['E1136'],
        'max-attributes': 15,
    })
    import doctest
    doctest.testmod()
