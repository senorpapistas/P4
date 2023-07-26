import pyhop
import json

def check_enough (state, ID, item, num):
	if getattr(state,item)[ID] >= num: return []
	return False

def produce_enough (state, ID, item, num):
	return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods ('have_enough', check_enough, produce_enough)

def produce (state, ID, item):
	return [('produce_{}'.format(item), ID)]

pyhop.declare_methods ('produce', produce)

def make_method (name, rule):
	def method (state, ID):
		# your code here
		next_tasks = []
		for item, value in rule.get('Requires', {}).items():
			next_tasks.append(('have_enough', ID, item, value))
		for item, value in rule.get('Consumes', {}).items():
			next_tasks.append(('have_enough', ID, item, value))
		next_tasks.append((f"op_{name}", ID))
		return next_tasks
	
	method.__name__ = name
	return method

def declare_methods (data):
	# some recipes are faster than others for the same product even though they might require extra tools
	# sort the recipes so that faster recipes go first

	# your code here
	# hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)	

	for recipe, details in data['Recipes'].items():
		method_name = f"produce_{list(details['Produces'].keys())[0]}"
		if method_name in  pyhop.methods:
			pyhop.methods[method_name].append(make_method(recipe, details))
		else:
			pyhop.declare_methods(method_name, make_method(recipe, details))

def make_operator (rule):
	def operator (state, ID):
		# your code here
		# print('before', vars(state))

		for item, value in rule.get('Requires', {}).items():
			if list(getattr(state, item).values())[0] < value:
				return False
			
		for item, value in rule.get('Consumes', {}).items():
			if list(getattr(state, item).values())[0] < value:
				return False
			setattr(state, item, list(getattr(state, item).values())[0] - value)

		for item, value in rule.get('Produces', {}).items():
			setattr(state, item, list(getattr(state, item).values())[0] + value)

		state.time[ID] -= rule.get('Time', 1)

		# print('after', vars(state))
		return state
	
	operator.__name__ = f"op_{list(rule.keys())[0]}"
	return operator

def declare_operators (data):
	# your code here
	# hint: call make_operator, then declare the operator to pyhop using pyhop.declare_operators(o1, o2, ..., ok)

	for recipe, details in data['Recipes'].items():
		pyhop.declare_operators(make_operator({recipe: details}))

def add_heuristic (data, ID):
	# prune search branch if heuristic() returns True
	# do not change parameters to heuristic(), but can add more heuristic functions with the same parameters: 
	# e.g. def heuristic2(...); pyhop.add_check(heuristic2)
	def heuristic (state, curr_task, tasks, plan, depth, calling_stack):
		# your code here
		return False # if True, prune this branch

	pyhop.add_check(heuristic)


def set_up_state (data, ID, time=0):
	state = pyhop.State('state')
	state.time = {ID: time}

	for item in data['Items']:
		setattr(state, item, {ID: 0})

	for item in data['Tools']:
		setattr(state, item, {ID: 0})

	for item, num in data['Initial'].items():
		setattr(state, item, {ID: num})

	return state

def set_up_goals (data, ID):
	goals = []
	for item, num in data['Goal'].items():
		goals.append(('have_enough', ID, item, num))

	return goals

if __name__ == '__main__':
	rules_filename = 'crafting.json'

	with open(rules_filename) as f:
		data = json.load(f)

	state = set_up_state(data, 'agent', time=239) # allot time here
	goals = set_up_goals(data, 'agent')

	declare_operators(data)
	declare_methods(data)
	add_heuristic(data, 'agent')

	pyhop.print_operators()
	pyhop.print_methods()

	# Hint: verbose output can take a long time even if the solution is correct; 
	# try verbose=1 if it is taking too long
	pyhop.pyhop(state, goals, verbose=3)
	# pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)
