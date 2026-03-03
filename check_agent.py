# 查看 agent 模块
import inspect
from browser_use.agent import Agent

print("Agent class location:", inspect.getfile(Agent))
print("\nAgent __init__ signature:")
print(inspect.signature(Agent.__init__))
