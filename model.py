import random
import collections
import utils

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
		self.stubbornness = 0 
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
	
	def get_approval_for_candidate(self, candidate, blocs, issues, verbose=False):
		if verbose:
			print(f"{self.name} calculating approval for candidate:{candidate.name}")
		total_approval = 0
		for bloc in blocs:
			if verbose:
				print(f"for bloc : {bloc.name}")
			bloc_preference = self.get_preference_for_bloc(bloc)
			total_approval += bloc_preference * bloc.get_opinion(candidate)
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
	
	def add_important_issue(self, issue, strength=0.5):
		temp = random.random()
		if temp > 0.9:
			self.important_issues[issue.name] = random.randint(1, 8)
			self.internal_preferences[issue.name] = 0.9
		elif temp > 0.7:
			self.important_issues[issue.name] = random.randint(1, 8)
			self.internal_preferences[issue.name] = 0.6
		elif temp > 0.5:
			self.important_issues[issue.name] = random.randint(1, 8)
			self.internal_preferences[issue.name] = 0.3
		elif temp>0.3:
			self.interested_issues.add(issue)
	
	def sway_opinion(self, issue, target, strength=0.5, success_mod=1): #moves voter's position on issue towards target
		resistance = random.random() * success_mod
		if issue in self.important_issues.keys():
			direction = 0
			if self.important_issues[issue.name] > target:
				direction = -1
			elif self.important_issues[issue.name] < target:
				direction = 1
			if resistance < strength:
				self.important_issues[issue.name] = self.important_issues[issue.name] + direction
			if (2*resistance) < strength:
				self.important_issues[issue.name] = self.important_issues[issue.name] + direction
			if strength < resistance:
				self.important_issues[issue.name] = self.important_issues[issue.name] - direction
			if (2*strength) < resistance:
				self.important_issues[issue.name] = self.important_issues[issue.name] - direction
		elif issue in self.interested_issues:
			if (2*resistance) < strength:
				self.important_issues[issue.name] = target
			elif resistance < strength:
				self.important_issues[issue.name] = target + utils.flip()
	
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
	
	def strengthen(self, amount):
		self.strength += amount
	
	def set_opinion(self, candidate, amount):
		self.party_pref[candidate.name] = amount

	def adj_opinion(self, candidate, amount):
		if candidate.name in self.party_pref.keys():
			self.party_pref[candidate.name] += amount
	
	def get_opinion(self, candidate):
		if candidate.name in self.party_pref.keys():
			return self.party_pref[candidate.name]
		else:
			return 0
	
	def __str__(self):
		return f"{self.name} : \n\t {self.important_issues} \n\t{self.interested_issues} \n\tStrength: {self.strength}    Members: {self.members}"

	
class Pol_Issue():
	def __init__(self, name, strength):
		self.name = name
		self.strength = strength
		self.delta_strength = 0
		
	def strengthen(self, amount):
		self.strength += amount
		self.delta_strength = amount

	def __str__(self):
		return f"{self.name} : {self.strength}"
		
	def __hash__(self):
		return self.name.__hash__()
		
	def __eq__(self, other):
		return self.name == other

class Party():
	def __init__(self, name, **kwargs):
		self.name = "The " + name + " Party"
		self.stances = kwargs
		self.talking_points = list()
		
	def get_agreement(self, issue, pos):
		if issue in self.stances.keys():
			temp = self.stances[issue]
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
	
	def add_talking_point(self, issue):
		self.talking_points.append(issue)
	
	def __hash__(self):
		return self.name.__hash__()
		
	def __eq__(self, other):
		return self.name == other
