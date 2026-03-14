import requests
import time
from datetime import datetime

# --------------------- 配置项 ---------------------
# 持仓基金代码（可自行修改，用于高亮显示）
HOLD_FUND_CODES = ["501312","161130","161125"]

# --------------------- 工具函数 ---------------------
def str_width(s):
    """计算字符串显示宽度（中文字符算2个宽度）"""
    return sum(2 if '\u4e00' <= c <= '\u9fff' else 1 for c in str(s))

def pad_text(s, width):
    """按显示宽度右填充空格，实现对齐"""
    s = str(s)
    w = str_width(s)
    pad = max(0, width - w)
    return s + ' ' * pad

def style_hold_text(text, is_hold):
    """持仓基金黄色加粗高亮"""
    if not is_hold:
        return text
    ANSI_YELLOW_BOLD = "\033[1;33m"
    ANSI_RESET = "\033[0m"
    return f"{ANSI_YELLOW_BOLD}{text}{ANSI_RESET}"

# --------------------- 数据获取 ---------------------
def fetch_qdii_data():
    """从集思录获取美股QDII数据"""
    url = "https://www.jisilu.cn/data/qdii/qdii_list/E?___jsl=LST___t=1773467653046&only_lof=y&rp=22"
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,zh-HK;q=0.8,zh-CN;q=0.7,zh;q=0.6",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": "https://www.jisilu.cn/data/qdii/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()["rows"]
    except Exception as e:
        print(f"数据获取失败: {e}")
        return None

# --------------------- 计算估值与溢价率 ---------------------
def calculate_premium(data_rows):
    """
    计算T-1估值与溢价率
    T-1估值 = T-2净值 * (1 + T-1指数涨幅 * 股票比率)
    溢价率 = (场内价格 - T-1估值) / T-1估值 * 100
    """
    results = []
    for row in data_rows:
        cell = row["cell"]
        try:
            fund_id = cell["fund_id"]
            fund_nm = cell["fund_nm"]
            issuer_nm = cell["issuer_nm"]
            price = float(cell["price"])
            increase_rt = cell["increase_rt"]
            volume = float(cell["volume"])
            amount = float(cell["amount"])
            amount_incr = cell["amount_incr"]
            turnover_rt = cell["turnover_rt"]
            nav = float(cell["fund_nav"])  # T-2净值
            nav_dt = cell["nav_dt"]
            asset_ratio = float(cell["asset_ratio"]) / 100  # 股票比率
            ref_increase_rt = cell["ref_increase_rt"]
            if ref_increase_rt == "-":
                ref_increase_rt = 0.0
            else:
                ref_increase_rt = float(ref_increase_rt.replace("%", "")) / 100
            index_nm = cell["index_nm"]
            apply_status = cell["apply_status"]
            redeem_status = cell["redeem_status"]
            apply_fee = cell["apply_fee"]
            redeem_fee = cell["redeem_fee"]

            # 计算T-1估值
            t1_val = nav * (1 + ref_increase_rt * asset_ratio)
            # 计算溢价率
            if t1_val == 0:
                premium_rt = 0.0
            else:
                premium_rt = (price - t1_val) / t1_val * 100

            results.append({
                "fund_id": fund_id,
                "fund_nm": fund_nm,
                "issuer_nm": issuer_nm,
                "price": price,
                "increase_rt": increase_rt,
                "volume": volume,
                "amount": amount,
                "amount_incr": amount_incr,
                "turnover_rt": turnover_rt,
                "nav": nav,
                "nav_dt": nav_dt,
                "asset_ratio": asset_ratio * 100,
                "ref_increase_rt": ref_increase_rt * 100,
                "t1_val": t1_val,
                "premium_rt": premium_rt,
                "index_nm": index_nm,
                "apply_status": apply_status,
                "redeem_status": redeem_status,
                "apply_fee": apply_fee,
                "redeem_fee": redeem_fee
            })
        except Exception as e:
            print(f"计算溢价率失败: {e}")
            continue
    # 按溢价率从高到低排序
    results.sort(key=lambda x: x["premium_rt"], reverse=True)
    return results

# --------------------- 输出结果 ---------------------
def print_results(data):
    """格式化打印结果"""
    print(f"\n************************ 海外ETF/LOF（共{len(data)}只） ************************\n")
    col_w = [8, 20, 8, 8, 14, 14, 10, 10, 12, 10, 12, 30, 14, 10, 10, 8]
    headers = [
        "代码", "名称", "现价", "涨幅", "成交额(万)", "份额(万份)", "场内换手",
        "T-2净值", "T-1估值(估)", "溢价率", "净值日期", "跟踪指数",
        "T-1指数涨幅", "申购费", "购买状态", "赎回费"
    ]
    print(''.join([pad_text(h, col_w[i]) for i, h in enumerate(headers)]))
    print("-" * 200)

    for item in data:
        is_hold = item["fund_id"] in HOLD_FUND_CODES
        line = ""
        line += style_hold_text(pad_text(item["fund_id"], col_w[0]), is_hold)
        line += style_hold_text(pad_text(item["fund_nm"], col_w[1]), is_hold)
        line += style_hold_text(pad_text(f"{item['price']:.3f}", col_w[2]), is_hold)
        line += style_hold_text(pad_text(item["increase_rt"], col_w[3]), is_hold)
        line += style_hold_text(pad_text(f"{item['volume']:.2f}", col_w[4]), is_hold)
        line += style_hold_text(pad_text(f"{item['amount']:.0f}", col_w[5]), is_hold)
        line += style_hold_text(pad_text(item["turnover_rt"], col_w[6]), is_hold)
        line += style_hold_text(pad_text(f"{item['nav']:.4f}", col_w[7]), is_hold)
        line += style_hold_text(pad_text(f"{item['t1_val']:.4f}", col_w[8]), is_hold)
        line += style_hold_text(pad_text(f"{item['premium_rt']:.2f}%", col_w[9]), is_hold)
        line += style_hold_text(pad_text(item["nav_dt"], col_w[10]), is_hold)
        line += style_hold_text(pad_text(item["index_nm"], col_w[11]), is_hold)
        line += style_hold_text(pad_text(f"{item['ref_increase_rt']:.2f}%", col_w[12]), is_hold)
        line += style_hold_text(pad_text(item["apply_fee"], col_w[13]), is_hold)
        line += style_hold_text(pad_text(item["apply_status"], col_w[14]), is_hold)
        line += style_hold_text(pad_text(item["redeem_fee"], col_w[15]), is_hold)
        print(line)

# --------------------- 主函数 ---------------------
def main():
    rows = fetch_qdii_data()
    if not rows:
        print("获取数据失败")
        return
    data = calculate_premium(rows)
    if not data:
        print("无有效数据")
        return
    print_results(data)

if __name__ == "__main__":
    main()
    time.sleep(1000)