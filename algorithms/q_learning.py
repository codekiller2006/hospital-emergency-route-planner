"""
Role 3: Reinforcement Learning Route Planner (Q-Learning)

Fulfills the "compare at least two AI approaches" rubric requirement by
providing a Q-Learning based alternative to Role 2's A* search.
"""

import time
import random
from collections import defaultdict
import networkx as nx

class QLearningRouter:
    """
    Q-Learning based dynamic router over a NetworkX/OSMnx MultiDiGraph.
    """

    def __init__(
        self,
        graph,
        alpha=0.2,          # learning rate
        gamma=0.9,          # discount factor
        epsilon=0.3,        # exploration rate (decays over training)
        epsilon_decay=0.995,
        min_epsilon=0.05,
        episodes=500,
        max_steps_per_episode=200,
        traffic_penalty=500.0,   # extra cost (seconds) added when hitting a jam
        seed=None,
    ):
        self.graph = graph
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self.episodes = episodes
        self.max_steps_per_episode = max_steps_per_episode
        self.traffic_penalty = traffic_penalty

        if seed is not None:
            random.seed(seed)

        self.Q = defaultdict(lambda: defaultdict(float))

    def _neighbors(self, node):
        return list(self.graph.successors(node)) if self.graph.is_directed() \
            else list(self.graph.neighbors(node))

    def _edge_data(self, u, v):
        edge_dict = self.graph.get_edge_data(u, v)
        if edge_dict is None:
            return None
        if all(isinstance(k, int) for k in edge_dict.keys()):
            best = min(
                edge_dict.values(),
                key=lambda d: d.get("travel_time", d.get("length", 1.0)),
            )
            return best
        return edge_dict

    def _step_cost_and_reward(self, u, v):
        data = self._edge_data(u, v)
        if data is None:
            return float("inf"), -1e6

        base_cost = data.get("travel_time", data.get("length", 1.0))
        is_jam = bool(data.get("is_traffic_jam", False))

        cost = base_cost + (self.traffic_penalty if is_jam else 0.0)
        reward = -cost 

        return cost, reward

    def train(self, start, goal):
        goal_reward = 1000.0 

        for episode in range(self.episodes):
            state = start
            visited_this_episode = {state}

            for _ in range(self.max_steps_per_episode):
                actions = self._neighbors(state)
                if not actions:
                    break 

                if random.random() < self.epsilon:
                    action = random.choice(actions)
                else:
                    q_values = self.Q[state]
                    unexplored = [a for a in actions if a not in q_values]
                    if unexplored and random.random() < 0.5:
                        action = random.choice(unexplored)
                    else:
                        action = max(actions, key=lambda a: q_values.get(a, 0.0))

                next_state = action
                _, reward = self._step_cost_and_reward(state, next_state)

                if next_state == goal:
                    reward += goal_reward

                if next_state in visited_this_episode:
                    reward -= 50.0

                best_next_q = max(
                    self.Q[next_state].values(), default=0.0
                )
                td_target = reward + self.gamma * best_next_q
                td_error = td_target - self.Q[state][action]
                self.Q[state][action] += self.alpha * td_error

                visited_this_episode.add(next_state)
                state = next_state

                if state == goal:
                    break

            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    def extract_path(self, start, goal, max_steps=500):
        path = [start]
        state = start
        total_time = 0.0
        total_distance = 0.0
        visited = {start}

        for _ in range(max_steps):
            if state == goal:
                return path, total_time, total_distance

            actions = self._neighbors(state)
            if not actions:
                break

            q_values = self.Q[state]
            candidates = [a for a in actions if a not in visited] or actions
            action = max(candidates, key=lambda a: q_values.get(a, float("-inf")))

            data = self._edge_data(state, action)
            cost, _ = self._step_cost_and_reward(state, action)
            total_time += cost
            total_distance += data.get("length", 0.0) if data else 0.0

            path.append(action)
            visited.add(action)
            state = action

        if state == goal:
            return path, total_time, total_distance
        return None, float("inf"), float("inf")

    def plan_route(self, start_node, end_node):
        start_clock = time.perf_counter()

        if start_node == end_node:
            return {
                "path": [start_node],
                "execution_time": time.perf_counter() - start_clock,
                "travel_time": 0.0,
                "distance": 0.0,
            }

        if not nx.has_path(self.graph, start_node, end_node):
            return {
                "path": [],
                "execution_time": time.perf_counter() - start_clock,
                "travel_time": float("inf"),
                "distance": float("inf"),
            }

        self.train(start_node, end_node)
        node_path, travel_time, distance = self.extract_path(start_node, end_node)

        execution_time = time.perf_counter() - start_clock

        return {
            "path": node_path if node_path else [],
            "execution_time": execution_time,
            "travel_time": travel_time,
            "distance": distance,
        }