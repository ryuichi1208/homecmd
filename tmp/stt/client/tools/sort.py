from dataclasses import dataclass

@dataclass
class Sort:
    num: list[int]
    name: str = "Sort"

s = Sort([1, 2, 3])
print(s.num)
print(s.name)
