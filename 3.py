import random
from collections import Counter
from tqdm import tqdm  # 用于显示进度条

def is_seven_pairs(hand):
    """
    判断14张牌是否组成“七对子”：每种牌的数目均为偶数
    注意：如果某种牌出现4次，也可视为2对。
    """
    if len(hand) != 14:
        return False
    counts = Counter(hand)
    for count in counts.values():
        if count % 2 != 0:  # 如果有牌出现次数为奇数，则不能构成完整的对子
            return False
    return True

def simulate_round():
    # 构造牌山：34种牌，每种4张，共136张牌
    deck = []
    for i in range(34):
        deck.extend([i] * 4)
    random.shuffle(deck)

    # 起手抽13张牌
    hand = [deck.pop() for _ in range(13)]

    # 模拟21回合摸牌弃牌过程
    for _ in range(21):
        if not deck:
            break  # 如果牌山抽完，提前结束
        # 摸一张牌，使手牌达到14张
        hand.append(deck.pop())
        # 检查是否满足“七对子”和牌型
        if is_seven_pairs(hand):
            return True
        # 否则，从手牌中寻找“无用牌”：即出现1次或3次的牌
        counts = Counter(hand)
        useless_tiles = [tile for tile in hand if counts[tile] in (1, 3)]
        if useless_tiles:
            tile_to_discard = random.choice(useless_tiles)
            hand.remove(tile_to_discard)
        else:
            # 如果没有符合条件的弃牌目标，随便弃掉一张牌
            hand.pop()

    # 21回合结束后，再摸一张牌，检查最终手牌是否构成“七对子”
    if deck:
        hand.append(deck.pop())
        return is_seven_pairs(hand)
    else:
        return False

# 进行多次模拟，并统计最终满足“七对子”次数
N = 1000000  # 模拟次数
success_count = 0

for _ in tqdm(range(N), desc="模拟进度"):
    if simulate_round():
        success_count += 1

print("经过21轮摸牌弃牌后，最终形成七对子和牌的次数为：", success_count)
