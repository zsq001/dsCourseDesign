from fastapi import APIRouter
from pydantic import BaseModel
from collections import deque

import json

router = APIRouter(prefix="/map", tags=["maps"])



# 读取school_map.json文件
with open('school_map.json') as file:
    school_map = json.load(file)

class min_path_params(BaseModel):
    start_node: str
    end_node: str


def find_shortest_path(nodes, start_node_id, end_node_id):
    """
    寻找任意两个节点之间的最短路径，并返回经过的所有节点和对应的坐标
    """
    # 获取起始节点和目标节点的坐标
    start_node = nodes[start_node_id]
    end_node = nodes[end_node_id]
    start_position = start_node['position']
    end_position = end_node['position']

    # 创建队列和访问列表，用于BFS
    queue = deque([(start_node_id, [start_node_id])])
    visited = set()

    # 用于保存经过的所有节点坐标
    path_positions = [start_position]

    while queue:
        node_id, path = queue.popleft()
        node = nodes[node_id]
        node_position = node['position']

        if node_id == end_node_id:
            # 找到目标节点，返回路径和节点坐标
            return path, path_positions

        if node_id not in visited:
            visited.add(node_id)

            # 遍历节点的邻居节点
            for neighbor_id, neighbor in nodes.items():
                if neighbor_id != node_id and neighbor_id not in visited:
                    neighbor_position = neighbor['position']

                    # 判断邻居节点是否可以通过横竖移动到达，并将其加入队列
                    if (abs(neighbor_position[0] - node_position[0]) +
                            abs(neighbor_position[1] - node_position[1])) == 1:
                        queue.append((neighbor_id, path + [neighbor_id]))

                        # 将邻居节点的坐标添加到列表中
                        path_positions.append(neighbor_position)



@router.post("/min_path")
async def minPath(params: min_path_params):
    nodes = school_map
    start_node_id = params.start_node
    end_node_id = params.end_node
    start_node = nodes[start_node_id]
    end_node = nodes[end_node_id]
    start_position = start_node['position']
    end_position = end_node['position']
    print(start_node['position'])
    print(start_position)
    result = []
    result.append(start_position.copy())  # 创建一个新的列表对象来存储坐标
    while start_position != end_position:
        if start_position[0] == end_position[0]:
            if start_position[1] > end_position[1]:
                start_position = [start_position[0], start_position[1] - 1]  # 创建新的坐标列表
                result.append(start_position.copy())  # 添加新的坐标到result列表
            else:
                start_position = [start_position[0], start_position[1] + 1]  # 创建新的坐标列表
                result.append(start_position.copy())  # 添加新的坐标到result列表
        else:
            if start_position[0] > end_position[0]:
                start_position = [start_position[0] - 1, start_position[1]]  # 创建新的坐标列表
                result.append(start_position.copy())  # 添加新的坐标到result列表
            else:
                start_position = [start_position[0] + 1, start_position[1]]  # 创建新的坐标列表
                result.append(start_position.copy())  # 添加新的坐标到result列表
    return result
