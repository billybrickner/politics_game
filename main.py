import collections
import random
import model
from model import *
import utils
from statistics import mean

voter_size_mod =1000
game_length=60

	
major_blocs = [Voter_Bloc("doctors",   1.0, "healthcare", healthcare=7),
		Voter_Bloc("dentists",  0.5, "candy", candy=1),
		Voter_Bloc("soldiers",  0.9, "military", military=7),
		Voter_Bloc("motorists", 0.7, "toll_roads", toll_roads=3), 
		Voter_Bloc("taxpayers", 0.4, "high_income_tax", "middle_income_tax", "low_income_tax", "capital_gains_tax", "property_tax"),
		]

all_issues = [Pol_Issue(name, random.random()) for name in utils.issue_names]
major_issues = collections.deque(random.sample(all_issues, k=5), maxlen=5)
all_voters = [Voter(f"voter{i:02}", utils.issue_names, major_blocs) for i in range(voter_size_mod)]


first_party= Party("keg", healthcare=4)
second_party= Party("pizza", candy=3)
third_party= Party("donner", welfare=1)
fourth_party= Party("birthday", military=7)

all_players = [first_party, second_party, third_party, fourth_party]
for each in all_players:
	each.add_talking_point(*random.sample(all_issues, k=4))

turn_order = utils.turn_sequence(all_players)
current_player = turn_order.get_current()

major_blocs[0].set_opinion(first_party,  0.1)
major_blocs[0].set_opinion(second_party, 0.1)
major_blocs[0].set_opinion(third_party,  0.1)
major_blocs[0].set_opinion(fourth_party, 0.1)			
#										   1
major_blocs[1].set_opinion(first_party,  0.1)
major_blocs[1].set_opinion(second_party, 0.1)
major_blocs[1].set_opinion(third_party,  0.1)
major_blocs[1].set_opinion(fourth_party, 0.1)
#										   1
major_blocs[2].set_opinion(first_party,  0.1)
major_blocs[2].set_opinion(second_party, 0.1)
major_blocs[2].set_opinion(third_party,  0.1)
major_blocs[2].set_opinion(fourth_party, 0.1)
#										   1
major_blocs[3].set_opinion(first_party,  0.1)
major_blocs[3].set_opinion(second_party, 0.1)
major_blocs[3].set_opinion(third_party,  0.1)
major_blocs[3].set_opinion(fourth_party, 0.1)
#										   1
major_blocs[4].set_opinion(first_party,  0.1)
major_blocs[4].set_opinion(second_party, 0.1)
major_blocs[4].set_opinion(third_party,  0.1)
major_blocs[4].set_opinion(fourth_party, 0.1)			

results = {"keg":0, "pizza":0, "donner":0, "birthday":0}


#-----------------------Utilities----------------------------------#

def name(subj):
	if type(subj) is Pol_Issue or type(subj) is Party or type(subj) is Voter_Bloc:
		return subj.name
	else:
		return str(subj)

def to_issue(targ):
	if type(targ) is Pol_Issue:
		return targ
	elif type(targ) is str:
		for i in all_issues:
			if name(i) == targ:
				return i
	else:
		return all_issues[5]

def int_voters(percentage, pop=voter_size_mod):
	return int(percentage*pop)

def check_outcome(d=6):
	return random.randint(1, d)
	
outcome_chart = {	1: "humiliating failure",
					2: "total failure",
					3: "less-than-desirable result",
					4: "lukewarm success",
					5: "notable success",
					6: "resounding success",
				}

#------------------------------------------------------------------#

def show_blocs():
	print("Major Players: ")
	for each in major_blocs:
		print(each)

def show_issues():
	print("Big Issues: ")
	for each in major_issues:
		print('\t', each)
		 

def show_display():
	pass
	
def show_party(player=current_player):
	pass




#-----------------------Offers-------------------------------------#
def offer_blocs(choices=major_blocs):
	print(f"Please select a bloc:")
	for b in range(len(choices)):
		print(f"{b}. {choices[b]}")
	sel = int(input())
	return choices[sel]

def offer_issues(choices=all_issues):
	print(f"Please select an Issue:")
	for b in range(len(choices)):
		print(f"{b}. {name(choices[b])}")
	sel = int(input())
	return to_issue(choices[sel])

def offer_parties():
	pass

#------------------------------------------------------------------#

#-----------------------POLLS--------------------------------------#
def poll(player=current_player):
	for each in random.sample(all_voters, k=10):
		print(each)

def check_issue(player=current_player):
	chosen = offer_issues()
	tally = 0
	for v in all_voters:
		if chosen in v.important_issues.keys():
			tally += 1
	print(f"{name(chosen)} is important to {tally} voters")

def get_opinion(player=current_player):
	avg_opinion = mean([v.get_approval_for_candidate(player, major_blocs, major_issues) for v in all_voters])
	print(f"The average opinion of {player.name} is {avg_opinion}")
	
def check_stance(player=current_player, strength=0.5):
	sel = offer_issues()
	num_surveyed = 0
	total_opinion = 0
	for v in all_voters:
		if sel in v.important_issues.keys() and random.random() > strength:
			num_surveyed += 1
			total_opinion += v.important_issues[sel]
	print(f"The average position among voters who responded was {total_opinion/num_surveyed}")
	

#------------------------------------------------------------------#
	
#-----------------------ISSUES-------------------------------------#

