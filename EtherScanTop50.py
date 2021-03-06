from html.parser import HTMLParser
import urllib.request
import time

starting_time = time.time()

total_supply_api = 'https://api.etherscan.io/api?module=stats&action=tokensupply&contractaddress='
token_top50_url = 'https://etherscan.io/token/generic-tokenholders2?a='

token_supply = dict()
with open("token_supply.txt", "r+") as token_supply_file:
    for line in token_supply_file:
        (key,value) = line.split(" ")
        token_supply[key] = value[:-1]

token_supply_file = open("token_supply.txt", "a")
token_symbol_file = open("token_symbol.json", "w+")
token_symbol_file.write("[")

class TokenTop50Parser(HTMLParser):
    def __init__(self, token_symbol):
        HTMLParser.__init__(self)
        self.round = 0
        self.isTd = 0
        self.file = open("TokenData/" + token_symbol + ".json", "w+")
        self.file.write("[")

    def handle_starttag(self, tag, attrs):
        if(tag == 'td'):
            self.isTd = 1

    def handle_endtag(self, tag):
        if(tag == 'td'):
            self.isTd = 0
        elif(tag == 'table'):
            self.file.write("{\"status\":\"eof\"}]")

    def handle_data(self, data):
        if(self.isTd == 1):
            self.round += 1
            if(self.round == 1):
                self.file.write("{\"rank\":\"" + data + "\",")
            elif(self.round == 2):
                self.file.write("\"address\":\"" + data + "\",")
            elif(self.round == 3):
                self.file.write("\"amount\":\"" + data + "\",")
            elif(self.round == 4):
                self.file.write("\"percentage\":\"" + data + "\"},")
                self.round = 0


class Top50TokenParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.isTd = 0
        self.isH5 = 0

        self.token_address = 0

    def handle_starttag(self, tag, attrs):
        if(tag == 'td'):
            self.isTd = 1
        elif(tag == 'h5'): #enter the address and Name section
            self.isH5 = 1
        elif(tag == 'a' and self.isH5 == 1):
            for name, value in attrs:
                if(name == 'href'):
                    self.token_address = value[9:-2]
                    print(self.token_address) #contract address
    
    def handle_data(self, data):
        if(self.isH5 == 1):
            token_symbol = data[data.index('(')+1:data.index(')')]
            print("Symbol:" + token_symbol) #symbol
            token_symbol_file.write("{\"symbol\":\"" + token_symbol + "\"},")

            #get total supply of the account
            token_total_supply = token_supply.get(self.token_address)

            if(token_total_supply == None):
                supply_request = urllib.request.Request(total_supply_api + self.token_address, headers={'User-Agent': 'Mozilla/5.0'})
                tem_str = str(urllib.request.urlopen(supply_request).read())

                token_total_supply = tem_str[tem_str.index("result")+9:-3]
                print(token_total_supply) # total supply

                token_supply[self.token_address] = token_total_supply #store in dictionary
                token_supply_file.write(self.token_address + " " + token_total_supply + "\n") #write in file
            else:
                print("Cache:" + token_total_supply)

            token_top50_request = urllib.request.Request(token_top50_url + self.token_address + "&s=" + token_total_supply, headers={'User-Agent': 'Mozilla/5.0'})
            tem_str = str(urllib.request.urlopen(token_top50_request).read())

            tokenTop50Parser = TokenTop50Parser(token_symbol)
            tokenTop50Parser.feed(tem_str)

    def handle_endtag(self, tag):
        if(tag == 'td'):
            self.istd = 0
        elif(tag == 'h5'):
            self.isH5 = 0

# Initial a info parser
top50Token = Top50TokenParser()

#given the url of the list of top 50 tokens
top50TokenUrl = 'https://etherscan.io/tokens?p=' + '1'

request = urllib.request.Request(top50TokenUrl, headers={'User-Agent': 'Mozilla/5.0'})

webpage = urllib.request.urlopen(request).read()
top50Token.feed(str(webpage))

token_symbol_file.write('{"status":"eof"}]')

print("Cost: " + str(time.time() - starting_time))