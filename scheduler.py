"""Assignment 1 - Scheduling algorithms (Task 4)

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

This module contains the abstract Scheduler class, as well as the two
subclasses RandomScheduler and GreedyScheduler, which implement the two
scheduling algorithms described in the handout.
"""
from typing import List, Dict, Union, Callable
from random import choice
from container import PriorityQueue
from domain import Parcel, Truck


class Scheduler:
    """A scheduler, capable of deciding what parcels go onto which trucks, and
    what route each truck will take.

    This is an abstract class.  Only child classes should be instantiated.
    """

    def schedule(self, parcels: List[Parcel], trucks: List[Truck],
                 verbose: bool = False) -> List[Parcel]:
        """Schedule the given <parcels> onto the given <trucks>, that is, decide
        which parcels will go on which trucks, as well as the route each truck
        will take.

        Mutate the Truck objects in <trucks> so that they store information
        about which parcel objects they will deliver and what route they will
        take.  Do *not* mutate the list <parcels>, or any of the parcel objects
        in that list.

        Return a list containing the parcels that did not get scheduled onto any
        truck, due to lack of capacity.

        If <verbose> is True, print step-by-step details regarding
        the scheduling algorithm as it runs.  This is *only* for debugging
        purposes for your benefit, so the content and format of this
        information is your choice; we will not test your code with <verbose>
        set to True.
        """
        raise NotImplementedError


class RandomScheduler(Scheduler):
    """A Random Scheduler which randomly chooses Parcels, and for each chosen
    parcel, schedules it to a randomly chosen Truck from among those trucks that
    have capacity to add that parcel"""

    def schedule(self, parcels: List[Parcel], trucks: List[Truck],
                 verbose: bool = False) -> List[Parcel]:
        """Schedule the given <parcels> onto the given <trucks> according to
        the rule outlined in the class Docstring.
        for parcel in parcels:

        Mutate the Truck objects in <trucks> so that they store information
        about which parcel objects they will deliver and what route they will
        take.

        Return a list containing the parcels that did not get scheduled onto any
        truck, due to lack of capacity.

        If <verbose> is True, print step-by-step details regarding
        the scheduling algorithm as it runs.
        """

        temp = parcels.copy()
        huge_par = []
        for k in range(len(parcels)):
            parcel = choice(temp)
            temp.remove(parcel)
            good_trucks = []
            for truck in trucks:
                if truck.sum_vol() + parcel.volume <= truck.capacity:
                    good_trucks.append(truck)
            if len(good_trucks) > 0:
                t = choice(good_trucks)
                t.pack(parcel)
                if verbose:
                    i = trucks.index(t)
                    print('Parcel' + str(k) + ' packed to Truck' + str(i))
                    b1 = 'Remaining space in Truck' + str(i) + ' after Parcel'
                    b2 = str(k) + ' is packed = '
                    print(b1 + b2, t.capacity - t.sum_vol())
            else:
                huge_par.append(parcel)
                if verbose:
                    c1 = 'Unable to pack Parcel' + str(k) + ' to any Truck due'
                    print(c1 + ' to lack of capacity')
        return huge_par


class GreedyScheduler(Scheduler):
    """A Scheduler which processes Parcels one at a time, and picks the "best"
    Truck it can for each Parcel. The order in which Parcels are processed, and
    the rule followed in making the choice for a Truck influences what Truck
    is "best" for a given Parcel

    === Private Attributes ===
    _par_func: a function written outside any class that plays a role in
    deciding the order in which Parcels are processed.
    _truck_func: a function written outside any class that, for a given Parcel,
    plays a role in deciding the choice of a suitable Truck to deliver the
    Parcel.
    """
    # Attribute types
    _par_func: Callable[[Parcel, Parcel], bool]
    _truck_func: Callable[[List[Truck]], Union[Truck, None]]

    def __init__(self, config: Dict) -> None:
        """Initialises a new GreedyScheduler
        """
        a = config['parcel_priority']
        b = config['parcel_order']
        c = config['truck_order']
        if a == 'destination' and b == 'non-decreasing':
            self._par_func = _dest_non_dec
        if a == 'destination' and b == 'non-increasing':
            self._par_func = _dest_non_inc
        if a == 'volume' and b == 'non-decreasing':
            self._par_func = _vol_non_dec
        if a == 'volume' and b == 'non-increasing':
            self._par_func = _vol_non_inc
        if c == 'non-decreasing':
            self._truck_func = _truck_non_dec
        if c == 'non-increasing':
            self._truck_func = _truck_non_inc

    def schedule(self, parcels: List[Parcel], trucks: List[Truck],
                 verbose: bool = False) -> List[Parcel]:
        """Schedule the given <parcels> onto the given <trucks>. The order in
        which the Parcels are processed, and the choice of a suitable truck to
        schedule a given Parcel, depend on the arguments passed while creating
        this GreedyScheduler.

        Mutate the Truck objects in <trucks> so that they store information
        about which parcel objects they will deliver and what route they will
        take.  Do *not* mutate the list <parcels>, or any of the parcel objects
        in that list.

        Return a list containing the parcels that did not get scheduled onto any
        truck, due to lack of capacity.

        If <verbose> is True, print step-by-step details regarding
        the scheduling algorithm as it runs.
        """
        if len(trucks) == 0:
            return []

        pq = PriorityQueue(self._par_func)
        huge_par = []
        for parcel in parcels:
            pq.add(parcel)
        while not pq.is_empty():
            par = pq.remove()
            good_trucks = []
            v_good_trucks = []
            for truck in trucks:
                if truck.sum_vol() + par.volume <= truck.capacity:
                    good_trucks.append(truck)
                    truck.very_good_truck(v_good_trucks, par)
            if len(v_good_trucks) > 0:
                good_trucks = v_good_trucks
            if len(good_trucks) > 0:
                a = self._truck_func(good_trucks)
                if verbose:
                    b1 = 'Parcel with volume ' + str(par.volume)
                    b1 += ' and destination ' + par.destination + ' packed to '
                    b1 += 'Truck having unused volume equal to '
                    print(b1, a.capacity - a.sum_vol())
                a.pack(par)
                if verbose:
                    c1 = 'Remaining space in this Truck after the above parcel'
                    print(c1 + ' is packed = ', a.capacity - a.sum_vol())

            else:
                huge_par.append(par)
                if verbose:
                    d1 = 'Unable to pack Parcel with volume ' + str(par.volume)
                    d1 += ' and destination ' + par.destination
                    print(d1 + ' to any truck due to lack of capacity.')

        return huge_par


