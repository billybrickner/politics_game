import random

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
		
	def apply_blocs(self, *args):
		for bloc in args:
			for bloc_issues in bloc.interested_issues:
				if bloc.name in self.internal_preferences.keys():
					self.internal_preferences[bloc.name] += 0.2
				else:
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
			
	def get_preference_for_candidate(self, candidate, blocs, issues):
		total_approval = 0
		for bloc in blocs:
			bloc_preference = self.get_preference_for_bloc(bloc)
			total_approval += bloc_preference * bloc.get_cand_pref(candidate)
		for issue in issues:
			issue_preference = self.get_preference_for_issue(issue)
			agreement = 0
			if issue_preference:
				agreement = candidate.get_agreement(issue.name, self.important_issues[issue.name])
			total_approval += issue_preference * agreement
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
		
	def set_cand_pref(self, subj_party, desire):
		self.party_pref[subj_party.name] = desire
		
	def get_cand_pref(self, cand):
		if cand.name in self.party_pref.keys():
			return self.party_pref[cand.name]
		else:
			return 0
	
	def __str__(self):
		return self.name + " : " + "\n\t" + str(self.important_issues) + "\n\t" + str(self.interested_issues)
		

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
	]
all_issues = [Pol_Issue(name, random.random()) for name in valid_issues]
t_pi = random.choices(all_issues, k=5)
print("Big Issues: ")
for each in t_pi:
	print('\t', each)
	
t_vb = [Voter_Bloc("doctors", 1, "healthcare", healthcare=7),
		Voter_Bloc("dentists", 0.5, "candy", candy=1),
		]			
print("Major Players: ")
for each in t_vb:
	print(each)
	
all_voters = [Voter(f"voter{i:02}", valid_issues, t_vb) for i in range(400)]

first_party= Party("keg", healthcare=4)
second_party= Party("pizza", candy=3)
third_party= Party("donner", welfare=1)
fourth_party= Party("birthday", military=7)

t_vb[0].set_cand_pref(first_party,  0.5)
t_vb[0].set_cand_pref(second_party, 0.5)
t_vb[0].set_cand_pref(third_party,  0.5)
t_vb[0].set_cand_pref(fourth_party, 0.5)			
			
t_vb[1].set_cand_pref(first_party,  0.5)
t_vb[1].set_cand_pref(second_party, 0.5)
t_vb[1].set_cand_pref(third_party,  0.5)
t_vb[1].set_cand_pref(fourth_party, 0.5)

#t_vb[0].set_cand_pref(first_party, 0.5)
#t_vb[0].set_cand_pref(first_party, 0.5)
#t_vb[0].set_cand_pref(first_party, 0.5)
#t_vb[0].set_cand_pref(first_party, 0.5)			

results = {"keg":0, "pizza":0, "donner":0, "birthday":0}

for each in all_voters:
	res = each.show_vote([first_party, second_party, third_party, fourth_party], t_vb, t_pi)
	results[res] += 1
	
print(results)