import pyupbit
import datetime
import time

# getTime() - 현재시간을출력
def getTime():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 골드타임 여부
curTimeMinute             = datetime.datetime.now().minute
lastTradingSellTimeMinute = (datetime.datetime.now() + datetime.timedelta(minutes=-1)).minute
lastTradingBuyTimeMinute  = (datetime.datetime.now() + datetime.timedelta(minutes=-1)).minute

# 매매구간 여부
pTRzone = False
# 골드타임 여부
pGolden  = False

print(getTime())
print(lastTradingSellTimeMinute)
print(lastTradingBuyTimeMinute)

#############################
# 0. 거래소 접속
#############################
print("#############################")
print("# 0. 거래소 접속")
print("#############################")
access = "D7WHZTDtvkBZzx4K1gpj5xlqwh5xxa8Xxluzkv6Z" # 본인 access 값으로 변경
secret = "R5FYPkcl8szmMzvtlfKn4wZMeGoe1XmHvIkXmERH" # 본인 secret 값으로 변경
upbit = pyupbit.Upbit(access, secret)


# 거래코인 설정
ticker = "KRW-AXS"
print("거래코인 설정 :", ticker)
# 최근거래 된 가격 가져오기(대상코인 현재가 - 매도 1호 호가)
print("대상코인 현재가 - 매도 1호 호가 : ", pyupbit.get_current_price(ticker))
print()


#############################
# 1. 현재 KRW 잔액조회
#############################
print("#############################")
print("# 1. 현재 KRW 잔액조회")
print("#############################")

# 조회하고자하는 대상 - 잔액조회
print("balance : ", upbit.get_balance("KRW")) # 보유 현금 조회
print("보유 KRW 조회 : {0:>10,} 원".format(int(upbit.get_balance("KRW")))) # 보유 현금 조회
print()


#############################
# 2. 현재 시각 출력
#############################
print("#############################")
print("# 2. 현재 시각 출력")
print("#############################")

print("현재 시각 :", getTime())
print()


#############################
# 3. 트레이딩 시작
#############################
print("#############################")
print("# 3. 트레이딩 시작")
print("#############################")

