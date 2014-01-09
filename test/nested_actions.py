

class ActionA(Action):
	
	def redo(self):
		pass

	def undo(self):
		pass
		
class ActionB(Action):
	
	def redo(self):
		pass

	def undo(self):
		pass


class ActionC1(Action):
	
	def redo(self):
		pass

	def undo(self):
		pass
		
class ActionC2(Action):
	
	def redo(self):
		pass

	def undo(self):
		pass

class ActionC(Action):
	
	def redo(self):
		ActionC1().call()
		ActionC2().call()
		0/0

	def undo(self):
		pass

'''

DO		ActionA
DO		ActionB
DO		ActionC
DO		ActionC1
DO		ActionC2
UNDO    ActionC 		# This could be bad!
UNDO    ActionC2
UNDO    ActionC1
UNDO    ActionB
UNDO    ActionA

'''