def rally(player=current_player):
	if len(player.talking_points)==0:
		print("you cannot hold a rally until you introduce some Talking Points; try having an interview first")
		return 0
	sel = offer_issues(player.talking_points)
	roll = check_outcome()
	print(f"your efforts to rally the people on {name(sel)} were reported to be a {outcome_chart[roll]}")
	temp = random.random()
	sel.strengthen(temp*(roll-3))
	if roll>4 and sel in player.stances.keys():
		print("You even managed to win some converts over to your way of thinking")
		for v in random.sample(all_voters, k=int_voters(0.025)):
			v.sway_opinion(sel, player.stances[sel], strength=(roll/10))

def interview(player=current_player):
	sel = offer_issues()
	for e in player.talking_points:
		print(name(e))
	player.add_talking_point(sel)
	roll = check_outcome()
	if roll > 5:
		for v in random.sample(all_voters, k=int_voters(0.025)):
			v.add_important_issue(sel)
	print(f"Trying to get people talking about {name(sel)} was a {outcome_chart[roll]}")
	while(roll>4):
		sel = offer_issues()
		player.add_talking_point(sel)
		roll = check_outcome()
		if roll > 5:
			for v in random.sample(all_voters, k=int_voters(0.025)):
				v.add_important_issue(sel)
		print(f"Trying to introduce {name(sel)} as one of your major talking points was a {outcome_chart[roll]}")

def speech(player=current_player):
	choices = list(player.stances.keys())
	#print(type(choices))
	sel = offer_issues(choices)
	roll = check_outcome()
	print(f"Your argument for {name(sel)} was hailed as a {outcome_chart[roll]}")
	for v in random.sample(all_voters, k=int_voters(0.15)):
		v.sway_opinion(sel, player.stances[sel], strength=(roll/8))
	if roll > 5:
		print("Your well-articulated points were enough to win over more voters than usual!")
		for v in random.sample(all_voters, k=int_voters(0.07)):
			v.sway_opinion(sel, player.stances[sel], strength=0.9)
	if roll < 2:
		Print("That was such a bad showing, it wouldn't be surprising if you drove some voters away from your position")
		for v in random.sample(all_voters, k=int_voters(0.04)):
			v.sway_opinion(sel, player.stances[sel], strength=0.05)

def debate(player=current_player):
	if len(player.talking_points)==0:
		print("you cannot attend a debate until you introduce some Talking Points; try having an interview first")
		return
	sel = offer_issues(player.talking_points)
	print(f"When asked about {name(sel)}, you made it clear that your position is...")
	if sel in player.stances.keys():
		print(f"Previous stance was {player.stances[sel]}")
	response = input("1-2-3-4-5-6-7")
	player.stances[sel] = int(response)
	roll = check_outcome()
	if roll >=3:
		print(f"Thanks to your efforts, {name(sel)} has entered the public discourse")
		major_issues.append(sel)
		for v in random.sample(all_voters, k=int_voters(0.05)):
			v.add_important_issue(sel)
	else:
		print(f"Your attempts to get people talking about {name(sel)} have failed")
	if roll > 5:
		print(f"It seems more people are talking about {name(sel)} than ever before!")
		for v in random.sample(all_voters, k=int_voters(0.05)):
			v.add_important_issue(sel)
#-----------------------------------------------------------------#

#-----------------------Blocs-------------------------------------#
def convention(player=current_player):
	sel = offer_blocs()
	roll = check_outcome()
	print(f"The convention was a {outcome_chart[roll]}!")
	sel.strengthen(player, random.random()*(roll-3))
	#if roll >4:
	#	print("
	

def benefit(player=current_player):
	sel = offer_blocs()
	roll = check_outcome()
	print(f"The benefit was a {outcome_chart[roll]}!")
	sel.adj_opinion(player, random.random()*(roll-3))
	if roll >4:
		print(f"It was such a success, it boosted the prominence of {name(sel)}")
#----------------------------------------------------------------#

#deck = ["benefit()", "convention()", "debate()", "speech()", "interview()", "rally()", "check_stance()", "get_opinion()", "check_issue()", "poll()"]
events = [benefit, convention, debate, speech, interview, rally, ]
polls =  [get_opinion, check_issue, check_stance, poll]

#campaign_sequence = 

def begin_turn(player):
	print(f"It is {name(player)}'s turn.")
	sel = int(input("1. show your Party's details\n 2. show the major issues\n 3. show the major blocs\n 4. draw for your turn\n"))
	while sel  != 4:
		if sel == 1:
			print(player)
		elif sel == 2:
			show_issues()
		elif sel == 3:
			show_blocs()
		sel = int(input("1. show your Party's details\n 2. show the major issues\n 3. show the major blocs\n 4. draw for your turn\n"))
	
	choices = polls
	for e in range(len(choices)):
		print(f"{e}. {choices[e]}")
	answer = int(input())
	print("You have chosen ", choices[answer])
	choices[answer](player)
	
	choices = events
	for e in range(len(choices)):
		print(f"{e}. {choices[e]}")
	answer = int(input())
	print("You have chosen ", choices[answer])
	choices[answer](player)
		
	
def hold_election():
	for each in all_voters:
		res = each.show_vote([first_party, second_party, third_party, fourth_party], major_blocs, major_issues)
		results[res] += 1
	print(results)

game_length = 40
while game_length > 0:
	begin_turn(current_player)
	game_length -= 1
	current_player = turn_order.next_turn()
