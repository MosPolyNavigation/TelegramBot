import selenium
from selenium import webdriver
from graph_data import Vertexes
from direction_services import *

chrome_options = selenium.webdriver.ChromeOptions()
chrome_options.add_argument('headless')
driver = selenium.webdriver.Chrome(options = chrome_options)

def get_route(from_point: str, to_point: str):
    driver.get('https://mospolynavigation.github.io/nav2/')
    command = f'return graph.getShortestWayFromTo("{from_point}","{to_point}")'
    try:
        res = driver.execute_script(command)
        return res['way']
    except:
        return False



def tell_route(from_p: str, to_p: str):
    way = get_route(from_p, to_p)
    if not way:
        return False
    cur_pos = way[0]
    x1, x2, y1, y2 = Vertexes[way[0]]['x'], Vertexes[way[1]]['x'], Vertexes[way[0]]['y'], Vertexes[way[1]]['y']
    t = Turtle(cur_pos, x2, y2)
    route_list = []
    for node in way[1:]:
        res = t.set_transition(node)
        hallways_neighbor_amount = count_neighbour_hallways(Vertexes[node])
        if res == 'l':
            route_list.append('tl')
        elif res == 'r':
            route_list.append('tr')
        elif res == 'f' and route_list:
            if hallways_neighbor_amount == 4:
                route_list.append('gfs')
            else:
                route_list.append('gf')

    return route_list




if __name__ == '__main__':
    while True:
        print("Enter the FROM point")
        from_p = input()
        print("Enter the TO point")
        to_p = input()
        res = tell_route(from_p, to_p)
        if res:
            print(res)





