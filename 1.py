import random
from tqdm import tqdm
import matplotlib.pyplot as plt

def is_dalan(hand):
    """
    判断14张牌是否满足“打烂”的和牌形要求。

    规则：
      1. 数牌：格式为 "数字+花色"（花色为 m, p, s），
         同一花色下任两张牌数字之差须 >= 3。
      2. 字牌：格式为 "数字+z"（数字1-7），
         同一牌不允许重复出现。

    参数:
      hand: list[str]，长度为14，每张牌用字符串表示。
    
    返回:
      True 如果和牌满足“打烂”条件，
      否则返回 False。
    """
    if len(hand) != 14:
        raise ValueError("和牌必须为14张牌")
    
    for i in range(len(hand)):
        for j in range(i + 1, len(hand)):
            tile1 = hand[i]
            tile2 = hand[j]
            # 数牌判断：牌面长度>=2 且最后一个字符不是'z'
            if len(tile1) >= 2 and tile1[-1] != 'z' and len(tile2) >= 2 and tile2[-1] != 'z':
                if tile1[-1] == tile2[-1]:
                    num1 = int(tile1[:-1])
                    num2 = int(tile2[:-1])
                    if abs(num1 - num2) < 3:
                        return False
            # 字牌判断：牌面以'z'结尾
            elif tile1.endswith('z') and tile2.endswith('z'):
                if tile1 == tile2:
                    return False
    return True

def max_non_conflicting(nums):
    """
    给定一个数字列表，选出一个尽可能大的子集，
    使得任意相邻两个数字差值>=3，采用贪心算法。
    """
    if not nums:
        return 0
    nums_sorted = sorted(nums)
    count = 1  # 保留第一个数字
    last = nums_sorted[0]
    for num in nums_sorted[1:]:
        if num - last >= 3:
            count += 1
            last = num
    return count

def calculate_shanten(hand):
    """
    计算手牌调整成“打烂”和牌型所需要的最小修改牌数，即向听数。

    思路：
      1. 对每种花色（数牌）：
         - 求该花色所有牌的数字列表；
         - 使用贪心算法求该列表中最大不冲突（数字间隔>=3）的子集大小；
         - 修改数 = 总牌数 - 保留数
      2. 对字牌：
         - 分别统计“1z”到“7z”的出现次数；
         - 对于出现次数大于1的，每种需要修改 count - 1 张。

    返回:
      整手牌的向听数（需要修改的牌数）。
    """
    if len(hand) != 14:
        raise ValueError("和牌必须为14张牌")
    
    modifications = 0

    # 分组：数牌与字牌
    suits = {'m': [], 'p': [], 's': []}
    honors = []  # 保存所有以'z'结尾的字牌

    for tile in hand:
        if tile.endswith('z'):
            honors.append(tile)
        else:
            suit = tile[-1]
            try:
                num = int(tile[:-1])
            except ValueError:
                continue  # 忽略格式不正确的牌
            if suit in suits:
                suits[suit].append(num)
    
    # 数牌处理：对每个花色计算最少修改数
    for suit, numbers in suits.items():
        count = len(numbers)
        keep = max_non_conflicting(numbers)
        modifications += (count - keep)
    
    # 字牌处理：统计重复情况
    honor_count = {}
    for tile in honors:
        honor_count[tile] = honor_count.get(tile, 0) + 1
    for tile, count in honor_count.items():
        if count > 1:
            modifications += (count - 1)
    
    return modifications

def tile_sort_key(tile):
    """
    定义牌的排序规则：
      - 数牌（末尾不为 'z'）先按花色顺序（m -> p -> s），再按数字大小排序
      - 字牌（末尾为 'z'）统一放在后面，按数字大小排序
    """
    if tile.endswith('z'):
        # 字牌排后面
        return (1, int(tile[:-1]))
    else:
        suit_order = {'m': 0, 'p': 1, 's': 2}
        return (0, suit_order.get(tile[-1], 99), int(tile[:-1]))

# 定义牌池：数牌（m, p, s）和字牌（z）
number_tiles = [f"{num}{suit}" for suit in ['m', 'p', 's'] for num in range(1, 10)]
honor_tiles = [f"{num}z" for num in range(1, 8)]
all_tiles = number_tiles + honor_tiles

def generate_sorted_hand():
    """ 随机生成14张牌并排序返回 """
    hand = [random.choice(all_tiles) for _ in range(14)]
    return sorted(hand, key=tile_sort_key)

# 模拟次数
simulations = 1_000_000

# 向听数统计字典：键为向听数，值为出现次数
shanten_distribution = {}

total_shanten = 0  # 用于累加所有模拟的向听数

# tqdm 显示进度条
for _ in tqdm(range(simulations), desc="模拟中"):
    hand = generate_sorted_hand()
    shanten = calculate_shanten(hand)
    total_shanten += shanten
    shanten_distribution[shanten] = shanten_distribution.get(shanten, 0) + 1

# 计算平均向听数（保留一位小数）
avg_shanten = total_shanten / simulations
print(f"\n平均向听数：{avg_shanten:.1f}")

# 将分布结果按向听数从小到大排序打印
sorted_distribution = sorted(shanten_distribution.items(), key=lambda x: x[0])
print("向听数分布情况：")
for shanten, count in sorted_distribution:
    print(f"向听 {shanten}: {count} 次，占比 {count / simulations:.2%}")

# 绘制直方图展示向听数分布
x_vals = [item[0] for item in sorted_distribution]
y_vals = [item[1] for item in sorted_distribution]

plt.bar(x_vals, y_vals, align='center', edgecolor='black')
plt.xlabel("broken tiles shanten number")
plt.ylabel("count")
plt.title("100 million hands shanten distribution")
plt.xticks(x_vals)
plt.show()
