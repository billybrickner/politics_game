import random
import collections

class Voter():
	def __init__(self, name, possible_issues, blocs):
		self.name = name
		self.important_issues = dict()
		self.internal_preferences = dict()
		temp = random.random()
		if temp > 0.3:
			i = random.choice(possible_issues)
			self.important_issues[i] = random.randint(1, 8)
			self.internal_preferences[i] = 0.3
		if temp > 0.6:
			i = random.choice(possible_issues)
			self.important_issues[i] = random.randint(1, 8)
			self.internal_preferences[i] = 0.6
		if temp > 0.9:
			i = random.choice(possible_issues)
			self.important_issues[i] = random.randint(1, 8)
			self.internal_preferences[i] = 0.9
		self.interested_issues = set(random.choices(possible_issues, k=random.randint(3, 6)))
		self.apply_blocs(*blocs)
		#print(self)
	
	def apply_blocs(self, *args):
		for bloc in args:
			for bloc_issues in bloc.interested_issues:
				if bloc_issues in self.interested_issues:
					if bloc.name in self.internal_preferences.keys():
						self.internal_preferences[bloc.name] += 0.2
					else:
						bloc.members += 1
						self.internal_preferences[bloc.name] = 0.3
		
	def get_preference_for_bloc(self, bloc):
		if bloc.name in self.internal_preferences.keys():
			return bloc.strength * self.internal_preferences[bloc.name]
		else:
			return 0
	
	def get_preference_for_issue(self, issue):
		if issue.name in self.important_issues.keys():
			return issue.strength * self.internal_preferences[issue.name]
		else:
			return 0
	
	def get_preference_for_candidate(self, candidate, blocs, issues, verbose=False):
		if verbose:
			print(f"{self.name} calculating approval for candidate:{candidate.name}")
		total_approval = 0
		for bloc in blocs:
			if verbose:
				print(f"for bloc : {bloc.name}")
			bloc_preference = self.get_preference_for_bloc(bloc)
			total_approval += bloc_preference * bloc.get_cand_pref(candidate)
			if verbose:
				print(total_approval)
		for issue in issues:
			if verbose:
				print(f"for issue : {issue.name}")
			issue_preference = self.get_preference_for_issue(issue)
			agreement = 0
			if issue_preference:
				agreement = candidate.get_agreement(issue.name, self.important_issues[issue.name])
			total_approval += issue_preference * agreement
			if verbose:
				print(total_approval)
		if verbose:
				print("final approval: ", total_approval)
		return total_approval
	
	def calc_vote(self, candidates, blocs, issues):
		preferences = dict()
		for each in candidates:
			temp = self.get_preference_for_candidate(each, blocs, issues) + (random.random()/10000)
			preferences[temp] = each.name
		choice = max(preferences.keys())
		return preferences[choice]
	
	def show_vote(self, candidates, blocs, issues):
		temp = self.calc_vote(candidates, blocs, issues)
		#print(self.name, " : ", temp)
		return temp

	def __str__(self):
		ret = self.name + " : " + "\n\t" + str(self.important_issues) + "\n\t" + str(self.interested_issues) + "\n\t" + str(self.internal_preferences)
		return ret


class Voter_Bloc():
	def __init__(self, name, strength, *args, **kwargs):
		self.name = name
		self.strength = strength
		self.interested_issues = list(args)
		self.important_issues = kwargs
		self.party_pref = dict()
		self.members = 0
		
	def set_cand_pref(self, subj_party, desire):
		self.party_pref[subj_party.name] = desire
		
	def get_cand_pref(self, cand):
		if cand.name in self.party_pref.keys():
			return self.party_pref[cand.name]
		else:
			return 0
	
	def __str__(self):
		return f"{self.name} : \n\t {self.important_issues} \n\t{self.interested_issues} \n\tStrength: {self.strength}    Members: {self.members}"

	
class Pol_Issue():
	def __init__(self, name, strength):
		self.name = name
		self.strength = strength

	def __str__(self):
		return f"{self.name} : {self.strength}"

class Party():
	def __init__(self, name, **kwargs):
		self.name = name
		self.important_issues = kwargs
		
	def get_agreement(self, issue, pos):
		if issue in self.important_issues.keys():
			temp = self.important_issues[issue]
			if temp == pos:
				return 2
			if (pos - 1) == temp or (pos+1) == temp:
				return 1.5
			if (pos-2) ==temp or (pos+2) == temp:
				return 1
			if (pos-3)==temp or (pos+3) == temp:
				return -0.5
			return -1
		else:
			return 0


