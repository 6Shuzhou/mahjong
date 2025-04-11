import random
from tqdm import trange
import math
import matplotlib.pyplot as plt

#########################
#  1. 基础功能函数定义   #
#########################

def generate_wall():
    """
    生成并打乱一副不含花牌的 136 张麻将牌山。
    34 种基本牌（1~9m, 1~9p, 1~9s, 1~7z），每种 4 张。
    """
    suits = ['m', 'p', 's']  # 万/筒/索
    wall = []
    # 1~9 m/p/s，每种4张
    for suit in suits:
        for num in range(1, 10):
            for _ in range(4):
                wall.append(f"{num}{suit}")
    # 字牌 1z ~ 7z，每种4张
    for num in range(1, 8):
        for _ in range(4):
            wall.append(f"{num}z")
    random.shuffle(wall)
    return wall

def is_dalan(hand):
    """
    判断14张牌是否满足“打烂”的和牌形要求。

    规则：
      1. 数牌：格式 "数字+花色"（花色为 m, p, s）
         同一花色下任两张牌数字之差须 >= 3。
      2. 字牌：格式 "数字+z"（数字1~7）
         同一种字牌不允许重复出现。

    参数:
      hand: list[str]，长度为14。

    返回:
      True 如果和牌满足“打烂”条件，
      否则返回 False。
    """
    if len(hand) != 14:
        return False
    
    for i in range(len(hand)):
        for j in range(i + 1, len(hand)):
            tile1 = hand[i]
            tile2 = hand[j]
            # 数牌判断
            if tile1[-1] in 'mps' and tile2[-1] in 'mps':
                # 如果是同花色
                if tile1[-1] == tile2[-1]:
                    n1 = int(tile1[:-1])
                    n2 = int(tile2[:-1])
                    if abs(n1 - n2) < 3:
                        return False
            # 字牌判断
            elif tile1.endswith('z') and tile2.endswith('z'):
                if tile1 == tile2:
                    return False
    return True

def has_7_distinct_honors(hand):
    """
    判断手牌中是否包含7种不同字牌(1z~7z)。
    """
    if len(hand) < 7:
        return False
    honors_in_hand = set(tile for tile in hand if tile.endswith('z'))
    # 看看手牌中的字牌与 {1z,2z,...,7z} 交集的大小
    return len(honors_in_hand.intersection({f"{i}z" for i in range(1,8)})) == 7

def is_dalan_with_7_honors(hand):
    """
    同时判断是否“打烂” + 是否拥有7种不同字牌。
    """
    if len(hand) != 14:
        return False
    return is_dalan(hand) and has_7_distinct_honors(hand)

#########################
#   2. 向听与弃牌策略    #
#########################

def max_non_conflicting(nums):
    """
    给定同花色数牌的数字列表，选出一个尽可能大的子集，
    使得任意相邻两个数字的差值 >=3。返回子集大小。
    (贪心算法)
    """
    if not nums:
        return 0
    nums_sorted = sorted(nums)
    count = 1
    last = nums_sorted[0]
    for n in nums_sorted[1:]:
        if n - last >= 3:
            count += 1
            last = n
    return count

def calculate_dalan_shanten_rough(hand):
    """
    粗略计算一下手牌距离“打烂”还差多少张要改(向听数)。
    
    这里重复使用前面提到的思路：
    1) 数牌：同花色中，用贪心算法选出最大不冲突子集；其余都视作需“修改”。
    2) 字牌：同一种字牌如果出现次数>1，超出的都要“修改”。
    
    返回一个整型，表示需要修改的牌数。
    """
    if len(hand) != 14:
        return 14  # 不合法时随便返回个大值
    
    # 把手牌拆分：万/筒/索/字牌
    suits = {'m': [], 'p': [], 's': []}
    honor_count = {}
    for t in hand:
        if t.endswith('z'):
            honor_count[t] = honor_count.get(t, 0) + 1
        else:
            suit = t[-1]  # m/p/s
            num = int(t[:-1])
            suits[suit].append(num)
    
    modifications = 0
    # 处理数牌
    for s in ['m','p','s']:
        arr = suits[s]
        keep = max_non_conflicting(arr)
        modifications += len(arr) - keep
    
    # 处理字牌
    for tile, cnt in honor_count.items():
        if cnt > 1:
            modifications += (cnt - 1)
    
    return modifications

def missing_honors_count(hand):
    """
    计算手牌距离拥有7种不同字牌还缺多少种。
    """
    all_7 = {f"{i}z" for i in range(1,8)}
    honors_in_hand = set(tile for tile in hand if tile in all_7)
    return max(0, 7 - len(honors_in_hand))

def evaluate_hand_for_discard(hand):
    """
    一个简易评估函数：返回 “打烂向听数” + “缺少的字牌种类数”。
    数值越小，手牌越接近“打烂+7字”目标。
    """
    return calculate_dalan_shanten_rough(hand) + missing_honors_count(hand)

def choose_discard_tile(hand):
    """
    从14张手牌中，尝试丢弃每一张，观察丢后剩下13张的“评估值”；
    最终丢弃能使评估值最小的那张。
    如果有并列，随意丢其中之一即可。
    """
    if len(hand) != 14:
        return None  # 没有可丢的
    
    best_tile = None
    best_eval = math.inf
    for i, tile in enumerate(hand):
        new_hand = hand[:i] + hand[i+1:]
        score = evaluate_hand_for_discard(new_hand)
        if score < best_eval:
            best_eval = score
            best_tile = tile
    return best_tile

#########################
#  3. 主模拟流程：演示   #
#########################

def simulate_dalan_with_7z_rounds(rounds=1):
    """
    进行 rounds 次模拟，每次模拟流程：
    1. 生成随机牌山
    2. 初始手牌13张
    3. 最多摸牌20次，每次：
       - 摸1张 => 14张
       - 若已满足【打烂+7种字牌】，结束
       - 否则弃1张 => 回到13张
    4. 看最终是否成功(14张满足条件)

    返回 (success_count, fail_count)
    """
    success_count = 0
    fail_count = 0
    
    for _ in trange(rounds, desc="模拟中"):
        wall = generate_wall()
        # 初始 13 张
        hand = wall[:13]
        wall_index = 13
        
        # 最多摸 20 张
        for draw_i in range(20):
            # 如果牌山已经不够摸了，也提前结束
            if wall_index >= len(wall):
                break
            # 摸牌
            hand.append(wall[wall_index])
            wall_index += 1
            
            # 判断
            if is_dalan_with_7_honors(hand):
                # 提前成功
                break
            else:
                # 不满足 => 弃一张
                discard = choose_discard_tile(hand)
                if discard is not None:
                    hand.remove(discard)
                else:
                    # 理论上不会出现
                    break
        
        # 循环结束后，最终手牌可能是 14 张，也可能是 13 张(如果牌山耗尽或发生异常)
        # 这里确保判断时要 14 张才有意义
        if len(hand) == 14 and is_dalan_with_7_honors(hand):
            success_count += 1
        else:
            fail_count += 1
    
    return success_count, fail_count

# --- 主调用示例 ---
if __name__ == "__main__":
    rounds = 100000  # 
    success, fail = simulate_dalan_with_7z_rounds(rounds)
    print(f"\n共模拟 {rounds} 次，成功达成 '打烂+7不同字牌' 的次数 = {success}，失败次数 = {fail}")
    print(f"成功率 = {success / rounds:.2%}")
