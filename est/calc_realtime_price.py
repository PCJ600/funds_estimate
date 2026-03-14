import requests
import time

def get_realtime_stock_data(stock_code):
    """
    获取新浪财经实时股票/基金数据
    
    参数:
    stock_code (str): 股票/基金代码，例如 "sh501306", "sz000001"
    
    返回:
    str: 返回的原始响应文本，如果请求失败则返回 None
    """
    # 定义请求头，模拟浏览器访问
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Referer": "https://finance.sina.com.cn/"  # 添加Referer头，这是请求新浪财经API的关键
    }
    
    # 构建请求URL
    url = f"http://hq.sinajs.cn/list={stock_code}"
    
    try:
        print(f"正在请求: {url}")
        
        # 发送请求
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 检查HTTP状态码
        
        # 设置正确的编码（新浪财经API返回的是GBK编码）
        response.encoding = 'GBK'
        
        print(f"请求状态码: {response.status_code}")
        print("响应内容:")
        print(response.text)
        print("-" * 50)
        
        return response.text
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP错误: {e}")
        print(f"状态码: {response.status_code if 'response' in locals() else '未知'}")
    except requests.exceptions.ConnectionError as e:
        print(f"连接错误: {e}")
    except requests.exceptions.Timeout as e:
        print(f"请求超时: {e}")
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    
    return None

# 测试函数
if __name__ == "__main__":
    # 测试不同的股票/基金代码
    codes_to_test = ["sh501302", "sh501305", "sh501306", "sh501307", "sh501310"]
    for code in codes_to_test:
        print(f"\n正在获取 {code} 的实时数据...")
        result = get_realtime_stock_data(code)
        
        if result:
            # 如果需要解析数据，可以在这里处理
            # 示例解析：新浪API返回格式通常为 var hq_str_sh501306="...";
            if "hq_str_" in result:
                try:
                    # 提取数据部分
                    data_str = result.split('"')[1]
                    fields = data_str.split(',')
                    
                    if len(fields) >= 3:
                        print(f"解析结果:")
                        print(f"  股票名称: {fields[0]}")
                        print(f"  今日开盘: {fields[1]}")
                        print(f"  昨日收盘: {fields[2]}")
                        print(f"  当前价格: {fields[3]}")
                        print(f"  今日最高: {fields[4]}")
                        print(f"  今日最低: {fields[5]}")
                        print(f"  成交量: {fields[8]}")
                        print(f"  成交额: {fields[9]}")
                        print(f"  更新时间: {fields[30]} {fields[31]}")
                except (IndexError, ValueError) as e:
                    print(f"解析数据时出错: {e}")
        else:
            print(f"获取 {code} 数据失败")
    
    # 暂停100秒，方便查看结果
    print("\n测试完成，程序将暂停100秒...")
    time.sleep(100)