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
    past_node: str = None


def past_nodes(start_node, end_node):
    start_position = start_node['position']
    end_position = end_node['position']
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


@router.post("/min_path")
async def minPath(params: min_path_params):
    nodes = school_map
    start_node_id = params.start_node
    end_node_id = params.end_node
    past_node_id = params.past_node
    start_node = nodes[start_node_id]
    end_node = nodes[end_node_id]
    result = []
    if past_node_id is not None:
        past_node = nodes[past_node_id]
        for i in past_nodes(start_node, past_node):
            result.append(i)
        result.pop()
        for i in past_nodes(past_node, end_node):
            result.append(i)
    else:
        for i in past_nodes(start_node, end_node):
            result.append(i)
    return result
