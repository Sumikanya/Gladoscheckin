import requests
import json
import os
import urllib.parse

from pypushdeer import PushDeer

# -------------------------------------------------------------------------------------------
# github workflows
# -------------------------------------------------------------------------------------------
if __name__ == '__main__':

    # 推送内容
    title = ""
    success, fail, repeats = 0, 0, 0        # 成功账号数量 失败账号数量 重复签到账号数量
    context = ""

    # glados账号cookie 直接使用数组 如果使用环境变量需要字符串分割一下
    cookies = os.environ.get("COOKIES", []).split("&")
    if cookies[0] != "":

        check_in_url = "https://glados.space/api/user/checkin"        # 签到地址
        status_url = "https://glados.space/api/user/status"          # 查看账户状态

        referer = 'https://glados.space/console/checkin'
        origin = "https://glados.space"
        useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        payload = {
            'token': 'glados.one'
        }
        
        for cookie in cookies:
            checkin = requests.post(check_in_url, headers={'cookie': cookie, 'referer': referer, 'origin': origin,
                                    'user-agent': useragent, 'content-type': 'application/json;charset=UTF-8'}, data=json.dumps(payload))
            state = requests.get(status_url, headers={
                                'cookie': cookie, 'referer': referer, 'origin': origin, 'user-agent': useragent})

            message_status = ""
            points = 0
            message_days = ""
            
            
            if checkin.status_code == 200:
                # 解析返回的json数据
                result = checkin.json()     
                # 获取签到结果
                check_result = result.get('message')
                points = result.get('points')

                # 获取账号当前状态
                result = state.json()
                # 获取剩余时间
                leftdays = int(float(result['data']['leftDays']))
                # 获取账号email
                email = result['data']['email']
                
                print(check_result)
                if "Checkin! Got" in check_result:
                    success += 1
                    message_status = "签到成功，会员点数 + " + str(points)
                elif "Checkin Repeats!" in check_result:
                    repeats += 1
                    message_status = "重复签到，明天再来"
                else:
                    fail += 1
                    message_status = "签到失败，请检查..."

                if leftdays is not None:
                    message_days = f"{leftdays} 天"
                else:
                    message_days = "error"
            else:
                email = ""
                message_status = "签到请求URL失败, 请检查..."
                message_days = "error"

            context += "账号: " + email + ", P: " + str(points) +", 剩余: " + message_days + " | "

        # 推送内容 
        title = f'Glados, 成功{success},失败{fail},重复{repeats}'
        print("Send Content:" + "\n", context)
        
    else:
        # 推送内容 
        title = f'# 未找到 cookies!'

    #print("sckey:", sckey)
    #print("cookies:", cookies)
    
    # 推送消息
    # 未设置 sckey 则不进行推送

    # bark 服务地址和推送 token
    bark_url = os.environ.get("BARK_URL", "")  # e.g. http://127.0.0.1:8080
    bark_token = os.environ.get("BARK_TOKEN", "")

    print("BARK_URL:", os.environ.get("BARK_URL"))
    print("BARK_TOKEN:", os.environ.get("BARK_TOKEN"))

    # URL 编码
    encoded_title = urllib.parse.quote(title)
    encoded_context = urllib.parse.quote(context)

    # 推送消息
    if bark_url and bark_token:
        # 构建 bark 推送 URL：{bark_url}/{token}/{title}/{message}
        push_url = f"{bark_url}/{bark_token}/{encoded_title}/{encoded_context}"
        print(push_url)
        try:
            resp = requests.get(push_url)
            if resp.status_code == 200:
                print("Bark 推送成功")
            else:
                print(f"Bark 推送失败，状态码: {resp.status_code}")
        except Exception as e:
            print(f"Bark 推送异常: {e}")
    else:
        print("未配置 BARK_URL 或 BARK_TOKEN，跳过推送")
