# !/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import math

from pybpodapi.model.state_machine.state_machine import StateMachine

logger = logging.getLogger(__name__)


class Builder(StateMachine):
	"""
	Extend state machine with builder logic
	"""

	def __init__(self, hardware):
		StateMachine.__init__(self, hardware)

	def update_state_numbers(self):
		"""
		Replace undeclared states (at the time they were referenced) with actual state numbers
		"""
		for i in range(len(self.undeclared)):
			undeclaredStateNumber = i + 10000
			thisStateNumber = self.manifest.index(self.undeclared[i])
			for j in range(self.total_states_added):
				if self.state_timer_matrix[j] == undeclaredStateNumber:
					self.state_timer_matrix[j] = thisStateNumber
				inputTransitions = self.input_matrix[j]
				for k in range(0, len(inputTransitions)):
					thisTransition = inputTransitions[k]
					if thisTransition[1] == undeclaredStateNumber:
						inputTransitions[k] = (thisTransition[0], thisStateNumber)
				self.input_matrix[j] = inputTransitions
				inputTransitions = self.global_timers.matrix[j]
				for k in range(0, len(inputTransitions)):
					thisTransition = inputTransitions[k]
					if thisTransition[1] == undeclaredStateNumber:
						inputTransitions[k] = (thisTransition[0], thisStateNumber)
				self.global_timers.matrix[j] = inputTransitions
				inputTransitions = self.global_counters.matrix[j]
				for k in range(0, len(inputTransitions)):
					thisTransition = inputTransitions[k]
					if thisTransition[1] == undeclaredStateNumber:
						inputTransitions[k] = (thisTransition[0], thisStateNumber)
				self.global_counters.matrix[j] = inputTransitions
				inputTransitions = self.conditions.matrix[j]
				for k in range(0, len(inputTransitions)):
					thisTransition = inputTransitions[k]
					if thisTransition[1] == undeclaredStateNumber:
						inputTransitions[k] = (thisTransition[0], thisStateNumber)
				self.conditions.matrix[j] = inputTransitions

		# Check to make sure all states in manifest exist
		logger.debug("Total states added: %s | Manifested sates: %s", self.total_states_added, len(self.manifest))
		if len(self.manifest) > self.total_states_added:
			raise StateMachineBuilderError(
				'Error: some states were referenced by name, but not subsequently declared.')

	def build_message(self):
		"""

		:return:
		"""
		message = [len(self.state_names), ]
		for i in range(self.total_states_added):  # Send state timer transitions (for all states)
			if math.isnan(self.state_timer_matrix[i]):
				message += (self.total_states_added,)
			else:
				message += (self.state_timer_matrix[i],)
		for i in range(
				self.total_states_added):  # Send event-triggered transitions (where they are different from default)
			currentStateTransitions = self.input_matrix[i]
			nTransitions = len(currentStateTransitions)
			message += (nTransitions,)
			for j in range(nTransitions):
				thisTransition = currentStateTransitions[j]
				message += (thisTransition[0],)
				destinationState = thisTransition[1]
				if math.isnan(destinationState):
					message += (self.total_states_added,)
				else:
					message += (destinationState,)
		for i in range(self.total_states_added):  # Send hardware states (where they are different from default)
			currentHardwareState = self.output_matrix[i]
			nDifferences = len(currentHardwareState)
			message += (nDifferences,)
			for j in range(nDifferences):
				thisHardwareConfig = currentHardwareState[j]
				message += (thisHardwareConfig[0],)
				message += (thisHardwareConfig[1],)
		for i in range(
				self.total_states_added):  # Send global timer triggered transitions (where they are different from default)
			currentStateTransitions = self.global_timers.matrix[i]
			nTransitions = len(currentStateTransitions)
			message += (nTransitions,)
			for j in range(nTransitions):
				thisTransition = currentStateTransitions[j]
				message += (thisTransition[0] - self.channels.events_positions.globalTimer,)
				destinationState = thisTransition[1]
				if math.isnan(destinationState):
					message += (self.total_states_added,)
				else:
					message += (destinationState,)
		for i in range(
				self.total_states_added):  # Send global counter triggered transitions (where they are different from default)
			currentStateTransitions = self.global_counters.matrix[i]
			nTransitions = len(currentStateTransitions)
			message += (nTransitions,)
			for j in range(nTransitions):
				thisTransition = currentStateTransitions[j]
				message += (thisTransition[0] - self.channels.events_positions.globalCounter,)
				destinationState = thisTransition[1]
				if math.isnan(destinationState):
					message += (self.total_states_added,)
				else:
					message += (destinationState,)
		for i in range(
				self.total_states_added):  # Send condition triggered transitions (where they are different from default)
			currentStateTransitions = self.conditions.matrix[i]
			nTransitions = len(currentStateTransitions)
			message += (nTransitions,)
			for j in range(nTransitions):
				thisTransition = currentStateTransitions[j]
				message += (thisTransition[0] - self.channels.events_positions.condition,)
				destinationState = thisTransition[1]
				if math.isnan(destinationState):
					message += (self.total_states_added,)
				else:
					message += (destinationState,)
		for i in range(self.hardware.n_global_counters):
			message += (self.global_counters.attached_events[i],)
		for i in range(self.hardware.n_conditions):
			message += (self.conditions.channels[i],)
		for i in range(self.hardware.n_conditions):
			message += (self.conditions.values[i],)

		self.state_timers = self.state_timers[:self.total_states_added]

		return message

	def build_message_32_bits(self):
		"""

		:return:
		:rtype: list
		"""

		thirty_two_bit_message = [i * self.hardware.cycle_frequency for i in self.state_timers] + \
		                      [i * self.hardware.cycle_frequency for i in self.global_timers.timers] + \
		                      self.global_counters.thresholds
		
		return thirty_two_bit_message

class StateMachineBuilderError(Exception):
	pass