def _dest_non_dec(parcel_a: Parcel, parcel_b: Parcel) -> bool:
    """Return True if <parcel_a> has a smaller destination (we compare strings)
    than <parcel_b>, False <parcel_a> has a larger destination than <parcel_b>.

    >>> p1 = Parcel(1, 10, 'Toronto', 'Hamilton')
    >>> p2 = Parcel(2, 5, 'London', 'Vancouver')
    >>> _dest_non_dec(p1, p2)
    True
    """
    return parcel_a.destination < parcel_b.destination


def _dest_non_inc(parcel_a: Parcel, parcel_b: Parcel) -> bool:
    """Return True if <parcel_a> has a larger destination (we compare strings)
    than <parcel_b>, False <parcel_a> has a smaller destination than <parcel_b>.

    >>> p1 = Parcel(1, 10, 'Toronto', 'Hamilton')
    >>> p2 = Parcel(2, 5, 'London', 'Vancouver')
    >>> _dest_non_inc(p1, p2)
    False
    """
    return parcel_a.destination > parcel_b.destination


def _vol_non_dec(parcel_a: Parcel, parcel_b: Parcel) -> bool:
    """Return True if <parcel_a> has a smaller volume than <parcel_b>,
    False <parcel_a> has a larger volume than <parcel_b>.

    >>> p1 = Parcel(1, 10, 'Toronto', 'Hamilton')
    >>> p2 = Parcel(2, 5, 'London', 'Vancouver')
    >>> _vol_non_dec(p1, p2)
    False
    """
    return parcel_a.volume < parcel_b.volume


def _vol_non_inc(parcel_a: Parcel, parcel_b: Parcel) -> bool:
    """Return True if <parcel_a> has a larger volume than <parcel_b>,
    False if <parcel_a> has a smaller volume than <parcel_b>.

    >>> p1 = Parcel(1, 10, 'Toronto', 'Hamilton')
    >>> p2 = Parcel(2, 5, 'London', 'Vancouver')
    >>> _vol_non_inc(p1, p2)
    True
    """
    return parcel_a.volume > parcel_b.volume


def _truck_non_dec(spl_list: List[Truck]) -> Union[Truck, None]:
    """Return None if <spl_list> is empty. If <spl_list> is non empty, return
    that Truck of <spl_list> which has the least available space. If there is a
    tie for such a truck, return the Truck which occurs the first in
    <spl_list>.

    >>> t1 = Truck(100, 20, 'Toronto')
    >>> t2 = Truck(200, 10, 'Toronto')
    >>> p1= Parcel(1, 11, 'Toronto', 'Hamilton')
    >>> t1.pack(p1)
    True
    >>> li = [t1, t2]
    >>> _truck_non_dec(li).capacity == 20
    True
    >>> _truck_non_dec(li).capacity - _truck_non_dec(li).sum_vol() == 9
    True
    """
    if len(spl_list) == 0:
        return None
    a = spl_list[0]
    for truck in spl_list:
        a_comp = a.capacity - a.sum_vol()
        truck_comp = truck.capacity - truck.sum_vol()
        if truck_comp < a_comp:
            a = truck
    return a


def _truck_non_inc(spl_list: List[Truck]) -> Union[Truck, None]:
    """Return None if <spl_list> is empty. If <spl_list> is non empty, return
    that Truck of <spl_list> which has the most available space. If there is a
    tie for such a truck, return the Truck which occurs the first in
    <spl_list>.

    >>> t1 = Truck(100, 20, 'Toronto')
    >>> t2 = Truck(200, 10, 'Toronto')
    >>> p1= Parcel(1, 11, 'Toronto', 'Hamilton')
    >>> t1.pack(p1)
    True
    >>> li = [t1, t2]
    >>> _truck_non_inc(li).capacity == 10
    True
    >>> _truck_non_inc(li).sum_vol() == 0
    True
    """
    if len(spl_list) == 0:
        return None
    a = spl_list[0]
    for truck in spl_list:
        a_comp = a.capacity - a.sum_vol()
        truck_comp = truck.capacity - truck.sum_vol()
        if truck_comp > a_comp:
            a = truck

    return a


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'allowed-io': ['compare_algorithms'],
        'allowed-import-modules': ['doctest', 'python_ta', 'typing',
                                   'random', 'container', 'domain'],
        'disable': ['E1136'],
        'max-attributes': 15,
    })
