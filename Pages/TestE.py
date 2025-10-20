from typing import Union, Tuple, Callable, List
import numpy as np
import pandas as pd


def make_rate_counters(
        thresh: Union[List[Union[int, float]], Tuple[Union[int, float], ...], np.ndarray],
        cumu: bool = True,
        include_mean: bool = True,
        include_below_min: bool = False,
        include_count_valid: int = 0
) -> Tuple[Callable, ...]:
    """
    根据阈值生成一组成绩区间统计函数（计数 + 比率），可选生成低于最低分统计、平均分函数和有效数据个数统计。

    🎯 核心特性：
      - 直接返回函数组，无需字典包装；
      - 函数名采用数学区间风格：count[60,80)、ratio[60,80)、count[80,+∞)、ratio[80,+∞)；
      - 支持区间统计和累计统计两种模式；
      - 可选生成低于最低分的统计函数（在两种模式下均有效）；
      - 可选生成平均分计算函数（自动忽略NaN值）；
      - 新增：可选生成有效数据个数统计函数（count_valid），位置由 include_count_valid 控制。

    📊 位置控制逻辑：
      - include_count_valid = 0: 不添加 count_valid；
      - include_count_valid = 1: 将 count_valid 添加在函数列表的第一个位置；
      - include_count_valid = -1: 将 count_valid 添加在函数列表的最后一个位置。

    ⚠️ 注意事项：
      - 当 cumu=True 时，区间表示分数 >= 阈值的比例，例如 ratio[80,+∞) 表示 80 分及以上占比。
      - 比率计算时，分母为输入数组的总长度（包括 NaN 值）。若需基于有效数据计算，请先过滤 NaN。

    :param thresh: list/tuple/ndarray，阈值列表，必须是长度 >=2 的升序序列；
    :param cumu: bool，是否为累计统计模式。True 时，每个阈值 t 生成 [t, +∞) 区间统计（即 >=t）。
    :param include_mean: bool, 是否生成计算平均分的函数，默认 True；
    :param include_below_min: bool, 是否生成低于最低分的统计函数，默认 False；
    :param include_count_valid: int, 控制 count_valid 的位置（0=不添加, 1=第一个位置, -1=最后一个位置）；
    :return: tuple，包含所有生成的统计函数。

    :raises ValueError: 当参数不符合要求时；
    :raises TypeError: 当参数类型不正确时。
    """
    # 参数验证。
    if not isinstance(thresh, (list, tuple, np.ndarray)):
        raise TypeError("thresh 必须为列表、元组或 numpy 数组。")

    if isinstance(thresh, np.ndarray):
        thresh = thresh.tolist()

    if len(thresh) < 2:
        raise ValueError("thresh 必须包含至少 2 个元素。")

    for i, t in enumerate(thresh):
        if not isinstance(t, (int, float)):
            raise TypeError(f"thresh 中的所有元素必须是数字类型，但索引 {i} 的元素是 {type(t)}。")

    for i in range(len(thresh) - 1):
        if thresh[i] >= thresh[i + 1]:
            raise ValueError("thresh 必须是严格升序序列。")

    if not isinstance(cumu, bool):
        raise TypeError("cumu 必须是布尔值。")

    if not isinstance(include_below_min, bool):
        raise TypeError("include_below_min 必须是布尔值。")

    if not isinstance(include_mean, bool):
        raise TypeError("include_mean 必须是布尔值。")

    if not isinstance(include_count_valid, int):
        raise TypeError("include_count_valid 必须是整数（0, 1, -1）。")

    if include_count_valid not in [0, 1, -1]:
        raise ValueError("include_count_valid 必须是 0, 1 或 -1。")

    for i, t in enumerate(thresh):
        if t < 0:
            raise ValueError(f"thresh 中的所有元素必须为非负数，但索引 {i} 的元素为 {t}。")

    def make_threshold_func(lower, upper=None, ratio=False, cumu_mode=False, is_last_interval=False, below_min=False):
        """
        内部辅助函数，用于创建阈值相关的统计函数（计数/比率）。
        """

        def func(scores):
            # 处理 pandas Series 对象。
            if isinstance(scores, pd.Series):
                if scores.empty:
                    return np.nan if ratio else 0
                arr = scores.values
            elif not isinstance(scores, (list, tuple, np.ndarray)):
                raise TypeError("输入分数必须是列表、元组或 numpy 数组。")
            else:
                arr = np.array(scores)

            # 尝试将数组转换为 float，以处理混合类型或 NaN
            try:
                arr = arr.astype(float)
            except (ValueError, TypeError):
                raise TypeError("分数数组必须能转换为数值类型。")

            mask = np.zeros(arr.shape, dtype=bool)  # 初始化掩码。

            if below_min:
                mask = arr < lower
            elif cumu_mode:
                # 在 cumu 模式下，is_last_interval 参数不再传入，逻辑简化
                mask = arr >= lower
            else:
                if is_last_interval:
                    mask = (arr >= lower) & (arr <= upper)
                else:
                    mask = (arr >= lower) & (arr < upper)

            count = np.sum(mask)
            total = len(arr)
            return count / total if ratio and total > 0 else int(count)

        # 生成函数名。
        prefix = "ratio" if ratio else "count"
        if below_min:
            func_name = f"{prefix}(-∞,{lower})"
        elif cumu_mode:
            func_name = f"{prefix}[{lower},+∞)"
        else:
            if is_last_interval:
                func_name = f"{prefix}[{lower},{upper}]"
            else:
                func_name = f"{prefix}[{lower},{upper})"
        func.__name__ = func_name
        return func

    def make_mean_func():
        """
        平均分计算函数：自动忽略 NaN 值。
        """

        def func(scores):
            if isinstance(scores, pd.Series):
                arr = scores.values
            elif not isinstance(scores, (list, tuple, np.ndarray)):
                raise TypeError("输入分数必须是列表、元组或 numpy 数组。")
            else:
                arr = np.array(scores)

            # 尝试将数组转换为 float
            try:
                arr = arr.astype(float)
            except (ValueError, TypeError):
                raise TypeError("分数数组必须能转换为数值类型。")

            # 过滤掉 NaN 值。
            valid = arr[~np.isnan(arr)]

            if len(valid) == 0:
                return np.nan

            return float(np.mean(valid))

        func.__name__ = "mean"
        return func

    def make_count_valid_func():
        """
        有效数据个数统计函数。
        """

        def func(scores):
            if isinstance(scores, pd.Series):
                arr = scores.values
            elif not isinstance(scores, (list, tuple, np.ndarray)):
                raise TypeError("输入分数必须是列表、元组或 numpy 数组。")
            else:
                arr = np.array(scores)

            # 尝试将数组转换为 float
            try:
                arr = arr.astype(float)
            except (ValueError, TypeError):
                raise TypeError("分数数组必须能转换为数值类型。")

            # 计算有效数据个数（非 NaN）。
            valid = ~np.isnan(arr)
            return int(np.sum(valid))

        func.__name__ = "count_valid"
        return func

    funcs = []
    n = len(thresh)
    min_thresh = thresh[0]

    # 生成低于最低分的统计。
    if include_below_min:
        below_count_func = make_threshold_func(min_thresh, ratio=False, below_min=True)
        below_ratio_func = make_threshold_func(min_thresh, ratio=True, below_min=True)
        funcs.extend([below_count_func, below_ratio_func])

    # 生成阈值区间统计。
    for i in range(n - 1):
        lower = thresh[i]
        upper = thresh[i + 1]
        is_last_interval = (i == n - 2)

        # 根据 cumu 模式选择调用方式，避免传递无用参数
        if cumu:
            count_func = make_threshold_func(lower, ratio=False, cumu_mode=True)
            ratio_func = make_threshold_func(lower, ratio=True, cumu_mode=True)
        else:
            count_func = make_threshold_func(lower, upper, ratio=False, is_last_interval=is_last_interval)
            ratio_func = make_threshold_func(lower, upper, ratio=True, is_last_interval=is_last_interval)

        funcs.extend([count_func, ratio_func])

    # 生成平均分统计。
    if include_mean:
        mean_func = make_mean_func()
        funcs.append(mean_func)

    # 根据 include_count_valid 添加有效数据个数统计。
    if include_count_valid != 0:
        count_valid_func = make_count_valid_func()
        if include_count_valid == 1:
            funcs.insert(0, count_valid_func)  # 插入到第一个位置。
        elif include_count_valid == -1:
            funcs.append(count_valid_func)  # 插入到最后一个位置。

    return tuple(funcs)


