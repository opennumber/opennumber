# api.opennumber.org

为了防止接口滥用，请填写以下资料发送到到email: opennumber.org@gmail.com
```
phone:
name:
公司url: 发送者邮箱必须是该公司邮箱，否则一律拒绝通过！
公司名称： 
```


在接到该邮件一个自然日内，我们会发送访问接口的token和key给您。



----
### HTTP 访问设置
- host: http://api.opennumber.org
- method: GET
- encoding: utf8

----
### HTTP 请求参数说明
- sign：该参数值为一个md5数值的hex。 例如md5("123456") == "e10adc3949ba59abbe56e057f20f883e"
- timestamp: 表示该请求的unix timestamp。为了方便调试。e.g timestamp=time()
- token: 访问者的身份token
- key:  用来生成sign


-----
### HTTP 响应
api.opennumber.org的响应为'application/json; charset=utf8'

```javascript
{
    "code": 0,
    "message": "success",
    "result": null
}
```
- code: 整数。 0表示成功， 其他的为请求失败。
- message: 请求结果的文字表述
- result: 请求的结果。不同的api，返回的数据会稍有不同


-------
### 获取手机号码的风险评级
- url: /phone/check
- token: [必选]。
- timestamp: [必选]
- phone: [必选] 要检测的手机号码
- action: [必选] 该手机号码在你们的网站干了什么事情. ['login', 'logout', 'register', 'post']. 对于例如领取优惠券，发帖等action=post。请谨慎选择
- ip: [选填] 支持ipv4/ipv6。你们的客户的IP地址， 注意不是你们的服务器地址。
- create_datetime: [选填] 手机号码action的时间，如果为空的时候， 默认为当前的时间。如果要检测一个手机号在三天前的login action，请设置create_datetime为三天前的时间。e.g: create_datetime=2016-01-01 20:00:00
- sign: [必选] md5(string_concat(token, timestamp, phone))


返回的结果
```javascript
{
    "code": 0,
    "message": "success",
    "result": {
        "rating": "green"
    }
}
```


rating: 表示该手机号码的风险评估。风险序列值为['white', 'green', 'yellow', 'red', 'black'], 风险依次增大

```
white: 该手机号码在白名单里
green: 手机号码征信良好
yellow: 该手机号码行为符合少量有风险的模式。
red:  该手机号码行为符合大量有风险的模式。
black: 该手机号码为黑名单。 信用极差！
```


------
### 提交手机号码白名单
提交白名单手机号码

这个需要单独申请接口访问权限。 发送email到opennumber.org@gmail.com申请访问权限

- url: /phone/commit/white_list
- token: [必选]。
- timestamp: [必选]
- phone: [必选] 要检测的手机号码
- sign: [必选] md5(string_concat(token, timestamp, phone))

返回的结果为
```javascript
{
    "code": 0,
    "message": "success",
    "result": null
}
```

----
### 提交手机号码的风险rating
提交手机号码的风险rating

这个需要单独申请接口访问权限。 发送email到opennumber.org@gmail.com申请访问权限

- url: /phone/commit/white_list
- token: [必选]。
- timestamp: [必选]
- phone: [必选] e.g: 13311223344
- rating: [必填]
- sign: [必选] md5(string_concat(token, timestamp, phone))

返回的结果为
```javascript
{
    "code": 0,
    "message": "success",
    "result": null
}
```
