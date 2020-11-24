import collections
import random

issue_names=[
	"healthcare", 
	"welfare",
	"military", 
	"candy",
	"immigration",
	"high_income_tax", 
	"middle_income_tax",
	"low_income_tax",
	"capital_gains_tax",
	"property_tax",
	"industrial_subsidies",
	"agricultural_subsidies",
	"childcare_benefits",
	"space_program",
	"toll_roads",
	"rail_expansion",
	]

class turn_sequence():
	def __init__(self, players):
		self.index = 0
		self.player_list = players
	
	def get_current(self):
		return self.player_list[self.index]
		
	def next_turn(self):
		#print("next turn")
		self.index += 1
		#print("index", self.index)
		if self.index >= len(self.player_list):
			self.index = 0
		#print("ret= ", self.player_list[self.index])
		return self.player_list[self.index]

	def get_next(self):
		temp = (self.index + 1) % len(self.player_list)
		return self.player_list[temp]
		
def flip():
	temp = random.randint(0, 1)
	if temp == 0:
		return -1
	else:
		return 1
		
