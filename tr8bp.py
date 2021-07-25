import pyupbit
import datetime
import time


# getTime() - 현재시간을출력
def getTime():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 골드타임 여부
pGold = False
curTimeMinute             = datetime.datetime.now().minute
lastTradingSellTimeMinute = (datetime.datetime.now() + datetime.timedelta(minutes=-1)).minute
lastTradingBuyTimeMinute  = (datetime.datetime.now() + datetime.timedelta(minutes=-1)).minute

print(getTime())
print(lastTradingSellTimeMinute)
print(lastTradingBuyTimeMinute)

#############################
# 0. 거래소 접속
#############################
print("#############################")
print("# 0. 거래소 접속")
print("#############################")
access = "D7WHZTDtvkBZzx4K1gpj5xlqwh5xxa8Xxluzkv6Z"  # 본인 access 값으로 변경
secret = "R5FYPkcl8szmMzvtlfKn4wZMeGoe1XmHvIkXmERH"  # 본인 secret 값으로 변경
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
print("balance : ", upbit.get_balance("KRW"))  # 보유 현금 조회
print("보유 KRW 조회 : {0:>10,} 원".format(int(upbit.get_balance("KRW"))))  # 보유 현금 조회
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

while True :
    # DataFrame
    df = pyupbit.get_ohlcv(ticker, interval="minute1")
    # 이동평균선 5
    ma5  = df['close'].rolling(window=5).mean()
    # 이동평균선 10
    ma10 = df['close'].rolling(window=10).mean()
    # 이동평균선 20
    ma20 = df['close'].rolling(window=20).mean()
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

    p4_ma20 = ma20[-5]  # 4 분전
    p3_ma20 = ma20[-4]  # 3 분전
    p2_ma20 = ma20[-3]  # 2 분전
    p1_ma20 = ma20[-2]  # 1 분전
    p0_ma20 = ma20[-1]  # 현재

    # 시가
    p4_open = df["open"][-5]
    p3_open = df["open"][-4]
    p2_open = df["open"][-3]  # -2
    p1_open = df["open"][-2]  # -1
    p0_open = df["open"][-1]  # current

    # 종가
    p4_close = df["close"][-5]
    p3_close = df["close"][-4]
    p2_close = df["close"][-3]  # -2
    p1_close = df["close"][-2]  # -1
    p0_close = df["close"][-1]  # current

    #print(p4_open, p4_close, p4_ma5, p4_ma10, p4_ma20, p4_close-p4_open)
    #print(p3_open, p3_close, p3_ma5, p3_ma10, p3_ma20, p3_close-p3_open)
    #print(p2_open, p2_close, p2_ma5, p2_ma10, p2_ma20, p2_close-p2_open)
    #print(p1_open, p1_close, p1_ma5, p1_ma10, p1_ma20, p1_close-p1_open)
    #print(p0_open, p0_close, p0_ma5, p0_ma10, p0_ma20, p0_close-p0_open)

    if p0_ma5 > p0_ma10 :
        # 이평5가 이평10 보다 클 경우 -  상승하는 시점 - 골든타임
        pGold = True
        print("p0_ma5 > p0_ma10 - 상승추세", "-", getTime(), pGold)

    if pGold == True and cur_price > p0_ma20 :
        # 골드 포인트이며, 현재 가격이 이평20 보다 큰 최초 시점
        #############################
        # 매수
        ############################
        # buy signal
        print("buy signal")
        print("현재 시각 :", getTime())
        print("cur_price > p0_ma20 ", "-", getTime(), pGold)
        # 매수한 시각의 분(minute)
        lastTradingBuyTimeMinute = datetime.datetime.now().minute

        # buy
        print("buy !!!")
        balance = upbit.get_balance("KRW")
        print("balance : ", balance)  # 보유 현금 잔액조회
        print("보유 KRW 조회 : {0:>10,} 원".format(int(balance)))  # 보유 현금 조회

        if lastTradingSellTimeMinute != curTimeMinute :
            ## 최근 매도 시점의 분과 현재 분이 같으면 매수 제함  --- cus. 하락시점 BB-M 아래위로 빈번한 매매 방지
            # 현재 보유코인 잔액 조회 후, 수수료 금액(0.05%(0.0005)) 제외한 금액으로 매수
            trnVal = upbit.buy_market_order(ticker, balance * 0.9995)
            # trnVal = "pass"
            print("rtnVal #1: ", trnVal)


    if p0_ma5 < p0_ma10 :
        # 이평5가 이평10을 작을 경우 - 하락하는 시점- 골든타임 아님
        pGold = False
        print("p0_ma5 < p0_ma10 - 하락추세", "-", getTime(), pGold)

    if pGold == False and cur_price < p0_ma20 :
        # 골드 포인트가 아니며, 현재 가격이 이평20 보다 작은 최초 시점
        #############################
        # 매도
        ############################
        # sell signal
        print("sell signal")
        print("현재 시각 :", getTime())
        # 매도한 시각의 분(minute)
        lastTradingSellTimeMinute = datetime.datetime.now().minute

        # sell
        print("sell !!!")
        balance = upbit.get_balance("KRW")
        print("balance : ", balance)  # 보유 현금 잔액조회
        print("보유 KRW 조회 : {0:>10,} 원".format(int(balance)))  # 보유 현금 조회

        if lastTradingBuyTimeMinute != curTimeMinute:
            ## 최근 매도 시점의 분과 현재 분이 같으면 매도 제함  --- cus. 하락시점 BB-M 아래위로 빈번한 매매 방지
            # 현재 보유코인 잔액 조회 후, 수수료 금액(0.05%(0.0005)) 제외한 금액으로 매수
            trnVal = upbit.sell_market_order(ticker, balance * 0.9995)
            # trnVal = "pass"
            print("rtnVal #2: ", trnVal)


    # 1초 간격으로 정보 가져오기
    time.sleep(1)
    # 현재 시각의 분 저장 --- cus. 하락시점 BB-M 아래위로 빈번한 매매 방지
    curTimeMinute = datetime.datetime.now().minute

    # while   End-->

