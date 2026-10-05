
import sys
import random
import json
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPixmap, QAction, QImage
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QMenu,
    QMessageBox
)


# ------------------------------------
# 1. CONFIGURATION
# ------------------------------------

ASSETS = Path(__file__).resolve().parent / "assets"

WINDOW_WIDTH = 200
WINDOW_HEIGHT = 150

ANIMATION_SPEED = 250
WALK_SPEED = 1


# ------------------------------------
# 2. ICONPET
# ------------------------------------

class IconPet(QWidget):

    def __init__(self):
        super().__init__()

        # Create transparent desktop window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.setFixedSize(
            WINDOW_WIDTH,
            WINDOW_HEIGHT
        )

        # The image label displays our cat
        self.sprite_label = QLabel(self)

        self.sprite_label.setGeometry(
            0, 0,
            WINDOW_WIDTH,
            WINDOW_HEIGHT
        )

        self.sprite_label.setAlignment(
            Qt.AlignmentFlag.AlignHCenter
            | Qt.AlignmentFlag.AlignBottom
        )

        # Allow the window to receive mouse clicks
        self.sprite_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True
                )
        # Bubble label above the pet
        self.bubble_label = QLabel(self)
        self.bubble_label.setText("")
        self.bubble_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bubble_label.setStyleSheet("""
            QLabel {
                background-color: white;
                color: black;
                border: 2px solid black;
                border-radius: 10px;
                padding: 4px 8px;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        self.bubble_label.adjustSize()
        self.bubble_label.hide()
        # ------------------------------------
        # 3. LOAD ALL ANIMATIONS
        # ------------------------------------

        
        self.animations = {
            "idle": self.load_animation(
                "idle", "idle_front_", 3, 100
            ),

            "side": self.load_animation(
                "r", "idle_side_right_", 2, 100
            ),

            "walk_right": self.load_animation(
                "wr", "walk_right_", 6, 90
            ),

            "walk_left": self.load_animation(
                "wl", "walk_left_", 6, 90
            ),

            "sleep": self.load_animation(
                "s", "sleep_", 2, 65
            ),

            "play": self.load_animation(
                "play_stretch", "play_stretch_", 4, 95
            ),
        }

        # ------------------------------------
        # 4. INITIAL PET STATE
        # ------------------------------------

        self.state = "idle"
        self.manual_sleep = False
        self.auto_sleep = False 
# TAMAGOTCHI NEEDS

        self.hunger = 20
        self.happiness = 100
        self.energy = 100
        self.frame_index = 0

        self.direction = 1

        self.state_ticks_remaining = 25

        self.sprite_label.setPixmap(
            self.animations["idle"][0]
        )

        # ------------------------------------
        # 5. INITIAL SCREEN POSITION
        # ------------------------------------

        self.screen_bounds = (
            QApplication.primaryScreen().availableGeometry()
        )

        x = (
            self.screen_bounds.right()
            - self.width()
            - 20
        )

        y = (
            self.screen_bounds.bottom()
            - self.height()
            + 1
        )

        self.move(x, y)

        # ------------------------------------
        # 6. START ANIMATION TIMER
        # ------------------------------------

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.update_pet
        )

        self.timer.start(ANIMATION_SPEED)
                # Update the cat's needs every 10 seconds
        self.needs_timer = QTimer(self)

        self.needs_timer.timeout.connect(
            self.update_needs
        )

        self.needs_timer.start(10000)
        self.show()

    # ------------------------------------
    # 7. PREPARE A SINGLE SPRITE
    # ------------------------------------

    def prepare_sleep_sprite(self, image_path):

        sprite = QPixmap(str(image_path))

        if sprite.isNull():
            raise FileNotFoundError(
                f"Cannot load sleep sprite: {image_path}"
            )

        # Resize the entire image without cropping it.
        # Both sleep frames must have identical original dimensions.
        return sprite.scaled(
            190,
            140,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation
        )
    def prepare_sprite(self, image_path, target_height):

        sprite = QPixmap(str(image_path))

        if sprite.isNull():
            raise FileNotFoundError(
                f"Cannot load sprite: {image_path}"
            )

        # Find the visible cat, ignoring transparent margins
        image = sprite.toImage().convertToFormat(
            QImage.Format.Format_ARGB32
        )

        left = image.width()
        top = image.height()
        right = -1
        bottom = -1

        for y in range(image.height()):
            for x in range(image.width()):

                alpha = (image.pixel(x, y) >> 24) & 255

                if alpha > 60:
                    left = min(left, x)
                    right = max(right, x)
                    top = min(top, y)
                    bottom = max(bottom, y)

        if right < left:
            raise ValueError(
                f"Sprite is empty: {image_path}"
            )

        # Crop away transparent space
        sprite = sprite.copy(
            QRect(
                left,
                top,
                right - left + 1,
                bottom - top + 1
            )
        )

        # Resize while preserving aspect ratio
        return sprite.scaled(
            WINDOW_WIDTH - 10,
            target_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation
        )

    # ------------------------------------
    # 8. LOAD AN ANIMATION
    # ------------------------------------

    
    def load_animation(
        self,
        folder,
        prefix,
        frame_count,
        height
    ):

        frames = []

        for number in range(1, frame_count + 1):

            filename = f"{prefix}{number}.png"

            image_path = ASSETS / folder / filename

            
            if folder == "s":
                sprite = self.prepare_sleep_sprite(
                    image_path
                )
            else:
                sprite = self.prepare_sprite(
                    image_path,
                    height
                )
            
            frames.append(sprite)

        return frames
    # we do be updating need here am I right 
    def refresh_bubble(self):

        text = ""

        # Priority order
        
        if self.energy <= 20:
            text = "Sleepy..."
        elif self.hunger >= 80:
            text = "I am HUNGRY BITCH!"
        elif self.happiness <= 30:
            text = "Play with me!"
        if text:
            self.bubble_label.setText(text)
            self.bubble_label.adjustSize()

            x = (WINDOW_WIDTH - self.bubble_label.width()) // 2
            y = 5

            self.bubble_label.move(x, y)
            self.bubble_label.show()
        else:
            self.bubble_label.hide()
    def update_needs(self):

        # Hunger increases over time
        self.hunger = min(
            100,
            self.hunger + 1
        )

        # Sleeping restores energy
        if self.state == "sleep":

            self.energy = min(
                100,
                self.energy + 5
            )

        # Other activities consume energy
        else:

            self.energy = max(
                0,
                self.energy - 1
            )

        # Happiness decreases when very hungry
        if self.hunger >= 80:

            self.happiness = max(
                0,
                self.happiness - 1
            )
                
        # Happiness also decreases over time
        # when the cat is awake

        if self.state != "sleep":

            self.happiness = max(
                0,
                self.happiness - 1
            )
    # AUTOMATIC SLEEP SYSTEM

        # Wake up when enough energy has been restored
        if self.auto_sleep and self.energy >= 80:

            self.auto_sleep = False
            self.wake_up()

        # Fall asleep automatically when exhausted
        elif (
            self.energy <= 20
            and not self.manual_sleep
            and not self.auto_sleep
        ):

            self.auto_sleep = True

            self.state = "sleep"
            self.frame_index = 0

            self.sprite_label.setPixmap(
                self.animations["sleep"][0]
            )
        self.refresh_bubble()
        print("ICONPET is exhausted! Going to sleep.")

                    
        # HUNGER SYSTEM

        if self.hunger >= 80 and self.state != "sleep":

            # Stop walking and display the idle animation
            self.state = "idle"

            self.frame_index = 0

            # Check again after the next animation cycle
            self.state_ticks_remaining = 3

            print("ICONPET is hungry! Feed me BITCH !")
        self.refresh_bubble()
    # ------------------------------------
    # 9. CHOOSE THE NEXT ACTIVITY
    # ------------------------------------

    def choose_next_activity(self):
        # don t choose a random activite during manual sleep 
        if self.manual_sleep or self.auto_sleep : 
            return
        
        # Stay idle when hungry
        if self.hunger >= 80:

            self.state = "idle"

            self.frame_index = 0

            self.state_ticks_remaining = 3

            return
        activity = random.choices(
            ["idle", "side", "walk", "sleep", "play"],
            weights=[4, 2, 4, 3, 1]
        )[0]

        if activity == "walk":

            if self.direction == 1:
                self.state = "walk_right"
            else:
                self.state = "walk_left"

        else:
            self.state = activity

        self.frame_index = 0

        # Play once; other activities last longer
        if self.state == "play":
            self.state_ticks_remaining = 4

        elif self.state == "sleep":
            self.state_ticks_remaining = 40

        else:
            self.state_ticks_remaining = random.randint(
                15, 35
            )

    # ------------------------------------
    # 10. UPDATE THE PET
    # ------------------------------------

    def update_pet(self):
        self.frame_index += 1
        # Only change activities automatically when
        # the cat isn't manually sleeping
        if not self.manual_sleep or not self.auto_sleep:

            self.state_ticks_remaining -= 1

            if self.state_ticks_remaining <= 0:
                self.choose_next_activity()
        # Move the cat when walking
        if self.state in ("walk_left", "walk_right"):

            new_x = self.x() + self.direction * WALK_SPEED

            left_limit = self.screen_bounds.left()

            right_limit = (
                self.screen_bounds.right()
                - self.width()
                + 1
            )

            # Turn around at screen boundaries
            if new_x <= left_limit:
                new_x = left_limit
                self.direction = 1
                self.state = "walk_right"
                self.frame_index = 0

            elif new_x >= right_limit:
                new_x = right_limit
                self.direction = -1
                self.state = "walk_left"
                self.frame_index = 0

            self.move(new_x, self.y())

        # Get the animation for the current activity
        frames = self.animations[self.state]

        # Loop through its frames
        self.frame_index %= len(frames)

        # Display the current animation frame
        self.sprite_label.setPixmap(
            frames[self.frame_index]
        )

        # Adjust the cat's vertical position
        if self.state == "sleep":
            self.sprite_label.move(0, 35)
        else:
            self.sprite_label.move(0, 0)
        self.refresh_bubble()

    def feed_pet(self):

        # Feeding reduces hunger
        self.hunger = max(0, self.hunger - 20)

        print("You fed ICONPET!")
        print(f"Hunger: {self.hunger}/100")
                
        # Return to normal behavior after feeding
        if self.hunger < 80:

            self.state = "idle"

            self.frame_index = 0

            self.state_ticks_remaining = 10

            print("ICONPET is full and happy!")
        self.refresh_bubble()
    # ------------------------------------
    # 11. MOUSE INTERACTIONS
    # ------------------------------------

        
    def play_with_pet(self):

        # Wake the cat if sleeping manually
        self.manual_sleep = False

        # Playing increases happiness
        self.happiness = min(
            100,
            self.happiness + 15
        )

        # Playing consumes energy
        self.energy = max(
            0,
            self.energy - 10
        )

        # Start the playing animation
        self.state = "play"

        self.frame_index = 0

        self.state_ticks_remaining = 4

        self.sprite_label.setPixmap(
            self.animations["play"][0]
        )

        print("Playing with ICONPET!")
        self.refresh_bubble()
    def put_to_sleep(self):

        # Enable manual sleeping
        self.auto_sleep= False 
        self.manual_sleep = True

        # Switch to sleeping animation
        self.state = "sleep"

        self.frame_index = 0

        self.state_ticks_remaining = 40

        # Immediately display the first sleep frame
        self.sprite_label.setPixmap(
            self.animations["sleep"][0]
        )

        print("ICONPET is sleeping.")
        


    def wake_up(self):

        # Disable manual sleeping
        self.auto_sleep = False 
        self.manual_sleep = False

        # Return to idle animation
        self.state = "idle"

        self.frame_index = 0

        self.state_ticks_remaining = 25

        # Display the first idle frame
        self.sprite_label.setPixmap(
            self.animations["idle"][0]
        )

        print("ICONPET woke up!")
        self.refresh_bubble()

    
    def show_status(self):

        QMessageBox.information(
            self,
            "ICONPET Status",
            f"Hunger: {self.hunger}/100\n"
            f"Happiness: {self.happiness}/100\n"
            f"Energy: {self.energy}/100\n\n"
            f"Current activity: {self.state}"
        )    
    def mousePressEvent(self, event):

            # LEFT CLICK: Play with the cat
        if event.button() == Qt.MouseButton.LeftButton:
            self.play_with_pet()

        # RIGHT CLICK: Open interaction menu
        elif event.button() == Qt.MouseButton.RightButton:

            menu = QMenu(self)

            # Feed the cat
            feed_action = QAction("Feed", self)

            feed_action.triggered.connect(
                self.feed_pet
            )

            menu.addAction(feed_action)

            menu.addSeparator()
            # Sleep
            sleep_action = QAction("Sleep", self)
            sleep_action.triggered.connect(
                self.put_to_sleep
            )
            menu.addAction(sleep_action)

            # Wake Up
            wake_action = QAction("Wake Up", self)
            wake_action.triggered.connect(
                self.wake_up
            )
            menu.addAction(wake_action)

            # Play
            play_action = QAction("Play", self)
            play_action.triggered.connect(
                self.play_with_pet
            )
            menu.addAction(play_action)
            # Status
            status_action = QAction("Status", self)

            status_action.triggered.connect(
                self.show_status
            )

            menu.addAction(status_action)
            menu.addSeparator()

            # Quit
            quit_action = QAction(
                "Quit ICONPET",
                self
            )

            quit_action.triggered.connect(
                QApplication.quit
            )

            menu.addAction(quit_action)

            menu.exec(
                event.globalPosition().toPoint()
            )
# ------------------------------------
# 12. START APPLICATION
# ------------------------------------

if __name__ == "__main__":

    app = QApplication(sys.argv)

    pet = IconPet()

    sys.exit(app.exec())