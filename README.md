# Autoboi v1.0
Auto BOI(Battle of Infinity) Plugin for PhBot

Completes the BOI on Silkroad Online automatically by injecting packets.

Only works for 71-80 and 81-90 and in Donwhang. It is currently fully functioning but I won't update or do bug fixes. It selects the corresponding BOI automatically according to the character level.

# Requirements:

- PhBot 25.3.3 or higher(You can not inject skill packets with lower versions)
- PhBot plugin package with Python 3.8+

# How to use:

- Copy the .py file into your Plugin folder and reload the plugins on bot. If it doesn't work, check requirements.
- **Solo**: Place your character somewhere near arena manager in Donwhang, just press Start BOI Solo(Button 3) and enjoy
- **Party**: Same as in Solo, first enter the party master and then party members. !!! The party master will first start when all party members have arrived!!!!!

![boi](https://user-images.githubusercontent.com/44427363/110676718-93580080-81d4-11eb-8dfc-cf7f172ef53b.png)

- 1: Hides the information log in the bot console.
- 2: Hides the attack log in the bot console.
- 3: Start BOI Solo only in Donwhang
- 4: Start BOI Party(Master), starts the BOI as a master. Use this for the party master. It will enter and wait for all party members to start the battle.
- 5: Start BOI Party(Master), starts the BOI as a member. Use this for the party members. It will teleport, transform and will look for monsters to attack.
- 6: Stops the bot. It might take a while for it to join the thread. stop_flag is only caught in loops.
