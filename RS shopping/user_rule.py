# coding=utf-8
# 自定义的推荐规则

from copy import copy
from tmall import getDiffDay


# 推荐规则
# 函数可分为两部分
# 1. 计算用户特征
# 2. 根据规则进行筛选
#
# 参数 data: 数组，数组元素为 (user_id, brand_id, action_type, month, day)
# 返回值 R : 数组，数组元素为 (user_id, brand_id)
def getRecommendByRule(data):
	F = {}		# 存储用户特征
	R = []		# 存储推荐结果

	# 所有要进行统计的特征，在这里进行声明并赋予初始值
	item = {
		'click': 0,		# 点击次数
		'buy': 0,		# 购买次数
		'fav': 0,		# 加入收藏夹次数
		'cart': 0,		# 加入购物车次数
		'diff_day': 1000,	# 因为是要推测下一个月的购买情况
				# 显然在最近一段时间有交互的，购买可能性越大
				# 因此将最后一次交互的相差天数也作为一个特征
				# 如我们推测7月15-8月15这一个月的购买情况，用户在7月8号跟7月12号均有交互记录
				# 则diff_day为3（取最近的7月12，计算跟7月15的相差天数）
		'click_diff_day': 1000,
		'buy_furthest_diff_day': 0,
		'buy_diff_day': 1000,
		'fav_diff_day': 1000,
		'cart_diff_day': 1000
	}


	# 1. 计算用户特征
	for uid, bid, action_type, month, day in data:
		# 初始化
		F.setdefault(uid, {})
		F[uid].setdefault(bid, copy(item))

		# 新建一个引用，简化代码
		e = F[uid][bid]

		# 基础特征计算
		if action_type == 0:
			e['click'] += 1
			if e['click_diff_day'] > getDiffDay((month, day), (7, 15)):
				e['click_diff_day'] = getDiffDay((month, day), (7, 15))
		elif action_type == 1:
			e['buy'] += 1
			if e['buy_diff_day'] > getDiffDay((month, day), (7, 15)):
				e['buy_diff_day'] = getDiffDay((month, day), (7, 15))
			if e['buy_furthest_diff_day'] < getDiffDay((month, day), (7, 15)):
				e['buy_furthest_diff_day'] = getDiffDay((month, day), (7, 15))
		elif action_type == 2:
			e['fav'] += 1
			if e['fav_diff_day'] > getDiffDay((month, day), (7, 15)):
				e['fav_diff_day'] = getDiffDay((month, day), (7, 15))
		elif action_type == 3:
			e['cart'] += 1
			if e['cart_diff_day'] > getDiffDay((month, day), (7, 15)):
				e['cart_diff_day'] = getDiffDay((month, day), (7, 15))

		# 时间特征
		diff_day = getDiffDay((month, day), (7, 15))
		if diff_day < e['diff_day']:
			e['diff_day'] = diff_day

		# 计算其他特征

	print(f"user_id为'10944750'的特征字典为：{F['10944750']}")

	# 2. 根据特征进行筛选
	for uid, bid_list in F.items():
		for bid, e in bid_list.items():
			# 在此处应用推荐规则，如将最近一个月内有交互，且总点击次数大于10次的，加入到推荐中
			if (e['diff_day'] < 27) and ((e['click'] > 8) or (e['buy'] == 1 and 34 > e['buy_diff_day'] > 30) or (e['buy'] == 2 and e['buy_diff_day'] < 22) or (e['cart'] > 0 and e['cart_diff_day'] < 5)):
				# 加入到推荐列表中，注意加入的是元组 (uid, bid)，有两个括号
				R.append((uid, bid))
			elif e['buy'] == 2 and e['buy_furthest_diff_day'] - e['buy_diff_day'] > 10:
				R.append((uid, bid))

	return R