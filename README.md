# IconPet 🐱

A small Tamagotchi-style desktop pet built with **Python and PySide6**.

IconPet lives directly on the desktop as a transparent, always-on-top animated cat. The pet can walk, sleep, play, become hungry or tired, and respond to user interactions.

## Features

- Animated desktop pet
- Transparent frameless window
- Always-on-top behavior
- Idle, walking, sleeping and playing animations
- Left/right movement across the desktop
- Hunger and energy system
- Context interaction menu
- Different behaviors depending on the pet's current state
- Status messages for hunger and tiredness

## Technologies

- Python
- PySide6 / Qt
- QTimer-based animation
- QPixmap sprite rendering
- Event-driven programming

## How It Works

IconPet uses a transparent PySide6 window containing animated sprite frames.

Different animation states are managed depending on the current behavior of the pet:

```text
Idle
Walking
Sleeping
Playing
```

Timers are used to update animation frames, movement and the pet's internal status.

The pet also maintains basic Tamagotchi-style statistics such as:

- Hunger
- Energy

These values change over time and influence the pet's behavior.

## Interaction

The pet can be interacted with through a context menu.

Available actions can trigger behaviors such as:

- Playing
- Sleeping
- Feeding
- Changing the current animation state

The cat can also display messages when it becomes hungry or tired.

## Animation System

Animations are created using sequences of sprite images.

Examples include:

```text
idle_front_1.png
idle_front_2.png
idle_front_3.png

walk_left_1.png
walk_left_2.png

walk_right_1.png
walk_right_2.png

sleep_1.png
sleep_2.png
```

The application cycles through these frames using Qt timers to create the animation.

## Demo

Add a GIF or screenshot here once you have one:

```html
<p align="center">
  <img src="docs/iconpet-demo.gif" width="500">
</p>
```

## Running IconPet

Install the required dependency:

```bash
pip install PySide6
```

Then run the application:

```bash
python main.py
```

> Replace `main.py` with the actual entry-point filename if it is different.

## Project Structure

A typical structure looks like:

```text
IconPet/
├── main.py
├── assets/
│   ├── idle_front_1.png
│   ├── idle_front_2.png
│   ├── idle_front_3.png
│   ├── walk_left_1.png
│   ├── walk_right_1.png
│   ├── sleep_1.png
│   └── ...
├── docs/
│   └── iconpet-demo.gif
├── requirements.txt
└── README.md
```

## Concepts Demonstrated

This project explores:

- Desktop GUI development
- Event-driven programming
- State management
- Sprite animation
- Timers and asynchronous UI events
- User interaction handling
- Basic virtual-pet mechanics

## Motivation

IconPet was created as a personal project to experiment with desktop GUI development while building something interactive and visually engaging.

The goal was to combine simple game-like mechanics with a lightweight desktop application.
