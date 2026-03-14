import requests
import pandas as pd
from datetime import datetime, time
import time

# --------------------- 对齐 ---------------------
def str_width(s):
    return sum(2 if '\u4e00' <= c <= '\u9fff' else 1 for c in str(s))

def pad_text(s, width):
    s = str(s)
    w = str_width(s)
    pad = max(0, width - w)
    return s + ' ' * pad

# --------------------- 港股交易日 + 交易时间判断 ---------------------
def is_hk_trading_hours():
    now = datetime.now()
    weekday = now.weekday()

    # 周六、周日 → 非交易日
    if weekday >= 5:
        return False

    # 交易时间
    current_time = now.time()
    morning = time(9, 30) <= current_time <= time(12, 0)
    afternoon = time(13, 00) <= current_time <= time(16, 00)
    return morning or afternoon

# --------------------- 数据获取 ---------------------
def fetch_lof_data():
    url = "https://www.jisilu.cn/data/qdii/qdii_list/A?___jsl=LST___t=1773454444970&only_lof=y&rp=22" # only_lof=y, 只算lof数据
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://www.jisilu.cn/data/qdii/',
        'X-Requested-with': 'XMLHttpRequest'
    }
    try:
        response = requests.get(url, headers=headers, timeout=8)
        return response.json()['rows']
    except:
        return None

# --------------------- 计算实时折溢价率 ---------------------
def calculate_premium_discount(data_rows):
    results = []
    trading = is_hk_trading_hours()

    for row in data_rows:
        cell = row['cell']
        try:
            fund_id = cell['fund_id']
            fund_nm = cell['fund_nm']
            asset_ratio = float(cell['asset_ratio']) / 100
            price = float(cell['price'])
            fund_nav = float(cell['fund_nav'])
            nav_dt = cell['nav_dt']
            apply_status = cell['apply_status']
            redeem_status = cell['redeem_status']
            redeem_fee = cell['redeem_fee']

            # 交易时间使用实时指数涨跌幅算估值; 对于非交易时间, 在当晚净值公布后, 指数涨跌幅就无效了, 所以设置为0, 方便净值公布后计算折溢价
            if trading:
                ref_increase_rt = float(cell['ref_increase_rt'].replace('%', '')) / 100
            else:
                ref_increase_rt = 0

            # 计算实时估值和实时溢价率
            real_val = fund_nav * (1 + ref_increase_rt * asset_ratio)
            premium = (price - real_val) / real_val * 100

            results.append([
                fund_id, fund_nm, asset_ratio*100, price, fund_nav, nav_dt,
                ref_increase_rt*100, real_val, premium, apply_status, redeem_status, redeem_fee
            ])
        except:
            continue

    return results

# --------------------- 输出 ---------------------
def main():
    rows = fetch_lof_data()
    if not rows:
        print("获取数据失败")
        return

    data = calculate_premium_discount(rows)
    if not data:
        print("无有效数据")
        return

    data.sort(key=lambda x: x[8], reverse=True)

    print("\n==================== 港股指数LOF实时溢价率 ====================\n")

    col_w = [10, 24, 12, 10, 12, 14, 12, 12, 12, 10, 10, 8]
    headers = ["基金代码", "基金名称", "股票比率", "现价", "T-1净值", "净值日期", "指数涨幅", "实时估值", "折溢价率", "申购", "赎回", "赎回费"]

    print(''.join([pad_text(h, col_w[i]) for i, h in enumerate(headers)]))
    print('-' * 165)

    for item in data:
        line = ''
        line += pad_text(item[0], col_w[0])
        line += pad_text(item[1], col_w[1])
        line += pad_text(f"{item[2]:.2f}%", col_w[2])
        line += pad_text(f"{item[3]:.3f}", col_w[3])
        line += pad_text(f"{item[4]:.4f}", col_w[4])
        line += pad_text(item[5], col_w[5])
        line += pad_text(f"{item[6]:.2f}%", col_w[6])
        line += pad_text(f"{item[7]:.3f}", col_w[7])
        line += pad_text(f"{item[8]:.2f}%", col_w[8])
        line += pad_text(item[9], col_w[9])
        line += pad_text(item[10], col_w[10])
        line += pad_text(item[11], col_w[11])
        print(line)

if __name__ == "__main__":
    main()
    time.sleep(1000)