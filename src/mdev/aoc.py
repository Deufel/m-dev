import httpx
import re
from bs4 import BeautifulSoup
from datetime import datetime

__SESSION = '53616c7465645f5f0965ef9f79dc215fe8cd1bf4ef464da8d883e9a9e1e5f5ef13032a2e880273d6ab7fa9002f52d7300dfc24607bc35c7181e1ab0701fc8ace'

def build_url(d: int | str=None, y: int | str=None, data: bool=False, part_two: bool=False) -> str:
    """
    Args:
        d (int | str) (default: None): day
        y (int | str) (default: None): year
        data (bool) (default: False): true to append /input
        part_two (bool) (default: False): true to append #part2

    Returns:
        str: aoc url

    """
    d = d or str(datetime.now().day)
    y = y or str(datetime.now().year)
    url=f"https://adventofcode.com/{y}/day/{d}"
    url+="/input" * data
    url+="#part2" * part_two
    return(url)

def get_data(d=None, y=None, s=__SESSION) -> str:
    """
    Args:
        d (default: None): day
        y (default: None): year
        s (default: __SESSION): __SESSION from AOC (f12->aplication->cookies)

    Returns:
        str: aoc data

    """
    url = build_url(d,y,data=True)
    c = {'session': __SESSION}
    r = httpx.get(url, cookies=c)
    return r.text

def str2int() -> list:
    """
    Returns:
        list: returns a list of integers with some replacements

    """
    data = get_data(1,2025).replace("R", "").replace("L", "-")
    l = [int(x) for x in data.splitlines()]
    return l

def count_100s() -> int:
    """
    Returns:
        int: number of times dial lands on 0/100

    """
    l = str2int()
    pos=50
    count=0
    for r in l:
        pos+=r
        count+=1 if pos % 100 == 0 else 0
    return count

def count_100_passes() -> int:
    """
    Returns:
        int: number of times dial lands on 0/100

    """
    l = str2int()
    pos_0 = 50
    count = 0
    for r in l:
        pos_r = pos_0 + r
        step = 1 if r > 0 else -1
        for i in range(pos_0, pos_r, step):
            count += 1 if i % 100 == 0 else 0
        pos_0 = pos_r
    return count
