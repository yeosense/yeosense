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
    # 이동평균선 20
    ma20 = df['close'].rolling(window=20).mean()
    # 현재가격 - ticker's
    cur_price = pyupbit.get_current_price(ticker)

    p4_ma20 = ma20[-5] # 4 분전
    p3_ma20 = ma20[-4] # 3 분전
    p2_ma20 = ma20[-3] # 2 분전
    p1_ma20 = ma20[-2] # 1 분전
    p0_ma20 = ma20[-1] # 현재

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

    if p3_ma20 < p2_ma20 and p2_ma20 < p1_ma20 and p1_ma20 < p0_ma20:
        # BB-M 이상 가격으로 상승추세 - 3분간 상승장 지속
        print("BB-M - 상승추세")

        print("p3_ma20---", p3_ma20, ma20[-4], ma20[-4] - ma20[-5])
        print("p2_ma20---", p2_ma20, ma20[-3], ma20[-3] - ma20[-4]) # -2
        print("p1_ma20---", p1_ma20, ma20[-2], ma20[-2] - ma20[-3]) # -1
        print("p0_ma20---", p0_ma20, ma20[-1], ma20[-1] - ma20[-2]) # current
        print()

        if (p2_close - p2_open) >= 0 and (p1_close - p1_open) >= 0 and (p1_open > p0_ma20 and p1_close > p0_ma20) :
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



            if ("error" in trnVal):
                if(trnVal["error"]['name'] not in "invalid_volume_ask" and trnVal["error"]['name'] not in "under_min_total_bid"):
                    print("\n\nError 발생 - log출력 !!!")
                    print("chk error : ", "error" in trnVal)

                    print("trnVal:name : ", trnVal["error"]['name'])
                    print("trnVal:message : ", trnVal["error"]['message'])
                    print("\n\n")

    if p0_open < p0_ma20 or p0_close < p0_ma20 :
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


    # 1초 간격으로 정보 가져오기
    time.sleep(1)
    # 현재 시각의 분 저장 --- cus. 하락시점 BB-M 아래위로 빈번한 매매 방지
    curTimeMinute = datetime.datetime.now().minute

    # while   End-->
