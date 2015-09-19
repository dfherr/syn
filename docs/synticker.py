# /usr/bin/env python2

import optparse
import sys
from time import sleep
import urllib2

#############################
## Option-Parser
#############################
optpar = optparse.OptionParser()
optpar.add_option("-N", "--NRG", type="int", dest="flag_n", default=0, help="Energy")
optpar.add_option("-E", "--Erz", type="int", dest="flag_e", default=0, help="Erz")
optpar.add_option("-F", "--FP", type="int", dest="flag_f", default=0, help="Forschungspunkte")
optpar.add_option("-R", "--Ranger", type="int", dest="flag_r", default=0, help="Ranger")
optpar.add_option("-M", "--Marine", type="int", dest="flag_m", default=0, help="Marine")
optpar.add_option("-B", "--BUC", type="int", dest="flag_b", default=0, help="BUC")
optpar.add_option("-A", "--AUC", type="int", dest="flag_a", default=0, help="AUC")
optpar.add_option("-H", "--HUC", type="int", dest="flag_h", default=0, help="HUC")
optpar.add_option("-T", "--Thief", type="int", dest="flag_t", default=0, help="Thief")
optpar.add_option("-G", "--Guardian", type="int", dest="flag_g", default=0, help="Guardian")
optpar.add_option("-a", "--Agent", type="int", dest="flag_ag", default=0, help="Agent")
(option, arg) = optpar.parse_args()

#############################
## User-Settings
#############################
NICK = "msslx"
PASSWORD = "XP.USNx9"

#############################
## Articles
#############################
class Article:
	def __init__(self, name, sell_price, price, count):
		self.name = name
		self.sell_price = sell_price
		self.values = (price, count)

	def setValues(self, price, count):
		if self.values != (price, count) and price != '' and self.sell_price != 0:
			if self.sell_price:
				print "\n" + self.name + ": Price " + str(self.values[0]) + " -> " + str(price) \
					  + " Count " + str(self.values[1]) + " -> " + str(count), "\a",
				sys.stdout.flush()
			if (int(self.values[0]) == int(self.sell_price) and int(self.values[1]) > int(count) and int(price) >= int(
					self.sell_price)) or (
								int(self.sell_price) < int(price) and int(self.values[0]) != 0 and int(self.values[0]) < int(
							self.sell_price)):
				print "--> VERKAUFT",
				signal(2)
			self.values = (price, count)
			if int(self.values[0]) == int(self.sell_price) and self.sell_price != 0:
				print "--> ANGEBOT ONLINE",
				signal(1)


#############################
## Get Source from url
#############################
def source(url):
	try:
		xml = urllib2.urlopen(urllib2.Request(url)).read()
	except:
		print "Failed!"
		signal(5)
	return xml


#############################
## Sound Signal
#############################
def signal(signal_count):
	for i in xrange(signal_count):
		sleep(0.33)
		print "\a",
		sys.stdout.flush()


#############################
## Article Price / Number
#############################
def getValues(xml, article):
	startSearch = article
	startSearchPos = xml.find(article)
	pricePosStart = xml.find('<price>', startSearchPos) + 7
	pricePosEnd = xml.find('</price>', startSearchPos)
	countPosStart = xml.find('<number>', startSearchPos) + 8
	countPosEnd = xml.find('</number>', startSearchPos)
	return (xml[pricePosStart:pricePosEnd], xml[countPosStart:countPosEnd])

#############################
## Run Skript
#############################
if __name__ == "__main__":
	URL = "http://basic.syndicates-online.de/export.php?action=market&username=" + NICK + "&password=" + PASSWORD
	xml = source(URL)
	# correct access
	if xml.find("Invalid authentification data!") == -1:
		# market products
		energy = Article("Energy", option.flag_n, 0, 0)
		erz = Article("Erz", option.flag_e, 0, 0)
		fp = Article("Forschungspunkte", option.flag_f, 0, 0)
		ranger = Article("Ranger", option.flag_r, 0, 0)
		rines = Article("Marine", option.flag_m, 0, 0)
		buc = Article("BUC", option.flag_b, 0, 0)
		auc = Article("AUC", option.flag_a, 0, 0)
		huc = Article("HUC", option.flag_h, 0, 0)
		thief = Article("Thief", option.flag_t, 0, 0)
		guardian = Article("Guardian", option.flag_g, 0, 0)
		agent = Article("Agent", option.flag_ag, 0, 0)
		# repeat until KeyboardInterrupt
		try:
			while True:
				# update Products
				values = getValues(xml, "Energie")
				energy.setValues(values[0], values[1])
				values = getValues(xml, "Erz")
				erz.setValues(values[0], values[1])
				values = getValues(xml, "Forschungspunkte")
				fp.setValues(values[0], values[1])
				values = getValues(xml, "Marine")
				rines.setValues(values[0], values[1])
				values = getValues(xml, "Ranger")
				ranger.setValues(values[0], values[1])
				values = getValues(xml, "Wartank")
				auc.setValues(values[0], values[1])
				values = getValues(xml, "Strike Fighter")
				buc.setValues(values[0], values[1])
				values = getValues(xml, "Titan")
				huc.setValues(values[0], values[1])
				values = getValues(xml, "Thief")
				thief.setValues(values[0], values[1])
				values = getValues(xml, "Guardian")
				guardian.setValues(values[0], values[1])
				values = getValues(xml, "Agent")
				agent.setValues(values[0], values[1])
				# wait for reload
				print ".",
				sys.stdout.flush()
				sleep(15)
				xml = source(URL)

		except KeyboardInterrupt:
			print "GG!"
	else:
		print xml