valid_issues=[
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
	
all_issues = [Pol_Issue(name, random.random()) for name in valid_issues]
major_issues = collections.deque(random.sample(all_issues, k=5), maxlen=5)
def show_isues():
	print("Big Issues: ")
	for each in major_issues:
		print('\t', each)
	
all_blocs = [Voter_Bloc("doctors",   1.0, "healthcare", healthcare=7),
		Voter_Bloc("dentists",  0.5, "candy", candy=1),
		Voter_Bloc("soldiers",  0.9, "military", military=7),
		Voter_Bloc("motorists", 0.7, "toll_roads", toll_roads=3), 
		Voter_Bloc("taxpayers", 0.4, "high_income_tax", "middle_income_tax", "low_income_tax", "capital_gains_tax", "property_tax"),
		]
def show_blocs():
	print("Major Players: ")
	for each in all_blocs:
		print(each)
		 
all_voters = [Voter(f"voter{i:02}", valid_issues, all_blocs) for i in range(400)]

first_party= Party("keg", healthcare=4)
second_party= Party("pizza", candy=3)
third_party= Party("donner", welfare=1)
fourth_party= Party("birthday", military=7)

all_blocs[0].set_cand_pref(first_party,  0.5)
all_blocs[0].set_cand_pref(second_party, 0.5)
all_blocs[0].set_cand_pref(third_party,  0.5)
all_blocs[0].set_cand_pref(fourth_party, 0.5)			

all_blocs[1].set_cand_pref(first_party,  0.5)
all_blocs[1].set_cand_pref(second_party, 0.5)
all_blocs[1].set_cand_pref(third_party,  0.5)
all_blocs[1].set_cand_pref(fourth_party, 0.5)

all_blocs[2].set_cand_pref(first_party,  0.5)
all_blocs[2].set_cand_pref(second_party, 0.5)
all_blocs[2].set_cand_pref(third_party,  0.5)
all_blocs[2].set_cand_pref(fourth_party, 0.5)

all_blocs[3].set_cand_pref(first_party,  0.5)
all_blocs[3].set_cand_pref(second_party, 0.5)
all_blocs[3].set_cand_pref(third_party,  0.5)
all_blocs[3].set_cand_pref(fourth_party, 0.5)

all_blocs[4].set_cand_pref(first_party,  0.5)
all_blocs[4].set_cand_pref(second_party, 0.5)
all_blocs[4].set_cand_pref(third_party,  0.5)
all_blocs[4].set_cand_pref(fourth_party, 0.5)			

results = {"keg":0, "pizza":0, "donner":0, "birthday":0}

turn_order = collections.deque([first_party, second_party, third_party, fourth_party])
current_player = turn_order[0]

def poll():
	for each in random.sample(all_voters, k=10):
		print(each)

def check_issue():
	print("Select an Issue:\n")
	for i in len(all_issues):
		print(f"\t{i}. {all_issues[i]}\n")
	sel = int(input())

def rally():
	print("Select an Issue:\n")
	for i in len(major_issues):
		print(f"\t{i}. {major_issues[i]}\n")
	sel = major_issues[int(input())]
	sel.strength += random.random()/4
	show_issues()

def speech():
	print("Select an Issue:\n")
	for i in len(all_issues):
		print(f"\t{i}. {all_issues[i]}\n")
	sel = all_issues[int(input())]
	major_issues.append(sel)
	show_issues()
	
def convention():
	print("Select a Bloc:\n")
	for i in len(all_blocs):
		print(f"\t{i}. {all_blocs[i]}\n")
	sel = int(input())
	sel.party_pref[p1.name] += random.random()/10
	print(f"{sel.name}'s approval of {p1.name} is now {sel.party_pref[p1.name]}")
	sel.strength += (random.random() - random.random())/10

def set_stance():
	print("Select an Issue:\n")
	for i in len(major_issues):
		print(f"\t{i}. {major_issues[i]}\n")
	sel = major_issues[int(input())]
	position = int(input())
	p1.important_issues[sel.name] = position
	print(p1)

def end_turn():
	turn_order.rotate()
	current_player = turn_order[0]

def show_issues():
	print("Active Issues: \n")
	for each in major_issues:
		print(each)

def hold_election():
	for each in all_voters:
		res = each.show_vote([first_party, second_party, third_party, fourth_party], all_blocs, major_issues)
		results[res] += 1
	print(results)