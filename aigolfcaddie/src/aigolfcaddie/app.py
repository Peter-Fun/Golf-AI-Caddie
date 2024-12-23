"""
author: Peter Xiao
email: peterxiaofun@gmail.com
date: 2024-12-15
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from openai import OpenAI
from PIL import Image
import json
import base64
import io
import cv2
from typing import List, Dict

from aigolfcaddie.utils import *

"""
The source code of the BeeWare App that creates frontend interaction with the user and calls 
backend functions to SAM and ChatGPT 4-o.
"""

class AIGolfCaddie(toga.App):
    """
    The structure of the BeeWare App that contains the frontend commands and user interactions. 
    """
    def startup(self):
        """
        The startup screen of the app where the user can go set course data or contact the chatbot.
        """
        # Shared dictionary of course data with coordinates
        self.course_data = {
            "bunker": [],
            "fairway": [],
            "green": [],
            "tee": [],
            "scale": None
        }

        self.main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # Buttons to switch between CourseDataBuilder and ChatBotApp
        course_data_button = toga.Button(
            "Open Course Data Builder", on_press=self.show_course_data_builder, 
            style=Pack(padding=10)
        )
        chat_bot_button = toga.Button(
            "Open Chat Bot", on_press=self.show_chat_bot, style=Pack(padding=10)
        )

        self.main_box.add(course_data_button)
        self.main_box.add(chat_bot_button)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()

    def show_course_data_builder(self, widget):
        """
        Initialize and display CourseDataBuilder layout
        """
        self.course_data_builder_box = self.build_course_data_builder()
        self.main_window.content = self.course_data_builder_box

    def show_chat_bot(self, widget):
        """
        Initialize and display ChatBotApp layout
        """
        self.chat_bot_box = self.build_chat_bot()
        self.main_window.content = self.chat_bot_box

    def build_course_data_builder(self):
        """
        Main layout for CourseDataBuilder
        """
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # Selecting obstacle type
        self.obstacle_type_dropdown = toga.Selection(
            items=["bunker", "fairway", "green", "tee"],
            style=Pack(padding=5)
        )

        # Input coordinates and tee color
        self.u_input = toga.TextInput(placeholder="Enter u coordinate of feature", 
                                      style=Pack(flex=1, padding=5))
        self.v_input = toga.TextInput(placeholder="Enter v coordinate of feature", 
                                      style=Pack(flex=1, padding=5))
        self.color_input = toga.TextInput(placeholder="Enter color (only for tee)", 
                                          style=Pack(flex=1, padding=5))

        # Input scale (pixel/yd)
        self.scale_input = toga.TextInput(placeholder="Enter scale", style=Pack(flex=1, padding=5))

        add_button = toga.Button("Add Feature", on_press=self.add_entry, style=Pack(padding=5))
        set_scale_button = toga.Button("Set Scale", on_press=self.set_scale, style=Pack(padding=5))
        clear_data_button = toga.Button("Clear Data", on_press=self.clear_data, 
                                        style=Pack(padding=5))

        back_button = toga.Button("Back to Main Menu", on_press=self.show_main_menu, 
                                  style=Pack(padding=5))

        self.json_display = toga.MultilineTextInput(readonly=True, style=Pack(flex=1, padding=5))

        input_row = toga.Box(style=Pack(direction=ROW, padding=5))
        input_row.add(self.u_input)
        input_row.add(self.v_input)
        input_row.add(self.color_input)
        input_row.add(self.obstacle_type_dropdown)
        input_row.add(add_button)
        input_row.add(set_scale_button)

        main_box.add(input_row)
        main_box.add(self.scale_input)
        main_box.add(self.json_display)
        main_box.add(clear_data_button)
        main_box.add(back_button)

        self.update_json_display()

        return main_box

    def build_chat_bot(self):
        """
        Main layout for ChatBotApp
        """
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        self.chat_area = toga.MultilineTextInput(readonly=True, style=Pack(flex=1, padding=5))

        self.input_box = toga.TextInput(placeholder="Type your message here...", 
                                        style=Pack(flex=1, padding=5))

        upload_button = toga.Button("Upload Image", on_press=self.upload_image, 
                                    style=Pack(padding=5))

        send_button = toga.Button("Send", on_press=self.send_message, style=Pack(padding=5))

        display_data_button = toga.Button("Show Course Data", on_press=self.show_course_data, 
                                          style=Pack(padding=5))

        back_button = toga.Button("Back to Main Menu", on_press=self.show_main_menu, 
                                  style=Pack(padding=5))

        self.image_view = toga.ImageView(style=Pack(flex=1))

        input_row = toga.Box(style=Pack(direction=ROW, padding=5))
        input_row.add(self.input_box)
        input_row.add(send_button)
        input_row.add(upload_button)

        main_box.add(self.chat_area)
        main_box.add(self.image_view)
        main_box.add(input_row)
        main_box.add(display_data_button)
        main_box.add(back_button)

        self.selected_image_path = None
        return main_box

    def show_main_menu(self, widget):
        """
        Set main window content back to main menu
        """
        self.main_window.content = self.main_box

    def add_entry(self, widget):
        """
        Functionality to add an entry to the course data
        """
        obstacle_type = self.obstacle_type_dropdown.value
        u_value = self.u_input.value
        v_value = self.v_input.value
        color = self.color_input.value

        if not u_value or not v_value:
            self.json_display.value = "Error: u and v values are required."
            return

        try:
            u_value = int(u_value)
            v_value = int(v_value)
        except ValueError:
            self.json_display.value = "Error: u and v must be numbers."
            return

        entry = {"u": u_value, "v": v_value}
        if obstacle_type == "tee" and color:
            entry["color"] = color

        self.course_data[obstacle_type].append(entry)
        self.update_json_display()

    def set_scale(self, widget):
        """
        Set the scale the image uses in pixels/yard.
        """
        scale_value = self.scale_input.value
        if not scale_value:
            self.json_display.value = "Error: Scale is required."
            return

        try:
            self.course_data["scale"] = float(scale_value)
        except ValueError:
            self.json_display.value = "Error: Scale must be a number."
            return
        self.update_json_display()

    def update_json_display(self):
        """
        Display updated course data
        """
        self.json_display.value = json.dumps(self.course_data, indent=4)

    def clear_data(self, widget):
        """
        Reset course data to initial empty state
        """
        self.course_data = {
            "bunker": [],
            "fairway": [],
            "green": [],
            "tee": [],
            "scale": None
        }
        self.update_json_display()

    def send_message(self, widget):
        """
        Send the user's input into SAM and pipe the output into ChatGPT send to user
        """
        # Get the user's input
        user_message = self.input_box.value

        if user_message:
            self.chat_area.value += f"You: {user_message}\n"

            user_input = ""

            # Part 1: Setup Information
            user_input += "The following are the 3 input parts described previously:\n"
            user_input += "## Setup Information\n"
            user_input += json.dumps(setup_info(),indent = 4) + '\n'

            # Part 2: Physical Features
            # Analyze inputted image using SAM
            image = Image.open(self.selected_image_path)
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')
            image_bytes = base64.b64encode(image_bytes.getvalue()).decode()
            sam_response = call_sam(image_bytes,[])

            metrics = analyze_result(sam_response, self.course_data) # Physical Features
            # Temporarily remove coordinates for formatted input into ChatGPT
            coord_metrics = []
            for metric in metrics:
                coord_metrics.append(metric["coordinates"])
                del metric["coordinates"]

            user_input += "## Physical Features\n"
            user_input += json.dumps(metrics,indent = 4)+ "\n"

            # Add back coordinates to update image to visualize SAM output
            for metric in range(len(metrics)):
                metrics[metric]["coordinates"] = coord_metrics[metric]
            metrics = feature_organization(metrics)
            self.visualize_detections(metrics)

            # Remove coordinates again for formatted input into ChatGPT
            for feature in metrics.keys():
                for metric in metrics[feature]:
                    del metric["coordinates"]

            # Part 3: Inter-Feature Distance
            metrics = feature_analysis(metrics) # Inter-Feature Distance
            user_input += "## Inter-Feature Distance\n"
            user_input += json.dumps(metrics,indent = 4)+ "\n"
            gpt_response = get_gpt_response(user_input, self.selected_image_path)
            self.chat_area.value += f"GPT-4: {json.dumps(json.loads(gpt_response), indent = 4)}\n"
            self.input_box.value = ""

    async def upload_image(self, widget):
        """
        Allow the user to upload an image to display on the screen and be used as input to ChatGPT
        """
        try:
            file = await self.dialog(toga.OpenFileDialog("Select Image", 
                                                         file_types=["png", "jpg", "jpeg"]))
            if file:
                self.chat_area.value += f"Uploaded file: {file}\n"
                self.selected_image_path = file
                self.draw_image()
            else:
                self.chat_area.value += f"No file selected\n"
        except ValueError:
            self.chat_area.value = f"File selection canceled\n"
   
    def draw_image(self, processed_image_bytes = None):
        """
        Take the user image and upload it onto the ImageView to display on screen
        """
        if processed_image_bytes:
            # SAM model update
            image = Image.open(io.BytesIO(processed_image_bytes))
            self.image_view.image = image
            self.chat_area.value += "Image updated with SAM bounding boxes.\n"
        elif self.selected_image_path:
            # User image upload
            image = Image.open(self.selected_image_path)
            image_data = io.BytesIO()
            image.save(image_data, format='PNG')
            self.image_view.image = image
            self.chat_area.value += "Image set as background.\n"
    
    def visualize_detections(self, metrics: Dict) -> None:
        """
        Visualize the detected bounding boxes and centers of mass within the golf map image. 
        This method will draw on top of the original image using opencv functions to indicate 
        SAM outputs and analysis.

        Args:
            metrics: the metrics outputed by feature_analysis function.
            in_img_file: the input image to load and draw over.
            out_img_file: where to save the annotated image.
        """
        im = cv2.imread(self.selected_image_path)
        for feature_type in metrics.keys():  # "bunker", "fairway", "green", "tee"
            for feature_info in metrics[feature_type]:
                u0, v0, u1, v1 = [
                    i / self.course_data["scale"] 
                    for i in feature_info["coordinates"]
                ]
                uc, vc = feature_info["feature_center_yards"]
                cv2.rectangle(im, (int(u0), int(v0)), (int(u1), int(v1)), (255,0,0), 2)
                cv2.putText(im, feature_type, (int(u0), int(v0) - 10), 
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(255,0,0))
                cv2.circle(im, (int(uc), int(vc)), radius=4, color=(255,0,0), thickness=-1)
        _, buffer = cv2.imencode('.png', im)
        self.draw_image(buffer.tobytes())

    def show_course_data(self, widget):
        """
        Show course data in ChatBotApp
        """
        course_data_json = json.dumps(self.course_data, indent=4)
        self.chat_area.value += f"Course Data:\n{course_data_json}\n"


def main():
    return AIGolfCaddie()