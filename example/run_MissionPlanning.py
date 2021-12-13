#!/usr/bin/env python3
import time
import matplotlib.pyplot as plt
import pathmagic
with pathmagic.context():
    from Simulator import Simulator
    import DrMaMP


if __name__ == "__main__":
    # define the world
    map_width_meter = 25.0
    map_height_meter = 25.0
    map_resolution = 2
    value_non_obs = 0  # the cell is empty
    value_obs = 255  # the cell is blocked
    # create a simulator
    MySimulator = Simulator(map_width_meter, map_height_meter, map_resolution, value_non_obs, value_obs)
    # number of obstacles
    num_obs = 120
    # [width, length] size of each obstacle [meter]
    size_obs = [1, 1]
    # generate random obstacles
    MySimulator.generate_random_obs(num_obs, size_obs)
    # convert 2D numpy array to 1D list
    world_map = MySimulator.map_array.flatten().tolist()

    # This is for an agent and a set of targets
    num_agents = 3
    num_targets = 12
    agent_position, targets_position = MySimulator.generate_agents_and_targets(num_agents, num_targets)

    # parameters for k-means
    num_cluster = num_agents
    number_of_iterations = 300

    t0 = time.time()
    # solve it
    path_all_agents, task_allocation_all_agents, cluster_centers, points_idx_for_clusters, cluster_assigned_idx\
        = DrMaMP.MissionPlanning(agent_position, targets_position, num_cluster,
                                      number_of_iterations, world_map, MySimulator.map_width,
                                      MySimulator.map_height)
    t1 = time.time()
    print("Time used [sec]:" + str(t1 - t0))

    print("path_all_agents")
    print(path_all_agents)
    print("task_allocation_all_agents")
    print(task_allocation_all_agents)
    print("cluster_centers")
    print(cluster_centers)
    print("points_idx_for_clusters")
    print(points_idx_for_clusters)
    print("cluster_assigned_idx")
    print(cluster_assigned_idx)

    # visualization
    MySimulator.plot_path_multi_agent(path_all_agents, agent_position, targets_position, task_allocation_all_agents, cluster_centers, points_idx_for_clusters)
    MySimulator.plot_cluster_assign(agent_position, targets_position, points_idx_for_clusters, cluster_centers, cluster_assigned_idx)
    plt.show()