# --- 示例用法 ---
if __name__ == "__main__":
    # 定义阈值
    thresholds = [60, 80, 100]
    print(f"阈值: {thresholds}")
    print(f"累计模式 (cumu=True):")

    # 生成统计函数组
    stat_funcs = make_rate_counters(thresholds, cumu=True, include_mean=True, include_below_min=True,
                                    include_count_valid=-1)

    # 示例数据
    sample_scores = [55, 65, 75, 85, 95, 88, 72, 60, 90, np.nan]
    print(f"示例数据: {sample_scores}")

    # 打印所有生成的函数名称
    print("\n生成的函数列表:")
    for i, func in enumerate(stat_funcs):
        print(f"  [{i:2d}] {func.__name__}")

    print("\n计算示例数据的统计结果:")
    for func in stat_funcs:
        result = func(sample_scores)
        print(f"  {func.__name__}: {result:.4f}" if isinstance(result, float) else f"  {func.__name__}: {result}")

    print("\n" + "=" * 50)
    print(f"非累计模式 (cumu=False):")
    stat_funcs2 = make_rate_counters(thresholds, cumu=False, include_mean=True, include_below_min=True,
                                     include_count_valid=-1)

    print("\n生成的函数列表:")
    for i, func in enumerate(stat_funcs2):
        print(f"  [{i:2d}] {func.__name__}")

    print("\n计算示例数据的统计结果:")
    for func in stat_funcs2:
        result = func(sample_scores)
        print(f"  {func.__name__}: {result:.4f}" if isinstance(result, float) else f"  {func.__name__}: {result}")




