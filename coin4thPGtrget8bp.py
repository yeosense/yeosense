import pyupbit
import datetime
import time
import requests
import pandas as pd


def setTicker(ticker):
    pass


class Trade:
    def __init__(self):
        #############################
        # variables
        #############################
        # ticker
        self.ticker = "KRW-AXS"

        # balance
        self.balance = 0

        # check Gold time
        self.upbit = pyupbit.Upbit
        self.pGBuy_ma   = False
        self.pGSell_ma  = False
        self.pGBuy_cci  = False
        self.pGSell_cci = False
        self.pGoldZone_ma   = False
        self.pGoldZone_macd = False
        self.status_ma20: str = "DOWN"
        self.trade = False

        # for macd
        self.macd = 0

    #############################
    # functions
    #############################

    # getTime() - print current time
    def getTime(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    #############################
    # 0. upbit connect
    #############################
    def connUpbit(self):
        print("#############################")
        print("# upbit connect")
        print("#############################")
        access = "D7WHZTDtvkBZzx4K1gpj5xlqwh5xxa8Xxluzkv6Z" # personal access key
        secret = "R5FYPkcl8szmMzvtlfKn4wZMeGoe1XmHvIkXmERH" # personal secret key
        self.upbit = pyupbit.Upbit(access, secret)
        print(self.upbit )
        print("upbit connected..\n")
        setTicker(self.ticker)


    # Commodity Channel Index
    def cci(self, df, ndays):
        df['TP'] = (df['high'] + df['low'] + df['close']) / 3
        df['sma'] = df['TP'].rolling(ndays).mean()
        df['mad'] = df['TP'].rolling(ndays).apply(lambda x: pd.Series(x).mad())
        df['CCI'] = (df['TP'] - df['sma']) / (0.015 * df['mad'])
        return df

    # RSI
    def rsi(self, ohlc: pd.DataFrame, period: int = 14):
        ohlc["trade_price"] = ohlc["trade_price"]
        delta = ohlc["trade_price"].diff()
        gains, declines = delta.copy(), delta.copy()
        gains[gains < 0] = 0
        declines[declines > 0] = 0

        _gain = gains.ewm(com=(period - 1), min_periods=period).mean()
        _loss = declines.abs().ewm(com=(period - 1), min_periods=period).mean()

        RS = _gain / _loss
        return pd.Series(100 - (100 / (1 + RS)), name="RSI")

    def setTicker(ticker):
        # set ticker
        print("set tr ticker :", ticker)
        # ticker - get 1st sell call
        ticker.get1stSellCall(ticker)


    def get1stSellCall(ticker):
        print("ticker - sell 1st call : ", pyupbit.get_current_price(ticker))
        print()


    #############################
    # 1. current KRW balance
    #############################

    def getBalance(self):
        print("#############################")
        print("# current KRW balance")
        print("#############################")
        # get current KRW
        if( self.upbit.get_balance("KRW") is None ) :
            self.balance = 0
            print("balance : None ", 0)  # get current KRW
        else:
            self.balance = self.upbit.get_balance("KRW")
            print("balance : ", self.balance )  # get current KRW
            print("보유 KRW 조회 : {0:>10,} 원".format(int(self.balance )))  # get current KRW

        print()


    #############################
    # 2. print current time
    #############################
    def getCurTime(self):
        print("current time :", self.getTime())


    #############################
    # 3. start trading
    #############################
    def startTrading(self):
        print("#############################")
        print("# start trading")
        print("#############################")

        # time
        curTimeMinute = datetime.datetime.now().minute
        lastTradingSellTimeMinute = (datetime.datetime.now() + datetime.timedelta(minutes=-1)).minute
        lastTradingBuyTimeMinute = (datetime.datetime.now() + datetime.timedelta(minutes=-1)).minute
        # balance
        balance = 0

        while True:
            # DataFrame
            self.getCurTime()
            print(self.ticker)
            df = pyupbit.get_ohlcv(self.ticker, interval="minute1")

            ################################################################################################################
            # calc. CCI

            df = self.cci(df, 14)
            p1_cci = df['CCI'][-2]
            p0_cci = df['CCI'][-1]

            pGBuy_cci = False
            pGSell_cci = False

            # buy#1
            if p1_cci < -100 and p0_cci > -100 :
                pGBuy_cci = True
            else :
                pGBuy_cci = False
            # buy#2
            if p1_cci < 100 and p0_cci > 100 :
                pGBuy_cci = True
            else :
                pGBuy_cci = False

            # sell#1
            if p1_cci > 100 and p0_cci < 100 :
                pGSell_cci = True
            else :
                pGSell_cci = False

            # sell#2
            if p1_cci > -100 and p0_cci < -100 :
                pGSell_cci = True
            else :
                pGSell_cci = False

            #print('p1_cci: ', p1_cci)
            #print('p0_cci: ', p0_cci)
            #print('pGBuy_cci: ', pGBuy_cci)
            #print('pGSell_cci: ', pGSell_cci)


            ################################################################################################################
            # calc. ma

            # 이동평균선 5
            ma5  = df['close'].rolling(window=5).mean()
            # 이동평균선 10
            ma10 = df['close'].rolling(window=10).mean()
            # ticker's current price
            cur_price = pyupbit.get_current_price(self.ticker)

            p1_ma5 = ma5[-2]    # current - 1
            p0_ma5 = ma5[-1]    # current
            p1_ma10 = ma10[-2]  # current - 1
            p0_ma10 = ma10[-1]  # current

            # Gold-cross - buy timing
            if p0_ma5 > p0_ma10 and p1_ma5 < p1_ma10 :
                pGBuy_ma = True
            else:
                pGBuy_ma = False

            # Death-cross - sell timing
            if p0_ma5 < p0_ma10 and p1_ma5 > p1_ma10 :
                pGSell_ma = True
            else:
                pGSell_ma = False

            # Gold zone - after Gold-cross & before Death-cross
            if p0_ma5 > p0_ma10 :
                pGoldZone_ma = True
            else:
                pGoldZone_ma = False

            #print("pGBuy_ma : ", pGBuy_ma)
            #print("pGSell_ma : ", pGSell_ma)
            #print("pGoldZone_ma : ", pGoldZone_ma)
            #print()


            ################################################################################################################
            # macd

            url = "https://api.upbit.com/v1/candles/minutes/1"
            querystring = {"market": self.ticker, "count": "100"}
            response = requests.request("GET", url, params=querystring)
            data = response.json()
            df0 = pd.DataFrame(data)
            df1 = df0.iloc[::-1]
            df1 = df1['trade_price']

            exp1 = df1.ewm(span=12, adjust=False).mean()
            exp2 = df1.ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            exp3 = macd.ewm(span=9, adjust=False).mean()

            #print('MACD: ', macd[0])
            #print('Signal: ', exp3[0])
            p0_macd = macd[0]

            p1 = macd[1] - exp3[1]
            p0 = macd[0] - exp3[0]

            #print('p1: ', p1)
            #print('p0: ', p0)

            pGBuy_macd = False
            pGSell_macd = False

            if p0 > 0 and p1 < 0 :
                pGBuy_macd = True
                pGSell_macd = False

            if p0 < 0 and p1 > 0 :
                pGBuy_macd = False
                pGSell_macd = True

            if p0 > 0 :
                pGoldZone_macd = True
            else :
                pGoldZone_macd = False

            #print("pGBuy_macd : ", pGBuy_macd)
            #print("pGSell_macd : ", pGSell_macd)

            ################################################################################################################
            # rsi
            df2 = df0.reindex(index=df0.index[::-1]).reset_index()
            p1_rsi = self.rsi(df2, 14).iloc[-2]
            p0_rsi = self.rsi(df2, 14).iloc[-1]
            #print("p1 rsi : ", str(p1_rsi))
            #print("p0 rsi : ", str(p0_rsi))

            pGBuy_rsi = False
            pGSell_rsi = False

            # buy#1
            if p1_rsi < 30 and p0_rsi > 30:
                pGBuy_rsi = True
            else :
                pGBuy_rsi = False

            # buy#20
            if p1_rsi < 70 and p0_rsi > 70 :
                pGBuy_rsi = True
            else :
                pGBuy_rsi = False

            # sell#1
            if p1_rsi > 70 and p0_rsi < 70 :
                pGSell_rsi = True
            else :
                pGSell_rsi = False

            # sell#2
            if p1_rsi > 30 and p0_rsi < 30 :
                pGSell_rsi = True
            else :
                pGSell_rsi = False

            ################################################################################################################
            ################################################################################################################

            # Do not trade
            if pGoldZone_macd == False :
                pGBuy_ma  = False

            # control trade
            if p0_macd < 0 :
                self.trade = False
            else:
                self.trade = True

            ################################################################################################################
            ################################################################################################################

            print("trade, pGBuy_rsi , pGBuy_cci , pGBuy_macd , pGBuy_ma  - ", self.trade, pGBuy_rsi , pGBuy_cci , pGBuy_macd , pGBuy_ma)
            print("trade, pGSell_rsi, pGSell_cci, pGSell_macd, pGSell_ma - ", self.trade, pGSell_rsi, pGSell_cci, pGSell_macd, pGSell_ma)

            ################################################################################################################
            #
            # set Buy timing
            #
            if self.trade == True and (pGBuy_rsi == True or pGBuy_cci == True or pGBuy_macd == True or pGBuy_ma == True) :
                # buy minute
                lastTradingBuyTimeMinute = datetime.datetime.now().minute

                print("buy !!!")
                balance = self.upbit.get_balance("KRW")

                if balance is None :
                    balance = 0

                print("balance : ", balance)  # 보유 현금 잔액조회
                print("보유 KRW 조회 : {0:>10,} 원".format(int(balance)))  # 보유 현금 조회

                if lastTradingSellTimeMinute != curTimeMinute:
                    ## 최근 매도 시점의 분과 현재 분이 같으면 매수 제한함  --- cus. 하락시점 BB-M 아래위로 빈번한 매매 방지
                    # 현재 보유코인 잔액 조회 후, 수수료 금액(0.05%(0.0005)) 제외한 금액으로 매수
                    trnVal = self.upbit.buy_market_order(self.ticker, balance * 0.9995)
                    # trnVal = "pass"
                    print("rtnVal #B: ", trnVal)

            #
            # set Sell timing
            #
            if (pGSell_rsi == True or pGSell_cci == True or pGSell_macd == True or pGSell_ma == True):
                # sell minute
                lastTradingSellTimeMinute = datetime.datetime.now().minute

                # sell
                print("sell !!!")
                # 현재 보유코인 잔액 조회 후, 수수료 금액(0.05%(0.0005)) 제외한 금액으로 매도
                balance = self.upbit.get_balance(self.ticker)

                if balance is None :
                    balance = 0

                print("보유 코인 balance : ", balance)  # 보유 코인 잔액조회
                print("수수료 : ", float(balance) * 0.0005)  # 수수료
                print("투자액 : ", float(balance) * 0.9995)  # 투자액
                print()

                if lastTradingBuyTimeMinute != curTimeMinute:
                    ## 최근 매수 시점의 분과 현재 분이 같으면 매도 제한함  --- cus. 하락시점 BB-M 아래위로 빈번한 매매 방지
                    trnVal = self.upbit.sell_market_order(self.ticker, balance * 0.9995)
                    # trnVal = "pass"
                    print("rtnVal #S: ", trnVal)


            ################################################################################################################
            # 0.0001초 간격으로 정보 가져오기
            time.sleep(0.001)
            # save current minute --- cus. prevent buy&sell in a minute
            curTimeMinute = datetime.datetime.now().minute
            print()
            ################################################################################################################


def main():
    t = Trade()
    t.connUpbit()         # connect upbit
    t.getBalance()        # get balance
    t.startTrading()      # start trading




if __name__ == '__main__':
    main()
