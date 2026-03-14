import requests
import json
import time

def get_latest_index_from_sse(secid):
    # 你截图里的 SSE 接口 URL
    url = "https://90.push2.eastmoney.com/api/qt/stock/trends2/sse"
    
    # 复制你浏览器里的请求头（关键是 Accept 和 User-Agent）
    headers = {
        "Accept": "text/event-stream",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Referer": f"https://quote.eastmoney.com/zz/{secid}.html"
    }
    
    # 接口参数（从你的 URL 里复制）
    params = {
        "fields1": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f17",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58",
        "mpi": "1000",
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "secid": secid,  # 2.930914 对应港股通高股息
        "ndays": "1",
        "iscr": "0",
        "iscca": "0",
        "wbp2u": "|0|0|0|web"
    }

    latest_data = None
    buffer = ""

    try:
        # 发起流式请求
        with requests.get(url, headers=headers, params=params, stream=True, timeout=10) as r:
            # 逐行读取流
            for line in r.iter_lines(decode_unicode=True):
                if line:
                    buffer += line
                else:
                    # 空行代表一条完整的 SSE 消息结束
                    if buffer.startswith("data:"):
                        json_str = buffer[5:].strip()  # 去掉 "data:" 前缀
                        try:
                            json_data = json.loads(json_str)
                            if json_data.get("rc") == 0 and "data" in json_data:
                                latest_data = json_data["data"]
                                break  # 拿到第一条有效数据就立刻退出，不继续监听
                        except json.JSONDecodeError:
                            pass
                    buffer = ""  # 清空缓冲区，准备下一条消息
    except requests.exceptions.Timeout:
        print("请求超时，可能是网络或接口问题")
    except Exception as e:
        print(f"请求出错: {e}")

    if latest_data:
        # 解析你需要的字段
        code = latest_data["code"]
        name = latest_data["name"]
        timestamp = latest_data["time"]
        
        # 从 trends 里取最后一条作为最新点数
        trends = latest_data.get("trends", [])
        if trends:
            last_trend = trends[-1]
            time_str = last_trend.split(",")[0]
            latest_price = float(last_trend.split(",")[2])  # 第二个字段是当前价格
            return {
                "code": code,
                "name": name,
                "latest_price": latest_price,
                "update_time": time_str
            }
    return None

# ========== 调用并打印结果 ==========
if __name__ == "__main__":
    
    test_codes = ["2.930914", "2.930917"]
    for fund_code in test_codes:
        result = get_latest_index_from_sse(fund_code)
        if result:
            print(f"📊 {result['name']} ({result['code']})")
            print(f"💹 最新点数: {result['latest_price']:.2f}")
            print(f"📅 更新时间: {result['update_time']}")
        else:
            print("❌ 未能获取数据")
        print("")
    time.sleep(100)