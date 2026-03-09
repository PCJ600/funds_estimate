import requests
import json
import re
import time

def get_fund_latest_net_value(fund_code):
    """
    获取东方财富基金 最新一日 单位净值
    适配真实HTML返回内容，只提取：日期、单位净值
    """
    url = "https://fundf10.eastmoney.com/F10DataApi.aspx"

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Host": "fundf10.eastmoney.com",
        "Pragma": "no-cache",
        "Referer": f"https://fundf10.eastmoney.com/jjjz_{fund_code}.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not A;Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }

    params = {
        "type": "lsjz",
        "code": fund_code,
        "page": 1,
        "per": 1,
        "sdate": "",
        "edate": ""
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        content = response.text

        # ==============================================
        # 🔍 正确解析：从HTML表格中提取 日期 和 单位净值
        # ==============================================
        # 匹配 <tr><td>日期</td><td ...>净值</td>
        pattern = r"<tr><td>(\d{4}-\d{2}-\d{2})</td><td[^>]*>([\d.]+)</td>"
        match = re.search(pattern, content)
        
        if match:
            nav_date = match.group(1)    # 净值日期
            unit_nav = match.group(2)    # 单位净值
            
            return {
                "基金代码": fund_code,
                "净值日期": nav_date,
                "单位净值": unit_nav
            }
        else:
            print(f"[{fund_code}] 解析失败：未匹配到数据")
            return None

    except Exception as e:
        print(f"[{fund_code}] 获取失败：{str(e)}")
        return None

if __name__ == "__main__":
    # ===================== 基金列表 =====================
    fund_list = ["501302", "501305", "501306", "501307", "501310"]
    
    print("===== 开始获取基金最新净值 =====\n")
    
    # 循环获取每一只基金
    for code in fund_list:
        data = get_fund_latest_net_value(code)
        if data:
            print(f"✅ {data['基金代码']} 获取成功：")
            print(json.dumps(data, ensure_ascii=False, indent=4))
        else:
            print(f"❌ {code} 获取失败")
        print("-" * 40)  # 分隔线，看得更清楚
    
    print("===== 全部获取完成 =====")

time.sleep(100)