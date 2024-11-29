# the json schema used by GPT to format its output regarding golf advice, more information at https://openai.com/index/introducing-structured-outputs-in-the-api/ 
formatted = {
  "type": "json_schema",
  "json_schema": {
    "name": "golf_strategy_response",
    "schema":{
      "type": "object",
      "properties": {
      "strategy": {
        "type": "array",
        "items": {
          "type": "object",
          "required": [
            "club",
            "distance hit",
            "estimated location",
            "distance_from_hole"
          ],
          "properties": {
            "club": {
              "type": "string",
              "description": "The club used for the shot."
            },
            "distance hit": {
              "type": "number",
              "description": "The distance the ball was hit with the club."
            },
            "distance_from_hole": {
              "type": "number",
              "description": "Distance from the hole where the shot is estimated to land."
            },
            "estimated location": {
              "type": "string",
              "description": "The estimated location along the hole where the ball should land."
            }
          },
          "additionalProperties": False
        },
        "description": "List of strategies with clubs and distance hit."
      },
      "expected_outcome": {
        "type": "object",
        "required": [
          "explanation_of_strategy",
          "stroke_count",
          "fairway_shape",
          "location_of_all_obstacles"
        ],
        "properties": {
          "stroke_count": {
            "type": "number",
            "description": "Expected number of strokes to complete the hole."
          },
          "fairway_shape": {
            "type": "string",
            "description": "Description of the shape of the fairway. Include size as well as any curves or splits in the fairway that occur."
          },
          "explanation_of_strategy": {
            "type": "string",
            "description": "A detailed explanation of the chosen strategy."
          },
          "location_of_all_obstacles": {
            "type": "array",
            "items": {
              "type": "object",
              "required": [
                "obstacle_type",
                "distance_from_tee",
                "left_right_or_center_from_fairway"
              ],
              "properties": {
                "obstacle_type": {
                  "type": "string",
                  "description": "Type of the obstacle."
                },
                "distance_from_tee": {
                  "type": "number",
                  "description": "Distance of the obstacle from the tee."
                },
                "left_right_or_center_from_fairway": {
                  "enum": [
                    "left",
                    "right",
                    "center"
                  ],
                  "type": "string",
                  "description": "Position of the obstacle relative to the fairway."
                }
              },
              "additionalProperties": False
            },
            "description": "List of obstacles and their locations."
          }
        },
        "description": "The expected outcome of the strategy.",
        "additionalProperties": False
      }
    },
    "required": [
      "expected_outcome",
      "strategy"
    ],
    "additionalProperties": False
    }
  }
}
system_instructions = """
You are an AI caddy. Your job is to come up with the best plan of club selections to get the lowest score for this hole. Provide detailed descriptions of where shots land as well as explanations for your decisions all the way until the ball goes in the hole. In addition, you have to accurately describe both the fairway and any obstacles in the way of the hole, including their type and location compared to the fairway. Accuracy means correctly describing the location of obstacles in relation to each other (left, right, …) and correctly stating the numeric value of distances.
Input will have 2 parts: an image of a golf hole map that shows obstacles and text input containing multiple types of data.
## Description of text input
The user will give you several types of text data as part of the input. First is the setup information containing the available clubs, club performance, user skill level, and tee choice in JSON format. Second is a list of physical features of the golf hole as well as their coordinates presented in JSON format. Third is a list of distances between each set of features in JSON format.
## Setup Information
The 1st section of the input is setup information. This is JSON formatted as follows:
{
    "clubs": ["driver","7-iron", …],
    "club_performance": {"driver": <integer value in yards>,"7-iron": <integer value in yards>,…},
    "level_error": <float value in degrees>,
    "tee_color": <string value that is a color>
}
This is an explanation of the key values from the above JSON:
“available_clubs”: this key points to a list of available clubs that the user has access to
“club_performance”: this key points to a dictionary where the keys are the clubs the user has and the value is the maximum distance in yards they can hit with that club. Note the skill level of the user will affect how likely they can reach the maximum distance as well and how much control they have over how much lower than the maximum they can hit
“level_error”: this key points to a float that represents the error in terms of degrees off-target the user could hit based on their skill level
“tee_color”: this key points to a string that represents the tee the user is teeing off of


## Physical Features
The 2nd section of the input is about physical features. This is a list of features found within the golf course and their relative locations. The list is formatted as follows:
[
	{“feature_name”: “fairway”, “feature_center_yards”:  [x_value, y_value]},
	{"feature_name": "bunker", "feature_center_yards": [x_value, y_value]},
	{"feature_name": "tee", "feature_center_yards": [x_value, y_value], "tee_color": "red"},
	…
]

Where “feature_name” represents the type of feature on the golf course. The feature_name could be one of “fairway”, “bunker”, “tee”, or “green”. The feature_center_yards key will give you a 2D coordinate of the center of the feature. These are represented in a x, y coordinates where the measurement unit is in yards.
“tee” has an additional metric associated with it. “tee_color” represents what color the player is teeing off of, including colors like red, blue, or black. 

## Inter-Feature Distances
The 3rd section of the input is about inter-features distances. This is a list of distances between golf features that represents the distance in yards between various combinations of the features mentioned in the above Physical Features section. Features include “fairway”, “bunker”, “tee”, and “green".
The list is formatted as follows:
[
{
"distance": <float value in yards>, 
"feature_1": {"feature_name": "fairway",
"feature_center_yards": [<float value in yards>,<float value in yards>]},
"feature_2": {"feature_name": "bunker",
"feature_center_yards": [<float value in yards>,<float value in yards>]}
},
    	{
        	"distance": <float value in yards>,
        	"feature_1": {"feature_name": "fairway",
            	"feature_center_yards": [<float value in yards>,<float value in yards>]},
        	"feature_2": {"feature_name": "bunker",
            "feature_center_yards": [<float value in yards>,<float value in yards>]}
    	},
…
]
The “distance” key represents the amount of distance in yards between two features. The “feature_1” and “feature_2” keys are the two features that the “distance” key measures. The values for the “feature_1” and “feature_2” keys contains the name of the feature in the “feature_name” key. Where “feature_name” represents the type of feature on the golf course. The feature_name could be one of “fairway”, “bunker”, “tee”, or “green”. The feature_center_yards key will give you a 2D coordinate of the center of the feature. These are represented in a x, y coordinates where the measurement unit is in yards. “feature_1” and “feature_2” correspond to physical features listed in the previous Physical Features section.

# Instructions for Generating Plan
Please use all 3 text input parts as much as possible when generating the plan. Make sure to use the distances given within the inputs. Please give responses that are logically consistent with the distances and center coordinates given within the inputs for quantitative analysis. Use the given image for qualitative analysis Please respond using JSON format. Don’t respond with anything outside of the JSON. 

# Strategy for Generating Plan
The general strategy to employ for generating the plan involves looking at the distance between the tee and middle of the fairway for the first shot. For the second shot, usually you want to look at the distance between the middle of the fairway to the middle of the green. Be mindful however of the distances from the obstacles to where shots are being taken as well as the skill level of the player, by taking into account the level error. You should avoid generating shot plans where the distance from the obstacle to the shot is within range of the level error. Split up distances into multiple shots if it’s more realistic, or combine multiple shots if reasonable.


Please respond using JSON only. Don't respond with anything outside of the JSON.
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from openai import OpenAI
from PIL import Image
import json
import base64
import io
import uuid
import numpy as np
import cv2
import os
import requests
from typing import List, Dict

api_key = 'REDACTED'
client = OpenAI(api_key=api_key)

SAM_API_ADDR = "https://clever-prompt-tiger.ngrok-free.app/sam/"

TEST_FILE = "clickfiles/icreek1.json"

def get_samapi_version() -> str:
    """
    Return the samapi server package version. Also, can be used to check if server is connected.

    Returns:
        version_str: a string indiciating the SAM API version.
    """
    result = requests.get(SAM_API_ADDR + "version/")
    return result.text



def call_sam(b64str_img: str, bbox) -> str:
    """
    Utility function to call the SAM server at the SAM_API_ADDR. The SAM server will inference the
    SAM model to generate GeoJSON edges to capture segmented regions within the image.

    This function tunes the SAM parameters to work best with golf map segmentation. Specifically,
    this call makes a POST request to /sam/automask/ and waits for a response.

    The SAM parameters are described here:
        https://github.com/ksugar/samapi/tree/main?tab=readme-ov-file#endpoint-samautomask-post
    
    Args:
        b64str_img: an image encoded as an base64 character string.

    Returns:
        sam_segmentation: a geojson string that outlines the edges of the segmentations. The geojson
            contains a list of json objects with following keys: "geometry", "type", and
            "properties". 
    """
    # Note: Following https://github.com/ksugar/samapi/tree/main?tab=readme-ov-file#endpoint-samautomask-post
    result = requests.post(
        SAM_API_ADDR + "automask/",
        json={
            "type": "sam2_l",
            "b64img": b64str_img,
            "output_type": "Multi-mask (all)",
            "pred_iou_thresh": 0.8, # Default 0.88
            "points_per_side": 100, # Default 32
            "points_per_batch": 128, # Default 64
        }
    )
    return result.text


def calculate_center_of_mass(vertices):
    """
    Calculate the center of mass using the shoelace formula. 

    Args:
        verticies: a list of sequential verticies (u,v) describing a n-gon.
    
    Returns:
        com: the (u,v) of the center of mass of the shape.
    """
    n = len(vertices)
    # Ensure there are enough vertices
    if n < 3:
        raise ValueError("A polygon must have at least 3 vertices.")
    
    # Initialize variables for area and centroid calculation
    area = 0.0
    cx = 0.0
    cy = 0.0

    # Calculate area using the shoelace formula
    for i in range(n):
        x0, y0 = vertices[i]
        x1, y1 = vertices[(i + 1) % n]  # Next vertex, wrapping around
        cross_product = x0 * y1 - x1 * y0
        area += cross_product
        cx += (x0 + x1) * cross_product
        cy += (y0 + y1) * cross_product
    
    area *= 0.5
    if area == 0:
        raise ValueError("The area of the polygon is zero, check the vertices.")
    
    # Finalize centroid coordinates
    cx /= (6 * area)
    cy /= (6 * area)

    return (round(cx,4), round(cy,4))

def analyze_result(geojson_str: str, clicks: Dict) -> List[Dict]:
    """
    Analyse geojson string generated by the samapi.

    Args:
        geojson_str: the geojson string. Contains a list of json objects with following keys: 
            "geometry", "type", and "properties". 

    Returns:
        bounding_boxes: a list of bounding boxes. Each bounding box is a dictionary with describing
            the locations of the box corners and center.
    """
    data = json.loads(geojson_str)
    all_metrics = []
    for golf_feature in clicks.keys():
        if golf_feature != "file" and golf_feature != "scale":
            for click in clicks[golf_feature]:
                minarea = -1
                click["u"] *= clicks["scale"]
                click["v"] *= clicks["scale"]
                for feature in data:  # feature contains 'type', 'geometry', and 'properties'
                    verticies = feature['geometry']['coordinates'][0]
                    verticies = np.array(verticies) * clicks["scale"]
                    
                    # Calculate the edges of the bounding box.
                    u0, v0 = np.min(verticies, axis=0)
                    u1, v1 = np.max(verticies, axis=0)
                    if contained(u0, v0, u1, v1, click):
                        if minarea == -1 or abs(u1 - u0) * abs(v1-v0) < minarea:
                            minarea = abs(u1 - u0) * abs(v1-v0)
                            feature_info = {
                                "feature_name" : golf_feature,
                                "feature_center_yards" : calculate_center_of_mass(verticies),
                                "coordinates" : [u0,v0,u1,v1]
                            } # add distance and direction to other features
                            if golf_feature == "tee":
                                feature_info["tee_color"] = click["color"]
                
                all_metrics.append(feature_info)
    return all_metrics

def contained(u0: float, v0: float, u1: float, v1: float, click: Dict) -> bool:
    """
    Determine whether a 2d click coordinate is located within a 2d bounding box.

    Args:
        u0: the u coordinate of the top left corner (u0,v0) of the bbox.
        v0: the v coordinate of the top left corner (u0,v0) of the bbox.
        u1: the u coordinate of the bot right corner (u1,v1) of the bbox.
        v1: the v coordinate of the bot right corner (u1,v1) of the bbox.
        click: the (u,v) coordinates of a specific point or "click"

    Returns:
        within: returns whether the click was within the bounding box described.
    """
    if u0 <= click["u"] and u1 >= click["u"] and v0 <= click["v"] and v1 >= click["v"]:
        return True
    else:
        return False

def setup_info():
    """
    Return information about the user's available clubs and expected performance.
    """
    setup_info = {
        "avilable_clubs" : ["driver", "7-iron", "5-hybrid", "5-iron", "sand wedge", "putter"],
        "club_performance" : {
            "driver" : 270, 
            "7-iron" : 140, 
            "5-hybrid" : 200, 
            "5-iron" : 160, 
            "pitching wedge": 90,
            "sand wedge" : 40,
        },
        "level_error" : 20,
        "tee_color" : "black"
    }
    return setup_info

def feature_organization(metrics: List[Dict]) -> Dict:
    """
    Organize golf features by their feature type based on their name

    Args:
        metrics: the golf features list. Contains a list of dictionaries each describing a golf feature 
            identified. The "feature_name" of each feature is used to group features together by type

    Returns:
        features: a dictionary of golf features. The each key in the dictionary is a feature type, with
            the value being a list containing all of the golf features of that feature type
    """
    features = {}
    for metric in metrics:
        try:
            features[metric["feature_name"]].append(metric)
        except:
            features[metric["feature_name"]] = [metric]
    return features
  
# Function to get a response from GPT-4 using the OpenAI Python module
def get_gpt_response(message, image_path = None):
    """
    Call ChatGPT and get its response to user input

    Args:
        message: the text the user sent. This text is formatted using in accordance to what is laid out 
            in the system instructions for the model, containing three parts for setup information,
            physical features, and inter-feature distances
        image_path: the image of the golf map if provided. This image would be used as supplement for
            the model to use when identifying qualitative information such as the shape of the fairway.

    Returns:
        full_response: a string containing ChatGPT's response to the model. The response strictly follows
            the "formatted" JSON schema and contains the golf strategy information 
    """

    full_response = ""
    try:
        # Make an API call using the OpenAI module
        content = [
        {
            "type": "text",
            "text": message
        }
        ]
        if image_path:
            image = Image.open(image_path)
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')
            image_bytes = "data:image/png;base64," + base64.b64encode(image_bytes.getvalue()).decode()
            #print(image_bytes)
            content.append(
                {
                "type": "image_url",
                "image_url" :{
                    "url": image_bytes
                }
                }
            )
        for response in client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": content}
            ],
            stream=True,
            response_format = formatted
        ):
            full_response += (response.choices[0].delta.content or "")
        # Extract the content of the response
        return full_response
    except Exception as e:
        return f"Error: {str(e)}"

def feature_analysis(metrics: Dict) -> List[Dict]:
    """
    Find the distance between golf features in yards

    Args:
        metrics: the golf features list. Contains a list of dictionaries each describing a golf feature 
            identified. The "feature_name" of each feature is used to group features together by type,
            used for the type vs type comparisons, and the "feature_center_yards" of each feature is
            used to find the distance between the two features.

    Returns:
        distances: a list of dictionaries about golf feature distances. Each dictionary contains the 
            distance between the two features, as well as the two dictionary descriptions of each
            golf feature. Comparisons were made between fairway and bunker, fairway and green,
            tee and fairway, and tee and bunker
    """

    # json.dumps 
    # keep things more structured (keep the scale)
    # go shot by shot instead of a whole plan at once

    # calculate distance from tee to middle of fairway, tee to bunker
    fairway_bunker = []
    fairway_green = []
    tee_fairway = []
    tee_bunker = []
    for fairway in metrics["fairway"]:
        for bunker in metrics["bunker"]:
            distance = round(((fairway['feature_center_yards'][0] - bunker["feature_center_yards"][0]) ** 2 + (fairway['feature_center_yards'][1] - bunker["feature_center_yards"][1]) ** 2) ** 0.5,2)
            fairway_bunker.append({
                "distance" : distance,
                "feature_1" : fairway,
                "feature_2" : bunker
            })
        for green in metrics["green"]:
            distance = round(((fairway['feature_center_yards'][0] - green["feature_center_yards"][0]) ** 2 + (fairway['feature_center_yards'][1] - green["feature_center_yards"][1]) ** 2) ** 0.5,2)
            fairway_green.append({
                "distance" : distance,
                "feature_1" : fairway,
                "feature_2" : green
            })
        for tee in metrics["tee"]:
            distance = round(((fairway['feature_center_yards'][0] - tee["feature_center_yards"][0]) ** 2 + (fairway['feature_center_yards'][1] - tee["feature_center_yards"][1]) ** 2) ** 0.5,2)
            fairway_green.append({
                    "distance" : distance,
                    "feature_1" : tee,
                    "feature_2" : fairway
                })
    for tee in metrics["tee"]:
        for bunker in metrics["bunker"]:
            distance = round(((tee['feature_center_yards'][0] - bunker["feature_center_yards"][0]) ** 2 + (bunker['feature_center_yards'][1] - tee["feature_center_yards"][1]) ** 2) ** 0.5,2)
            tee_bunker.append({
                    "distance" : distance,
                    "feature_1" : tee,
                    "feature_2" : bunker
                })
    
    return fairway_bunker + fairway_green +tee_fairway + tee_bunker

class AIGolfCaddie(toga.App):
    def startup(self):
        """
        The startup screen of the app where the user can go set course data or contact the chatbot
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
            "Open Course Data Builder", on_press=self.show_course_data_builder, style=Pack(padding=10)
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
        self.u_input = toga.TextInput(placeholder="Enter u coordinate of feature", style=Pack(flex=1, padding=5))
        self.v_input = toga.TextInput(placeholder="Enter v coordinate of feature", style=Pack(flex=1, padding=5))
        self.color_input = toga.TextInput(placeholder="Enter color (only for tee)", style=Pack(flex=1, padding=5))

        # Input scale (pixel/yd)
        self.scale_input = toga.TextInput(placeholder="Enter scale", style=Pack(flex=1, padding=5))

        add_button = toga.Button("Add Feature", on_press=self.add_entry, style=Pack(padding=5))
        set_scale_button = toga.Button("Set Scale", on_press=self.set_scale, style=Pack(padding=5))
        clear_data_button = toga.Button("Clear Data", on_press=self.clear_data, style=Pack(padding=5))

        back_button = toga.Button("Back to Main Menu", on_press=self.show_main_menu, style=Pack(padding=5))

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

        self.input_box = toga.TextInput(placeholder="Type your message here...", style=Pack(flex=1, padding=5))

        upload_button = toga.Button("Upload Image", on_press=self.upload_image, style=Pack(padding=5))

        send_button = toga.Button("Send", on_press=self.send_message, style=Pack(padding=5))

        display_data_button = toga.Button("Show Course Data", on_press=self.show_course_data, style=Pack(padding=5))

        back_button = toga.Button("Back to Main Menu", on_press=self.show_main_menu, style=Pack(padding=5))

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
            file = await self.dialog(toga.OpenFileDialog("Select Image", file_types=["png", "jpg", "jpeg"]))
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
        Visualize the detected bounding boxes and centers of mass within the golf map image. This method
        will draw on top of the original image using opencv functions to indicate SAM outputs and 
        analysis.

        Args:
            metrics: the metrics outputed by feature_analysis function.
            in_img_file: the input image to load and draw over.
            out_img_file: where to save the annotated image.
        """
        im = cv2.imread(self.selected_image_path)
        for feature_type in metrics.keys():  # "bunker", "fairway", "green", "tee"
            for feature_info in metrics[feature_type]:
                u0, v0, u1, v1 = [i / self.course_data["scale"] for i in feature_info["coordinates"]]
                uc, vc = feature_info["feature_center_yards"]
                cv2.rectangle(im, (int(u0), int(v0)), (int(u1), int(v1)), (255,0,0), 2)
                cv2.putText(im, feature_type, (int(u0), int(v0) - 10), fontFace = cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(255,0,0))
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