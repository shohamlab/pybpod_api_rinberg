# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Light Chasing example

Follow light on 3 pokes

Connect noseports to ports 1-3.

"""

import examples.settings as settings

from pybpodapi.model.bpod import Bpod
from pybpodapi.model.state_machine import StateMachine


def run():
	"""
	Run this protocol now
	"""

	my_bpod = Bpod().start(settings.SERIAL_PORT)

	sma = StateMachine(my_bpod.hardware)

	sma.add_state(
		state_name='Port1Active1',  # Add a state
		state_timer=0,
		state_change_conditions={'Port1In': 'Port2Active1'},
		output_actions=[('PWM1', 255)])

	sma.add_state(
		state_name='Port2Active1',
		state_timer=0,
		state_change_conditions={'Port2In': 'Port3Active1'},
		output_actions=[('PWM2', 255)])

	sma.add_state(
		state_name='Port3Active1',
		state_timer=0,
		state_change_conditions={'Port3In': 'Port1Active2'},
		output_actions=[('PWM3', 255)])

	sma.add_state(
		state_name='Port1Active2',
		state_timer=0,
		state_change_conditions={'Port1In': 'Port2Active2'},
		output_actions=[('PWM1', 255)])

	sma.add_state(
		state_name='Port2Active2',
		state_timer=0,
		state_change_conditions={'Port2In': 'Port3Active2'},
		output_actions=[('PWM2', 255)])

	sma.add_state(
		state_name='Port3Active2',
		state_timer=0,
		state_change_conditions={'Port3In': 'exit'},
		output_actions=[('PWM3', 255)])

	my_bpod.send_state_machine(sma)

	raw_events = my_bpod.run_state_machine(sma)

	print(raw_events)

	my_bpod.disconnect()


if __name__ == '__main__':
	settings.run_this_protocol(run)