while True:
    # DataFrame
    df = pyupbit.get_ohlcv(ticker, interval="minute1")
    # 이동평균선 5
    ma5  = df['close'].rolling(window=5).mean()
    # 이동평균선 10
    ma10 = df['close'].rolling(window=10).mean()
    # 이동평균선 20
    ma20 = df['close'].rolling(window=20).mean()
    # 이동평균선 60
    ma60 = df['close'].rolling(window=60).mean()
    # 현재가격 - ticker's
    cur_price = pyupbit.get_current_price(ticker)

    p4_ma5  = ma5[-5]   # 4 분전
    p3_ma5  = ma5[-4]   # 3 분전
    p2_ma5  = ma5[-3]   # 2 분전
    p1_ma5  = ma5[-2]   # 1 분전
    p0_ma5  = ma5[-1]   # 현재

    p4_ma10 = ma10[-5]  # 4 분전
    p3_ma10 = ma10[-4]  # 3 분전
    p2_ma10 = ma10[-3]  # 2 분전
    p1_ma10 = ma10[-2]  # 1 분전
    p0_ma10 = ma10[-1]  # 현재

    p4_ma20 = ma20[-5] # 4 분전
    p3_ma20 = ma20[-4] # 3 분전
    p2_ma20 = ma20[-3] # 2 분전
    p1_ma20 = ma20[-2] # 1 분전
    p0_ma20 = ma20[-1] # 현재

    p4_ma60 = ma60[-5] # 4 분전
    p3_ma60 = ma60[-4] # 3 분전
    p2_ma60 = ma60[-3] # 2 분전
    p1_ma60 = ma60[-2] # 1 분전
    p0_ma60 = ma60[-1] # 현재

    # 시가
    p4_open = df["open"][-5]
    p3_open = df["open"][-4]
    p2_open = df["open"][-3] # -2
    p1_open = df["open"][-2] # -1
    p0_open = df["open"][-1] # current

    # 종가
    p4_close = df["close"][-5]
    p3_close = df["close"][-4]
    p2_close = df["close"][-3] # -2
    p1_close = df["close"][-2] # -1
    p0_close = df["close"][-1] # current

    # 이평20이 이평60 보다 크거나 같을 경우
    # 이평60이 평행/상승구간일 경우 -- 하락장일 경우 매매를 정지하기 위한 옵션(튀는값 없애기 위함)
    # 현재 가격이 이평20의 현재가 보다 크거나 같을 때 -- 이평20이 이평60 보다 작고, 이평60이 평행이며 일 경우 매매를 없애기 위한 조건임
    # - 매매시점 구하기
    if ((p0_ma60 <= p0_ma20) or (p1_ma60 <= p0_ma60)) and (p0_ma20 <= cur_price) :
        pTRzone = True
        print(getTime(), "-", "pTRzone = True")
    else :
        pTRzone = False
        print(getTime(), "-", "pTRzone = False")
        # 모든 매매 정지
        cur_price = 0
        p1_open   = 0
        p1_close  = 0

    # 이평5가  이평10 보다 클 경우 -- Golden zone
    if (p0_ma5 > p0_ma10) :
        pGolden = True
    else :
        pGolden = False

    #############################
    # 매수시점 구하기
    #############################
    if pTRzone is True or (p3_ma20 < p2_ma20 and p2_ma20 < p1_ma20 and p1_ma20 < p0_ma20) or pGolden is True :
        # pTRzone is True 이거나, BB-M 이상 가격으로 상승추세 - 3분간 상승장 지속이거나, # Golden zone일 경우
        print("BB-M - 상승추세")

        print("p3_ma20---", p3_ma20, ma20[-4], ma20[-4] - ma20[-5])
        print("p2_ma20---", p2_ma20, ma20[-3], ma20[-3] - ma20[-4]) # -2
        print("p1_ma20---", p1_ma20, ma20[-2], ma20[-2] - ma20[-3]) # -1
        print("p0_ma20---", p0_ma20, ma20[-1], ma20[-1] - ma20[-2]) # current
        print()

        #if (p2_close - p2_open) >= 0 and (p1_close - p1_open) >= 0 and (p1_open > p0_ma20 and p1_close > p0_ma20) :
        # 양봉, 양봉, 그리고 현시점의 ma20 보다 현시점의 시가, 종가 클 경우
        # buy signal
        print("buy signal")
        #############################
        # 매수
        #############################
        print("현재 시각 :", getTime())

        print("p2----", df["open"][-3], df["close"][-3], df["close"][-3]-df["open"][-3]) # -2
        print("p1----", df["open"][-2], df["close"][-2], df["close"][-2]-df["open"][-2]) # -1
        print("p0----", df["open"][-1], df["close"][-1], df["close"][-1]-df["open"][-1]) # current
        print()

        # buy
        print("buy !!!")
        balance = upbit.get_balance("KRW")
        print("balance : ", balance) # 보유 현금 잔액조회
        print("보유 KRW 조회 : {0:>10,} 원".format(int(balance))) # 보유 현금 조회

        if lastTradingSellTimeMinute != curTimeMinute:
            ## 최근 매도 시점의 분과 현재 분이 같으면 매수 제함  --- cus. 하락시점 BB-M 아래위로 빈번한 매매 방지
            # 현재 보유코인 잔액 조회 후, 수수료 금액(0.05%(0.0005)) 제외한 금액으로 매수
            trnVal = upbit.buy_market_order(ticker, balance * 0.9995)
            # 매수한 시각의 분(minute)
            lastTradingBuyTimeMinute = datetime.datetime.now().minute
            print("rtnVal #1: ", trnVal)
            print()
            print()


    #############################
    # 매도시점 구하기
    #############################
    # 현시점의 시가, 종가 중 어느 하나가 이평20 보다 낮을 경우
    # Golden zone이 아닐 경우에만
    # 매도할 수 있다.
    if ((p0_open < p0_ma20) or (p0_close < p0_ma20)) and (pGolden is False):
        # sell
        p0_ma20 = ma20[-1] # 현재
        print("p0---- ma20:", p0_ma20, "open:", df["open"][-1], "close:", df["close"][-1], "cur_price:", cur_price, df["close"][-1]-df["open"][-1]) # current
        print("현재 시각 :", getTime())
        print("sell !!!")
        #############################
        # 매도
        #############################
        # 현재 보유코인 잔액 조회 후, 수수료 금액(0.05%(0.0005)) 제외한 금액으로 매도
        balance = upbit.get_balance(ticker)
        print("보유 코인 balance : ", balance) # 보유 코인 잔액조회
        print("수수료 : ", balance * 0.0005) # 수수료
        print("투자액 : ", balance * 0.9995) # 투자액
        print()

        if lastTradingBuyTimeMinute != curTimeMinute :
            trnVal = upbit.sell_market_order(ticker, balance * 0.9995)
            # 매도한 시각의 분(minute)
            lastTradingSellTimeMinute = datetime.datetime.now().minute
            print("rtnVal2 : ", trnVal)
            print()
            print()


    # 1초 간격으로 정보 가져오기
    time.sleep(1)
    # 현재 시각의 분 저장 --- cus. 하락시점 BB-M 아래위로 빈번한 매매 방지
    curTimeMinute = datetime.datetime.now().minute

    # while   End-->
