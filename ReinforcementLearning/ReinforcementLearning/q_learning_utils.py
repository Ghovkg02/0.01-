# import time
from ReinforcementLearning import Environment, QLearningAgent

# Hyper-parameters
alpha = 0.1
discount = 0.6
epsilon = 0.1

def save_q_values(path, q_values):
    with open(path, 'w+') as f:
        f.write(str(q_values))

def get_q_values(path):
    q_values_dict = ""
    with open(path, 'r') as f:
        for i in f.readlines():
            q_values_dict = i  # string
    return q_values_dict

def calculate_congestion_density(environment):
    """Calculate congestion density based on the current number of vehicles."""
    current_vehicles = environment.sim.n_vehicles_on_map  # Current number of vehicles
    # Here, we're not using max_capacity. Return current vehicles instead.
    return current_vehicles  # Congestion density is simply the number of vehicles

def update_display(agent, environment):
    """Update the display with average wait time and congestion density."""
    average_wait_time = environment.sim.current_average_wait_time
    congestion_density = calculate_congestion_density(environment)

    print(f"Average Wait Time: {average_wait_time:.2f}, Congestion Density: {congestion_density:.2f}")

def train_agent(agent, environment, path, n_episodes: int, render: bool = False):
    print(f"\n -- Training Q-agent for {n_episodes} episodes  -- ")

    for n_episode in range(1, n_episodes + 1):
        state = environment.reset(render)
        score = 0
        done = False

        while not done:
            action = agent.get_action(state)
            new_state, reward, done, truncated = environment.step(action)
            if truncated:
                exit()
            agent.update(state, action, new_state, reward)
            state = new_state
            score += reward

        # Optionally update display during training
        if n_episode % 100 == 0:  # Adjust frequency as needed
            update_display(agent, environment)

    save_q_values(path, agent.q_values)
    print(" -- Training finished -- ")

def validate_agent(agent, environment, n_episodes: int, render: bool = False):
    print(f"\n -- Evaluating Q-agent for {n_episodes} episodes -- ")
    total_wait_time, total_collisions, n_completed = 0, 0, 0

    for episode in range(1, n_episodes + 1):
        state = environment.reset(render)
        score = 0
        collision_detected = 0
        done = False

        while not done:
            action = agent.get_action(state)
            state, reward, done, truncated = environment.step(action)
            if truncated:
                exit()
            score += reward
            collision_detected += environment.sim.collision_detected

        if collision_detected:
            print(f"Episode {episode} - Collisions: {int(collision_detected)}")
            total_collisions += 1
        else:
            wait_time = environment.sim.current_average_wait_time
            total_wait_time += wait_time
            print(f"Episode {episode} - Wait time: {wait_time:.2f}")

            # Update display for average wait time and congestion density
            update_display(agent, environment)

    n_completed = n_episodes - total_collisions
    print(f"\n -- Results after {n_episodes} episodes: -- ")
    print(f"Average wait time per completed episode: {total_wait_time / n_completed:.2f}")
    print(f"Average collisions per episode: {total_collisions / n_episodes:.2f}")

def q_learning(n_episodes: int, render: bool):
    env: Environment = Environment()
    actions = env.action_space
    q_agent = QLearningAgent(alpha, epsilon, discount, actions)
    n_train_episodes = 10000
    file_name = f"ReinforcementLearning/Traffic_q_values_{n_train_episodes}.txt"
    # train_agent(q_agent, env, file_name, n_train_episodes, render=False)
    q_agent.q_values = eval(get_q_values(file_name))
    validate_agent(q_agent, env, n_episodes, render)
