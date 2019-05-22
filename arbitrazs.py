from websocket import WebSocketApp
from json import dumps, loads
from pprint import pprint
import numpy as np



URL = "wss://ws-feed.gdax.com"
outfilename = "arbitrazs.txt"
outfile = open(outfilename,"a+")

class CryptoData:
	name = ""
	asks = []
	bids = []
	last_update = ""
	def __init__(self, name):
		self.name = name

	def parseData(self, msg):
		if msg["product_id"]==self.name:
			#print("%s - %s" % (self.name,msg))
			if msg["type"]=="snapshot":
				self.parseSnapshot(msg)
			if msg["type"]=="l2update":
				self.parseUpdate(msg)
			self.printBook()

	def parseSnapshot(self, msg):
		self.asks=[(float(msg["asks"][i][0]), float(msg['asks'][i][1])) for i in range(len(msg['asks']))]
		self.bids = [(float(msg["bids"][i][0]), float(msg['bids'][i][1])) for i in range(len(msg['bids']))]

	def parseUpdate(self, msg):
		#print(msg)
		self.last_update=msg["time"]
		for value in msg["changes"]:
			if (float(value[2]) == 0):
				priceToRemove = float(value[1])
				if value[0]=="sell":
					#print("before delete %s (%s)" % (len(self.asks), priceToRemove))
					self.asks = list(filter(lambda x : x[0] != priceToRemove, self.asks))
					#print("after delete %s" % (len(self.asks)))
				else:
					self.bids = list(filter(lambda x : x[0] != priceToRemove, self.bids))
			else:
				if value[0]=="sell":
					self.asks.append((float(value[1]), float(value[2])))
				else:
					self.bids.append((float(value[1]), float(value[2])))

	def printBook(self):
		self.asks=sorted(self.asks, key = lambda x: x[0]);
		self.bids=sorted(self.bids, key = lambda x: x[0], reverse = True);
		outfile.write("%s orderbook at %s was: \n" % (self.name,self.last_update))
		for i in range(min(len(self.asks),10)):
			outfile.write("%d \t %f %f \t --- \t %f %f \n" % (i,self.bids[i][0],self.bids[i][1],self.asks[i][0],self.asks[i][1]))

	def printBestLevel(self):
		outfile.write("%s best bid: %f, best ask: %f \n" % (self.name, self.bids[0][0], self.asks[0][0]))


r_BTCUSD = CryptoData("BTC-USD")
r_ETHUSD = CryptoData("ETH-USD")
r_ETHBTC = CryptoData("ETH-BTC")

def on_message(_, message):
	"""Callback executed when a message comes.
	Positional argument:
	message -- The message itself (string)
	"""
	global r_ask_BTCUSD, r_bid_BTCUSD, r_ask_ETHUSD, r_bid_ETHUSD, r_ask_ETHBTC, r_bid_ETHBTC, arbitrazs
	global time_ask_BTCUSD, time_bid_BTCUSD, time_ask_ETHUSD, time_bid_ETHUSD, time_ask_ETHBTC, time_bid_ETHBTC, time_all
	a = loads(message)
	r_BTCUSD.parseData(a)
	r_ETHUSD.parseData(a)
	r_ETHBTC.parseData(a)

    #--------------------------------------------------------------------------------------------
    #-------------MŰVELETEK AZ ORDERBOOKKAL------------------------------------------------------------

	arbitrazs_1=1-((r_ETHBTC.bids[0][0]*r_BTCUSD.bids[0][0])/r_ETHUSD.bids[0][0])
	arbitrazs_2=1-(r_ETHUSD.asks[0][0]/(r_ETHBTC.bids[0][0]*r_BTCUSD.bids[0][0]))
	r_BTCUSD.printBestLevel()
	r_ETHUSD.printBestLevel()
	r_ETHBTC.printBestLevel()
	outfile.write("arbitrazs_1: %f\n" % (arbitrazs_1))
	outfile.write("arbitrazs_2: %f\n" % (arbitrazs_2))



def on_open(socket):
    """Callback executed at socket opening.
    Keyword argument:
    socket -- The websocket itself
    """
    params = {

    "type": "subscribe",
    "channels": [
        {
            "name": "level2",
            "product_ids": [
                "ETH-USD",
                "BTC-USD",
                "ETH-BTC"
            ],
        },
        ]
    }

    socket.send(dumps(params))

def main():
	print("Getting orderbook from %s....\noutput is writing to %s" % (URL,outfilename))
	ws = WebSocketApp(URL, on_open=on_open, on_message=on_message)
	ws.run_forever()
	outfile.close()


if __name__ == '__main__':
    main()
    #print(time_ask_BTCUSD[0], time_ask_BTCUSD[int(len(time_ask_BTCUSD)/3)], time_ask_BTCUSD[int(2*len(time_ask_BTCUSD)/3)], time_ask_BTCUSD[len(time_ask_BTCUSD)-1], i)
