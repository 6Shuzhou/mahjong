import random
from itertools import combinations
from tqdm import tqdm

NUM_TILES = 34
COPIES = 4
YAOCHU = frozenset({0, 8, 9, 17, 18, 26, 27, 28, 29, 30, 31, 32, 33})

# 东南西北的所有顺子组合
WIND_SHUNTSU = list(combinations([27, 28, 29, 30], 3))
DRAGON_SHUNTSU = [(31, 32, 33)]

# 是否启用特殊字牌顺子规则
USE_SPECIAL_WIND = True


def hand_to_counts(hand):
    c = [0] * NUM_TILES
    for t in hand:
        c[t] += 1
    return c


def _can_form_sets(cnt, i=0, formed=0):
    if formed == 4:
        return all(x == 0 for x in cnt)
    if i >= NUM_TILES:
        return False
    if cnt[i] == 0:
        return _can_form_sets(cnt, i + 1, formed)

    # 刻子
    if cnt[i] >= 3:
        cnt[i] -= 3
        if _can_form_sets(cnt, i, formed + 1):
            cnt[i] += 3
            return True
        cnt[i] += 3

    # 数牌顺子
    if i < 27 and i % 9 <= 6 and cnt[i + 1] and cnt[i + 2]:
        cnt[i] -= 1
        cnt[i + 1] -= 1
        cnt[i + 2] -= 1
        if _can_form_sets(cnt, i, formed + 1):
            cnt[i] += 1
            cnt[i + 1] += 1
            cnt[i + 2] += 1
            return True
        cnt[i] += 1
        cnt[i + 1] += 1
        cnt[i + 2] += 1

    # 字牌顺子（特殊规则）
    if USE_SPECIAL_WIND:
        if 27 <= i <= 30:
            for combo in WIND_SHUNTSU:
                if i in combo and all(cnt[c] > 0 for c in combo):
                    for c in combo:
                        cnt[c] -= 1
                    if _can_form_sets(cnt, i, formed + 1):
                        for c in combo:
                            cnt[c] += 1
                        return True
                    for c in combo:
                        cnt[c] += 1

        if 31 <= i <= 33 and cnt[31] and cnt[32] and cnt[33]:
            cnt[31] -= 1
            cnt[32] -= 1
            cnt[33] -= 1
            if _can_form_sets(cnt, i, formed + 1):
                cnt[31] += 1
                cnt[32] += 1
                cnt[33] += 1
                return True
            cnt[31] += 1
            cnt[32] += 1
            cnt[33] += 1

    return False


def is_normal_agari(cnt):
    for i in range(NUM_TILES):
        if cnt[i] >= 2:
            cnt[i] -= 2
            if _can_form_sets(cnt, 0, 0):
                cnt[i] += 2
                return True
            cnt[i] += 2
    return False


def is_seven_pairs(cnt):
    pairs = 0
    for c in cnt:
        if c == 2:
            pairs += 1
        elif c != 0:
            return False
    return pairs == 7


def is_kokushi(cnt):
    for i in range(NUM_TILES):
        if cnt[i] and i not in YAOCHU:
            return False
    for i in YAOCHU:
        if cnt[i] > 2:
            return False
    return sum(1 for i in YAOCHU if cnt[i] > 0) == 13


def is_tenpai(hand):
    cnt = hand_to_counts(hand)
    for t in range(NUM_TILES):
        if cnt[t] < COPIES:
            cnt[t] += 1
            if is_seven_pairs(cnt):
                return True, '7pairs'
            if is_kokushi(cnt):
                return True, 'kokushi'
            if is_normal_agari(cnt[:]):
                return True, 'normal'
            cnt[t] -= 1
    return False, None


def simulate(n=1_000_000):
    wall = [t for t in range(NUM_TILES) for _ in range(COPIES)]
    total = normal = pairs = kokushi = 0

    for _ in tqdm(range(n), desc="天听模拟"):
        hand = random.sample(wall, 13)
        tenpai, mode = is_tenpai(hand)
        if tenpai:
            total += 1
            if mode == 'normal':
                normal += 1
            elif mode == '7pairs':
                pairs += 1
            elif mode == 'kokushi':
                kokushi += 1

    print(f"\n{'='*60}")
    print(f"模拟次数: {n:,}")
    print(f"规则: {'特殊字牌顺子' if USE_SPECIAL_WIND else '标准规则'}")
    print(f"{'='*60}")
    print(f"天听总概率:           {total/n:.4%}")
    print(f"  ├─ 一般型天听:      {normal/n:.4%}")
    print(f"  ├─ 七对子天听:      {pairs/n:.4%}")
    print(f"  └─ 国士无双天听:    {kokushi/n:.4%}")
    print(f"{'='*60}")


if __name__ == "__main__":
    simulate(1_000_000)
