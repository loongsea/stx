#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def demo_naming_problem():
    """演示为什么不能只用 __name__ 作为字典键"""
    
    # 模拟只使用 __name__ 的情况
    def create_func_with_display_name_only():
        def func(scores):
            return len([s for s in scores if s >= 60])
        
        func.__name__ = "count[60,+)"  # 包含特殊字符的名字
        return func
    
    # 尝试用 __name__ 作为字典键
    f = create_func_with_display_name_only()
    funcs = {}
    
    print("=== 问题演示 ===")
    print(f"函数的 __name__: {f.__name__}")
    print(f"是否为有效的Python标识符: {f.__name__.isidentifier()}")
    
    # 用 __name__ 作为字典键
    funcs[f.__name__] = f
    print(f"字典键: {list(funcs.keys())}")
    
    # 尝试访问 - 这样可以工作
    result = funcs["count[60,+)"]([55, 65, 75])
    print(f"通过字符串键访问结果: {result}")
    
    # 但是无法通过属性访问！
    print("\n=== 无法实现的功能 ===")
    print("# 以下代码会报错，因为包含特殊字符:")
    print("# funcs.count[60,+)  # SyntaxError!")
    print("# getattr(funcs, 'count[60,+)')  # 也不行")
    
    try:
        # 这会失败
        getattr(funcs, f.__name__)
    except Exception as e:
        print(f"getattr 失败: {e}")

def demo_current_solution():
    """演示当前双重命名方案的优势"""
    
    def create_func_with_dual_naming():
        def func(scores):
            return len([s for s in scores if s >= 60])
        
        func.__name__ = "count[60,+)"      # 显示用
        func.safe_name = "ge60_count"      # 字典键用
        return func
    
    f = create_func_with_dual_naming()
    funcs = {}
    
    print("\n=== 当前方案的优势 ===")
    print(f"显示名称: {f.__name__}")
    print(f"安全名称: {f.safe_name}")
    print(f"安全名称是否为有效标识符: {f.safe_name.isidentifier()}")
    
    # 使用安全名称作为字典键
    funcs[f.safe_name] = f
    print(f"字典键: {list(funcs.keys())}")
    
    # 可以安全访问
    result = funcs["ge60_count"]([55, 65, 75])
    print(f"通过安全键访问结果: {result}")
    
    # 也可以通过 getattr 访问 (如果 funcs 是对象的话)
    print(f"getattr 可以工作: {getattr(f, 'safe_name')}")
    
    print("\n=== 打印时的美观效果 ===")
    print(f"函数显示: {f.__name__} -> 结果: {f([55, 65, 75])}")

if __name__ == "__main__":
    demo_naming_problem()
    demo_current_solution()