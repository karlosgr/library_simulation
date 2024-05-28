"""
    This module implements a simulation of a queue problem in a library 
"""

from queue import PriorityQueue, Queue
from enum import Enum, auto
import numpy as np


class EventType(Enum):
    """
    Represents the type of an event in the simulation.

    Attributes:
        ARRIVE: Represents an arrival event.
        FINISH: Represents a finish event.
    """

    ARRIVE = auto()
    FINISH = auto()


class LibSimulation:
    """
    A class that represents a library simulation.

    Arguments:
    - time (int): The total simulation time in hours.
    - person_mean_delay (int): The mean delay between person arrivals in minutes.
    - service_mean_delay (int): The mean delay for serving a person in minutes.

    Methods:
    - simulate(self, days=100): Simulates the library operation for a given number of days.
    - simulate_day(self): Simulates a day in the library.
    """

    def __init__(self, time, person_mean_delay, service_mean_delay) -> None:
        self.time = int(time * 3600)
        self._person_delay = int(person_mean_delay * 60)
        self._service_delay = int(service_mean_delay * 60)

    def simulate(self, days=100):
        """
        Simulates the library operation for a given number of iterations.

        Parameters:
        - iter_count (int): The number of iterations to run the simulation (default: 100).

        Returns:
        - Tuple[float, float, float]: A tuple containing the mean values of people's awaiting time,
            line length, and number of articles across all iterations.
        """
        people_await_time: list[int] = []
        line_length: list[float] = []
        articles: list[int] = []

        for _ in range(days):
            day_line_length, day_articles, day_awaiting_time_mean = self.simulate_day()
            people_await_time.append(day_awaiting_time_mean)
            line_length.append(day_line_length)
            articles.append(day_articles)

        return np.mean(people_await_time), np.mean(line_length), np.mean(articles)

    def simulate_day(self):
        """
        Simulates a day in the library.

        Returns:
            number_waiting_persons_in_time (dict[int, int]): A dictionary mapping -
            the number of waiting persons to the time they spent waiting.
            total_free_time (int): The total time the worker was free.
            people_awaiting_time (list[int]): A list of the waiting times for each person.
        """
        people_awaiting_time: list[int] = []
        free_worker: bool = True
        actual_time: int = 0
        total_articles: int = 0
        waiting_persons: Queue = Queue()
        events: PriorityQueue = self._generate_arrives()
        number_waiting_persons_in_time: dict[int, int] = {}

        while not events.empty():
            event = events.get()

            transcur_time = event[0] - actual_time

            actual_time = event[0]

            waiting_person_count = waiting_persons.qsize()

            if free_worker:
                total_articles += (transcur_time * 22) // 3600

            if waiting_person_count in number_waiting_persons_in_time:
                number_waiting_persons_in_time[waiting_person_count] += transcur_time
            else:
                number_waiting_persons_in_time[waiting_person_count] = transcur_time

            if event[1] is EventType.ARRIVE:
                waiting_persons.put((event[0]))

            if event[1] is EventType.FINISH:
                free_worker = True

            if free_worker:
                if not waiting_persons.empty():
                    person = waiting_persons.get()
                    people_awaiting_time.append(actual_time - person)
                    events.put(
                        (
                            np.random.exponential(self._service_delay) + actual_time,
                            EventType.FINISH,
                        )
                    )
                    free_worker = False

        sum_t: float = 0.0

        for i, time in number_waiting_persons_in_time.items():
            sum_t += i * time

        return sum_t / actual_time, total_articles, np.mean(people_awaiting_time)

    def _generate_arrives(self) -> PriorityQueue:
        actual_time = np.random.poisson(self._person_delay)
        arrives = PriorityQueue()

        while actual_time < self.time:
            arrives.put((actual_time, EventType.ARRIVE))
            actual_time += np.random.poisson(self._person_delay)

        return arrives
