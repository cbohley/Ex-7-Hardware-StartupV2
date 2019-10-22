import os

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton

from pidev.stepper import stepper
import spidev
from time import sleep
import RPi.GPIO as GPIO

spi = spidev.SpiDev()
import time
import threading

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
ADMIN_SCREEN_NAME = 'admin'


class ProjectNameGUI(App):
    """
    Class to handle running the GUI Application
    """

    def build(self):
        """
        Build the application
        :return: Kivy Screen Manager instance
        """
        return SCREEN_MANAGER


Window.clearcolor = (1, 1, 1, 1)  # White


class MainScreen(Screen):
    """
    Class to handle the main screen and its associated touch events
    """
    s0 = stepper(port=0, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
                 steps_per_unit=200, speed=8)
    go = False
    direction_pin = 1

    def pressed(self):

        self.go = not self.go

        if self.go:
            self.s0.run(self.direction_pin, int(self.ids.slider.value))
            self.ids.motor.text = "Motor On"
        else:
            self.s0.softStop()
            self.ids.motor.text = "Motor Off"

    def direction(self):
        if self.go:
            if self.direction_pin == 1:
                self.direction_pin = 0
                self.ids.direction.text = "Clockwise"
                self.s0.run(self.direction_pin, int(self.ids.slider.value))
            else:
                self.direction_pin = 1
                self.ids.direction.text = "Counter-Clockwise"
                self.s0.run(self.direction_pin, int(self.ids.slider.value))

    def motor_thread(self):
        y = threading.Thread(target=self.motor, daemon=True)
        y.start()

    def motor(self):
        self.s0.set_as_home()
        print(self.s0.get_position_in_units())
        self.ids.updates.text = str(self.s0.get_position_in_units())
        self.s0.set_speed(1)
        self.s0.go_to_position(15)
        print(self.s0.get_position_in_units())
        self.ids.updates.text = str(self.s0.get_position_in_units())
        time.sleep(10)

        self.s0.set_speed(5)
        self.s0.relative_move(10)
        self.ids.updates.text = str(self.s0.get_position_in_units())
        time.sleep(8)

        self.s0.relative_move(-25)
        self.ids.updates.text = str(self.s0.get_position_in_units())
        time.sleep(30)

        self.s0.set_speed(8)
        self.s0.relative_move(-100)
        self.ids.updates.text = str(self.s0.get_position_in_units())
        time.sleep(10)

        self.s0.relative_move(100)
        self.ids.updates.text = "Finished: " + str(self.s0.get_position_in_units())

    def admin_action(self):
        """
        Hidden admin button touch event. Transitions to passCodeScreen.
        This method is called from pidev/kivy/PassCodeScreen.kv
        :return: None
        """
        SCREEN_MANAGER.current = 'passCode'


class AdminScreen(Screen):
    """
    Class to handle the AdminScreen and its functionality
    """

    def __init__(self, **kwargs):
        """
        Load the AdminScreen.kv file. Set the necessary names of the screens for the PassCodeScreen to transition to.
        Lastly super Screen's __init__
        :param kwargs: Normal kivy.uix.screenmanager.Screen attributes
        """
        Builder.load_file('AdminScreen.kv')

        PassCodeScreen.set_admin_events_screen(
            ADMIN_SCREEN_NAME)  # Specify screen name to transition to after correct password
        PassCodeScreen.set_transition_back_screen(
            MAIN_SCREEN_NAME)  # set screen name to transition to if "Back to Game is pressed"

        super(AdminScreen, self).__init__(**kwargs)

    @staticmethod
    def transition_back():
        """
        Transition back to the main screen
        :return:
        """
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    @staticmethod
    def shutdown():
        """
        Shutdown the system. This should free all steppers and do any cleanup necessary
        :return: None
        """
        os.system("sudo shutdown now")

    @staticmethod
    def exit_program():
        """
        Quit the program. This should free all steppers and do any cleanup necessary
        :return: None
        """
        quit()


"""
Widget additions
"""

Builder.load_file('main.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(PassCodeScreen(name='passCode'))
SCREEN_MANAGER.add_widget(PauseScreen(name='pauseScene'))
SCREEN_MANAGER.add_widget(AdminScreen(name=ADMIN_SCREEN_NAME))

"""
MixPanel
"""


def send_event(event_name):
    """
    Send an event to MixPanel without properties
    :param event_name: Name of the event
    :return: None
    """
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()


if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    ProjectNameGUI().run()
