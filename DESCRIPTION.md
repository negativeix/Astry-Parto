ASTRY Parto

Project Overview
"ASTRY Parto" is a game where you control a spaceship from a Top-Down View perspective. The spaceship constantly moves forward. There are two control buttons: one for rotating the spaceship clockwise (press it twice quickly to dash) and the other for shooting bullets. The goal of the game is to control your spaceship and shoot down other ships until you're the last one remaining.

Project Review
The reference game is Astro Party, which was played on a tablet when I was younger. My goal is to make it playable on a computer and add special skills, as well as create different level designs.

Programming Development
3.1 Game Concept
"Astry Parto" is a game where players control a spaceship in a Top-Down view. The spaceship constantly moves forward, and players can rotate and shoot to attack other ships. The game will include special skills, such as dashing to dodge or shooting special bullets with unique effects that vary depending on the difficulty level. The goal is to destroy other bots(players)' ships and be the last one remaining.

3.2  Object-Oriented Programming Implementation
Spaceship – Manages movement and rotation of the spaceship.
Bullet – Handles bullet creation and movement.
Obstacle – Creates obstacles and detects collisions.
GameManager – Controls game start, scorekeeping, and game over conditions.
Power – Manages power-ups such as lasers and special bullets.

UML: https://lucid.app/lucidchart/74cea01b-97d6-4557-aa8a-55fad4c31f65/edit?viewport_loc=-639%2C153%2C2992%2C1405%2CHWEp-vi-RSFO&invitationId=inv_ba21e04e-eff6-4c13-a41c-5338933c70d9


3.3 Algorithms Involved
Event-Driven Mechanism
 The game listens for player inputs, like rotating the spaceship or shooting bullets, and responds immediately. For example, when a key is pressed, the spaceship will rotate or a bullet will be fired without delay.


Rule-Based Logic
 The game ensures that player actions follow the rules, such as making sure the player can only shoot after the cooldown period or perform a dash only when the direction key is pressed twice quickly. This helps keep the gameplay fair and structured.


Randomization
 Power-ups are randomly spawned whenever an Obstacle is destroyed. This means every time an obstacle is destroyed, the game will randomly select a power-up (like Laser or Triple Bullet) and place it in a random location, making each playthrough feel fresh and unpredictable.


Collision Detection
 The game constantly checks if the Spaceship or Bullets collide with obstacles. When a collision occurs, the game will trigger the appropriate response, such as destroying the obstacle or causing damage to the spaceship.


Statistical Data (Prop Stats)
4.1 Data Features

1. Accuracy which measures how accurate the player is by calculating the ratio of successful hits to total bullets fired
2. Time Played which tracks how much time the player spends in each game session, helping us understand how long players engage with the game
3. Bullets Fired which records the number of bullets the player fires during the game and gives insight into the player's playstyle
4. Obstacles Destroyed which tracks how many obstacles the player has destroyed, showing how well they are progressing through the game
5. Dash Usage which measures how often the player uses the dash ability, helping us analyze how important this movement strategy is in their gameplay.



4.2 Data Recording Method
The data will be stored in the CSV file.

4.3 Data Analysis Report
Use bar charts show the frequency of each number of on the number of Accuracy,Time played,Bullets Fired,Obstacles Destroyed and Dash Usage

4. Project Timeline

Week
Task
1 (10 March)
Proposal submission / Project initiation
2 (17 March)


3 (24 March)
Full proposal summit
4 (31 March)
Finish the base code of all features
5 (7 April)
Implement data tracking system 
6 (14 April)
Submission week (Draft)





