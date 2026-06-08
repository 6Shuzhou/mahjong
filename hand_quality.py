import random
from collections import Counter
from tqdm import tqdm
import math

def generate_wall():
    """
    生成一副标准136张麻将牌（34种牌，每种4张）。
    数牌: 1~9m, 1~9p, 1~9s
    字牌: 1~7z
    """
    wall = []
    # 数牌
    for suit in ['m', 'p', 's']:
        for num in range(1, 10):
            for _ in range(4):
                wall.append(f"{num}{suit}")
    # 字牌
    for num in range(1, 8):
        for _ in range(4):
            wall.append(f"{num}z")
    return wall

def draw_hand(wall, n=13):
    """从牌山中随机抽取n张牌作为起手"""
    return random.sample(wall, n)

def count_pairs(hand):
    """
    计算手牌中的"对子"数。
    对子的定义：某张牌出现恰好2次记为1对；出现4次记为2对。
    返回对子总数。
    """
    counts = Counter(hand)
    pairs = 0
    for tile, cnt in counts.items():
        pairs += cnt // 2  # 2张=1对, 4张=2对
    return pairs

def has_ankou(hand):
    """判断是否有一个暗刻（某张牌出现恰好3次）"""
    counts = Counter(hand)
    return any(cnt >= 3 for cnt in counts.values())

def has_ankan(hand):
    """判断是否有一个暗杠（某张牌出现恰好4次）"""
    counts = Counter(hand)
    return any(cnt == 4 for cnt in counts.values())

def has_two_ankou(hand):
    """判断起手是否有两个暗刻（至少有两种牌各出现≥3次）"""
    counts = Counter(hand)
    return sum(1 for cnt in counts.values() if cnt >= 3) >= 2

def has_ankou_and_two_pairs(hand):
    """
    判断起手是否有一个暗刻 + 两个对子。
    暗刻：某张牌出现恰好3次
    对子：某张牌出现恰好2次（出现4张的不算对子）
    """
    counts = Counter(hand)
    has_exact_3 = any(cnt == 3 for cnt in counts.values())
    pair_count = sum(1 for cnt in counts.values() if cnt == 2)
    return has_exact_3 and pair_count >= 2

def has_suit_ge_8(hand):
    """判断起手某种花色（万/筒/索）的牌超过7张（≥8张）"""
    suit_counts = {'m': 0, 'p': 0, 's': 0}
    for tile in hand:
        if tile[-1] in suit_counts:
            suit_counts[tile[-1]] += 1
    return any(cnt >= 8 for cnt in suit_counts.values())

def has_5_distinct_honors(hand):
    """起手有5个不相同的字牌"""
    honors = set(tile for tile in hand if tile.endswith('z'))
    return len(honors) >= 5

def has_more_than_5_honors(hand):
    """起手有超过5个字牌（即至少6张字牌）"""
    honor_count = sum(1 for tile in hand if tile.endswith('z'))
    return honor_count > 5

def simulate(n_simulations=1_000_000):
    wall = generate_wall()
    
    stats = {
        '4_pairs': 0,
        '5_pairs': 0,
        'ankan': 0,
        'two_ankou': 0,
        'ankou_and_two_pairs': 0,
        'suit_ge_8': 0,
        '5_distinct_honors': 0,
        'more_than_5_honors': 0,
    }
    
    # 用于统计是否有多个条件同时满足
    any_good = 0
    
    for _ in tqdm(range(n_simulations), desc="模拟起手"):
        hand = draw_hand(wall, 13)
        
        is_4_pairs = count_pairs(hand) == 4
        is_5_pairs = count_pairs(hand) == 5
        is_ankan = has_ankan(hand)
        is_two_ankou = has_two_ankou(hand)
        is_ankou_and_two_pairs = has_ankou_and_two_pairs(hand)
        is_suit_ge_8 = has_suit_ge_8(hand)
        is_5_honors = has_5_distinct_honors(hand)
        is_6_plus_honors = has_more_than_5_honors(hand)
        
        if is_4_pairs:
            stats['4_pairs'] += 1
        if is_5_pairs:
            stats['5_pairs'] += 1
        if is_ankan:
            stats['ankan'] += 1
        if is_two_ankou:
            stats['two_ankou'] += 1
        if is_ankou_and_two_pairs:
            stats['ankou_and_two_pairs'] += 1
        if is_suit_ge_8:
            stats['suit_ge_8'] += 1
        if is_5_honors:
            stats['5_distinct_honors'] += 1
        if is_6_plus_honors:
            stats['more_than_5_honors'] += 1
            
        if any([is_4_pairs, is_5_pairs, is_ankan, is_two_ankou, is_ankou_and_two_pairs, is_suit_ge_8, is_5_honors, is_6_plus_honors]):
            any_good += 1
    
    print(f"\n{'='*60}")
    print(f"模拟次数: {n_simulations:,}")
    print(f"{'='*60}")
    print(f"1. 起手恰好4对:            {stats['4_pairs']:,} 次, 概率 = {stats['4_pairs']/n_simulations:.4%}")
    print(f"2. 起手恰好5对:            {stats['5_pairs']:,} 次, 概率 = {stats['5_pairs']/n_simulations:.4%}")
    print(f"3. 起手有一个暗杠:         {stats['ankan']:,} 次, 概率 = {stats['ankan']/n_simulations:.4%}")
    print(f"4. 起手有两个暗刻:         {stats['two_ankou']:,} 次, 概率 = {stats['two_ankou']/n_simulations:.4%}")
    print(f"5. 起手一个暗刻加两个对子: {stats['ankou_and_two_pairs']:,} 次, 概率 = {stats['ankou_and_two_pairs']/n_simulations:.4%}")
    print(f"6. 起手某种花色≥8张:       {stats['suit_ge_8']:,} 次, 概率 = {stats['suit_ge_8']/n_simulations:.4%}")
    print(f"7. 起手有5个不同字牌:      {stats['5_distinct_honors']:,} 次, 概率 = {stats['5_distinct_honors']/n_simulations:.4%}")
    print(f"8. 起手有超过5个字牌:      {stats['more_than_5_honors']:,} 次, 概率 = {stats['more_than_5_honors']/n_simulations:.4%}")
    print(f"{'-'*60}")
    print(f"至少满足一个条件:          {any_good:,} 次, 概率 = {any_good/n_simulations:.4%}")
    print(f"不满足任何条件:            {n_simulations - any_good:,} 次, 概率 = {(n_simulations - any_good)/n_simulations:.4%}")
    
    return stats

if __name__ == "__main__":
    simulate(1_000_000)
