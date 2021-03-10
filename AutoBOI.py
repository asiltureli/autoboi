from phBot import *
from threading import Timer, Thread
from dataclasses import dataclass
from random import choice

import QtBind
import struct
import json
import os
import sys
import time
import pickle


############## Needed Data ##########################
MAX_ATTEMPT             = 3
BOIthread               = False
player_inside           = False
char_data               = False
char_level              = False
running                 = 0
stopFlag                = 0
patrol_counter          = 0
show_log                = True
show_attack_log         = True
# Arena Manager
dw_arena_manager_packet = b'\x87\x01\x00\x00' # Arena Manager in DW
dw_arena_manager_id     = 391
# Commands
command_inject_select   = 0x7045 # Select NPC or mob
command_boi_enter       = 0x705A # Enter BOI
command_close_npc       = 0x704B # Close NPC
command_inject_npc      = 0x7588 # Inject NPC
command_cast_skill      = 0x7074 # Cast skill
# Packets
boi_solo_71_80          = b'\x02\xE4\x00\x00\x00'
boi_solo_81_90          = b'\x02\xE5\x00\x00\x00'
boi_pt_71_80            = b'\x02\xE6\x00\x00\x00'
boi_pt_81_90            = b'\x02\xE7\x00\x00\x00'

# 71-80 Solo
solo_75_dungeon_master_packet = b'\x6F\x0A\x00\x00'
solo_75_dungeon_master_id = 2671

solo_yeoha_75_packet         = b'\x70\x0A\x00\x00'
solo_yeoha_75_id             = 2672
solo_yeoha_transform         = b'\x03\x70\x0A\x00\x00'

# solo_yeoha_skill_1           = b'\x01\x04\x0F\x87\x00\x00\x01'
# solo_yeoha_skill_2           = b'\x01\x04\x0E\x87\x00\x00\x01'

# 81-90 Solo
solo_85_dung_master_pkt      = b'\x72\x0A\x00\x00'
solo_85_dung_master_id       = 2674

solo_niya_shaman_85_packet   = b'\x73\x0A\x00\x00'
solo_niya_shaman_85_id       = 2675
solo_niya_shaman_transform   = b'\x03\x73\x0A\x00\x00'

# solo_niya_shaman_skill_1     = b'\x01\x04\x12\x87\x00\x00\x01'
# solo_niya_shaman_skill_2     = b'\x01\x04\x13\x87\x00\x00\x01'

# 71-80 Party
party_75_dungeon_master_packet = b'\x75\x0A\x00\x00'
party_75_dungeon_master_id = 2677

party_yeoha_75_packet         = b'\x76\x0A\x00\x00'
party_yeoha_75_id             = 2678
party_yeoha_transform         = b'\x03\x76\x0A\x00\x00'

# party_yeoha_skill_1           = b'\x01\x04\x11\x87\x00\x00\x01'
# party_yeoha_skill_2           = b'\x01\x04\x10\x87\x00\x00\x01'

# 81-90 Party
party_85_dung_master_pkt      = b'\x78\x0A\x00\x00'
party_85_dung_master_id       = 2680

party_niya_shaman_85_packet   = b'\x79\x0A\x00\x00'
party_niya_shaman_85_id       = 2681
party_niya_shaman_transform   = b'\x03\x79\x0A\x00\x00'

# party_niya_shaman_skill_1     = b'\x01\x04\x1B\x87\x00\x00\x01'
# party_niya_shaman_skill_2     = b'\x01\x04\x1A\x87\x00\x00\x01'

# Skills
yeoha_skill_1                 = b'\x01\x04\x0F\x87\x00\x00\x01'
yeoha_skill_2                 = b'\x01\x04\x0E\x87\x00\x00\x01'
yeoha_skill_3                 = b'\x01\x04\x11\x87\x00\x00\x01'
yeoha_skill_4                 = b'\x01\x04\x10\x87\x00\x00\x01'

shaman_skill_1                = b'\x01\x04\x12\x87\x00\x00\x01'
shaman_skill_2                = b'\x01\x04\x13\x87\x00\x00\x01'
shaman_skill_3                = b'\x01\x04\x1A\x87\x00\x00\x01'
shaman_skill_4                = b'\x01\x04\x1B\x87\x00\x00\x01'

# GUI
gui = QtBind.init(__name__,'Auto BOI')

Btn_BOI_solo            = QtBind.createButton(gui,'startSoloBOI',"  Start BOI Solo  ", 150, 50)
Btn_BOI_pt_master       = QtBind.createButton(gui,'startPtBOI_Master',"  Start BOI Party (Master)  ",350, 50)
Btn_BOI_pt_member       = QtBind.createButton(gui,'startPtBOI_Member',"  Start BOI Party (Member)  ", 350,80)
Btn_stop                = QtBind.createButton(gui,'setStopFlag',"  Stop  ", 250, 120)
CBox_hide_log           = QtBind.createCheckBox(gui, 'hide_log','Hide Log', 10, 10)
CBox_hide_attack_log    = QtBind.createCheckBox(gui, 'hide_attack_log','Hide Attack Log', 10, 30)

'''
Btn_debug               = QtBind.createButton(gui,'f_debug',"  Debug  ", 650,10)
'''
# Dataclass for different BOI versions
@dataclass
class boi_dataclass:
    # NPC information
    arena_manager_packet: bytes
    arena_manager_id: int

    # Packet for entering BOI
    boi_packet: bytes

    # Dungeon Master Info inside
    dungeon_master_packet: bytes
    dungeon_master_id: int

    # Data needed For transformation
    transform_npc_packet: bytes
    transform_npc_id: int
    transform_packet: bytes

    # Skill packets
    skill_1: bytes
    skill_2: bytes
    skill_3: bytes
    skill_4: bytes

def teleported():
    global char_data, char_level, running
    char_data = get_character_data()
    char_level = char_data['level']
    running = 0

print('Auto BOI succesfully loaded')
def startSoloBOI():
    global char_level, MAX_ATTEMPT, BOIthread
    char_data = get_character_data()
    char_level = char_data['level']
    if show_log:
        log('Char Level: ' + str(char_level))
    if char_level < 81:
        if show_log:
            log('Selected: Solo BOI 71-80')
        boi_data = boi_dataclass(
            arena_manager_packet        = dw_arena_manager_packet,
            arena_manager_id            = dw_arena_manager_id,
            boi_packet                  = boi_solo_71_80,
            dungeon_master_packet       = solo_75_dungeon_master_packet,
            dungeon_master_id           = solo_75_dungeon_master_id,
            transform_npc_packet        = solo_yeoha_75_packet,
            transform_npc_id            = solo_yeoha_75_id,
            transform_packet            = solo_yeoha_transform,
            skill_1                     = yeoha_skill_1,
            skill_2                     = yeoha_skill_2,
            skill_3                     = yeoha_skill_3,
            skill_4                     = yeoha_skill_4
            ) 
    else:
        if show_log:
            log('Selected: Solo BOI 81-90')
        boi_data = boi_dataclass(
            arena_manager_packet        = dw_arena_manager_packet,
            arena_manager_id            = dw_arena_manager_id,
            boi_packet                  = boi_solo_81_90,
            dungeon_master_packet       = solo_85_dung_master_pkt,
            dungeon_master_id           = solo_85_dung_master_id,
            transform_npc_packet        = solo_niya_shaman_85_packet,
            transform_npc_id            = solo_niya_shaman_85_id,
            transform_packet            = solo_niya_shaman_transform,
            skill_1                     = shaman_skill_1,
            skill_2                     = shaman_skill_2,
            skill_3                     = shaman_skill_3,
            skill_4                     = shaman_skill_4
            ) 
    pt_info = get_party()
    if len(list(pt_info.keys())) != 0: 
        log('Leaving Party')
        inject_joymax(0x7061, bytes(), False)
    BOIthread = Thread(target=startBOI, args=(boi_data,))
    BOIthread.start()

def startPtBOI_Master():
    global char_level, MAX_ATTEMPT, BOIthread
    char_data = get_character_data()
    char_level = char_data['level']
    if show_log:
        log('Char Level: ' + str(char_level))
    if char_level < 81:
        if show_log:
            log('Selected: Party BOI 71-80')
        boi_data = boi_dataclass(
            arena_manager_packet        = dw_arena_manager_packet,
            arena_manager_id            = dw_arena_manager_id,
            boi_packet                  = boi_pt_71_80,
            dungeon_master_packet       = party_75_dungeon_master_packet,
            dungeon_master_id           = party_75_dungeon_master_id,
            transform_npc_packet        = party_yeoha_75_packet,
            transform_npc_id            = party_yeoha_75_id,
            transform_packet            = party_yeoha_transform,
            skill_1                     = yeoha_skill_1,
            skill_2                     = yeoha_skill_2,
            skill_3                     = yeoha_skill_3,
            skill_4                     = yeoha_skill_4
            ) 
    else:
        if show_log:
            log('Selected: Party BOI 81-90')
        boi_data = boi_dataclass(
            arena_manager_packet        = dw_arena_manager_packet,
            arena_manager_id            = dw_arena_manager_id,
            boi_packet                  = boi_pt_81_90,
            dungeon_master_packet       = party_85_dung_master_pkt,
            dungeon_master_id           = party_85_dung_master_id,
            transform_npc_packet        = party_niya_shaman_85_packet,
            transform_npc_id            = party_niya_shaman_85_id,
            transform_packet            = party_niya_shaman_transform,
            skill_1                     = shaman_skill_1,
            skill_2                     = shaman_skill_2,
            skill_3                     = shaman_skill_3,
            skill_4                     = shaman_skill_4
            ) 

    BOIthread = Thread(target=startBOI_master, args=(boi_data,))
    BOIthread.start()

def startPtBOI_Member():
    global char_level, MAX_ATTEMPT, BOIthread
    char_data = get_character_data()
    char_level = char_data['level']
    if show_log:
        log('Char Level: ' + str(char_level))
    if char_level < 81:
        if show_log:
            log('Selected: Party BOI 71-80')
        boi_data = boi_dataclass(
            arena_manager_packet        = dw_arena_manager_packet,
            arena_manager_id            = dw_arena_manager_id,
            boi_packet                  = boi_pt_71_80,
            dungeon_master_packet       = party_75_dungeon_master_packet,
            dungeon_master_id           = party_75_dungeon_master_id,
            transform_npc_packet        = party_yeoha_75_packet,
            transform_npc_id            = party_yeoha_75_id,
            transform_packet            = party_yeoha_transform,
            skill_1                     = yeoha_skill_1,
            skill_2                     = yeoha_skill_2,
            skill_3                     = yeoha_skill_3,
            skill_4                     = yeoha_skill_4
            ) 
    else:
        if show_log:
            log('Selected: Party BOI 81-90')
        boi_data = boi_dataclass(
            arena_manager_packet        = dw_arena_manager_packet,
            arena_manager_id            = dw_arena_manager_id,
            boi_packet                  = boi_pt_81_90,
            dungeon_master_packet       = party_85_dung_master_pkt,
            dungeon_master_id           = party_85_dung_master_id,
            transform_npc_packet        = party_niya_shaman_85_packet,
            transform_npc_id            = party_niya_shaman_85_id,
            transform_packet            = party_niya_shaman_transform,
            skill_1                     = shaman_skill_1,
            skill_2                     = shaman_skill_2,
            skill_3                     = shaman_skill_3,
            skill_4                     = shaman_skill_4
            ) 

    BOIthread = Thread(target=startBOI_member, args=(boi_data,))
    BOIthread.start()


def startBOI(boi):
    global player_inside, stopFlag
    stopFlag = 0
    log('Starting...')
    openArenaNPC(boi)
    for enter_attempt in range(MAX_ATTEMPT):
        enterBOI(boi)
        time.sleep(10)
        checkIfInside(boi)
        if not player_inside:
            if show_log:
                log('Could not enter. Enter attempt: ' + str(enter_attempt + 1))
            continue
        else:
            if show_log:
                log('Succesfully entered BOI')
            break

        if stopFlag:
            break

    if not player_inside:
        if show_log:
            log('Aborting')
        return
    time.sleep(2)
    startBattle(boi)
    time.sleep(2)
    moveFromEnterToTransform()

    transform(boi)

    moveToStone()

    while 1:
        checkIfOutside(boi)
        try:
            if show_attack_log:
                log('Searching mobs')
            attackMobs(boi)
        except:
            log(sys.exc_info()[0])
            continue
        if stopFlag or not player_inside:
            break
    
    log('Finished BOI!!')

def startBOI_master(boi):
    global player_inside, stopFlag
    stopFlag = 0
    log('Starting...')
    openArenaNPC(boi)
    for enter_attempt in range(MAX_ATTEMPT):
        enterBOI(boi)
        time.sleep(10)
        checkIfInside(boi)
        if not player_inside:
            if show_log:
                log('Could not enter. Enter attempt: ' + str(enter_attempt + 1))
            continue
        else:
            if show_log:
                log('Succesfully entered BOI')
            break
        if stopFlag:
            break
    move_to(14674.0, 2592.0, 622.0)
    time.sleep(1.5)  
    if not player_inside:
        if show_log:
            log('Aborting')
        return
    time.sleep(2)
    while 1 and not stopFlag:
        ptMembers = get_party()
        if show_log:
            log('Checking if party members have arrived!')
        arrival = partyMembersInBOI()
        if arrival:
            break
        else:
            if show_log:
                log(str(len(list(ptMembers.keys()))) + ' players in pt. Waiting for them to join...')
            time.sleep(2)
    startBattle(boi)
    time.sleep(2)
    moveFromEnterToTransform()

    transform(boi)

    moveToStone()

    while 1:
        checkIfOutside(boi)
        try:
            if show_attack_log:
                log('Searching mobs')
            attackMobs(boi)
        except:
            log(sys.exc_info()[0])
            continue
        if stopFlag or not player_inside:
            break
    
    log('Finished BOI!!')


def startBOI_member(boi):
    global player_inside, stopFlag
    stopFlag = 0
    log('Starting...')
    openArenaNPC(boi)
    for enter_attempt in range(MAX_ATTEMPT):
        enterBOI(boi)
        time.sleep(10)
        checkIfInside(boi)
        if not player_inside:
            if show_log:
                log('Could not enter. Enter attempt: ' + str(enter_attempt + 1))
            continue
        else:
            if show_log:
                log('Succesfully entered BOI')
            break
        
        if stopFlag:
            break

    if not player_inside:
        if show_log:
            log('Aborting')
        return
    time.sleep(2)
    moveFromEnterToTransform()

    transform(boi)

    moveToStone()

    while 1:
        checkIfOutside(boi)
        try:
            if show_attack_log:
                log('Searching mobs')
            attackMobs(boi)
        except:
            log(sys.exc_info()[0])
            continue
        if stopFlag or not player_inside:
            break
    
    log('Finished BOI!!')

def timerInfo(text):
    log(text)
    
def setStopFlag():
    global stopFlag
    stopFlag = 1

def openArenaNPC(boi):

    global command_inject_select
    if show_log:
        log('Entering DW Arena Manager')
    try:
        response = inject_joymax(command_inject_select,boi.arena_manager_packet, False)
    except:
        if show_log:
            log('Cannot enter Arena Manager: ' + str(sys.exc_info()[0]))

def enterBOI(boi):
    global command_boi_enter
    if show_log:
        log('Entering BOI')
    try:
        response = inject_joymax(command_boi_enter, boi.arena_manager_packet + boi.boi_packet, False)
    except:
        if show_log:
            log('Cannot enter BOI: ' + str(sys.exc_info()[0]))

def startBattle(boi):
    global command_inject_npc, command_inject_select
    if show_log:
        log('Selecting Dungeon Master')
    inject_joymax(command_inject_select, boi.dungeon_master_packet, False)
    time.sleep(2)
    if show_log:
        log('Starting Battle')
    inject_joymax(command_inject_npc, b'\x01', False)
# Transforms to the monster
def transform(boi):
    global command_inject_select, command_close_npc
    inject_joymax(command_inject_select, boi.transform_npc_packet, False)
    time.sleep(1)
    inject_joymax(command_inject_npc, boi.transform_packet, False)
    time.sleep(0.5)
    inject_joymax(command_close_npc, boi.transform_npc_packet, False)
    if show_log:
        log('Transformed')

# Moves from entrance to transformation
def moveFromEnterToTransform():
    try:
        inject_joymax(0x7074, b'\x01\x04\x1B\x05\x00\x00\x00')
    except:
        pass
    move_to(14674.0, 2592.0, 622.0)
    time.sleep(1.5)
    move_to(14682.0, 2592.0, 586.0)
    time.sleep(1)
    move_to(14690.0, 2592.0, 524.0)
    time.sleep(1)
    move_to(14697.0, 2592.0, 462.0)
    time.sleep(1)
    move_to(14706.0, 2592.0, 384.0)
    time.sleep(1)
    move_to(14714.0, 2592.0, 376.0)
    time.sleep(1)
    move_to(14714.0, 2605.0, 376.0)
    time.sleep(1)

# Moves to stone to protext
def moveToStone():
    try:
        inject_joymax(0x7074, b'\x01\x04\x1B\x05\x00\x00\x00')
    except:
        pass
    move_to(14721.0, 2600.0, 381.0)
    time.sleep(0.5)
    move_to(14727.0, 2599.0, 381.0)
    time.sleep(0.5)
# Check if char is inside of arena
def checkIfInside(boi):
    global player_inside
    npcs = get_npcs()
    searched = [boi.dungeon_master_id, boi.transform_npc_id]
    if any(x in npcs.keys() for x in searched):
        player_inside = 1
        if show_log:
            log('Player is inside')
        return

  # Check if char is outside of arena  
def checkIfOutside(boi):
    global player_inside
    npcs = get_npcs()
    searched = [391]
    if any(x in npcs.keys() for x in searched):
        player_inside = 0
        if show_log:
            log('Player is outside')
        return
def npcCheck():
    moveFromEnterToTransform()

def attackMobs(boi):

    global command_cast_skill, command_inject_select, patrol_counter
    mobs = get_monsters()
    if not mobs:
        if show_attack_log:
            log('No Mobs are present, waiting...')
        if patrol_counter % 4 == 0:
            move_to(14740.0, 2593.0, 0)
        if patrol_counter % 4 == 1:
            move_to(14729.0, 2584.0, 0)
        if patrol_counter % 4 == 2:
            move_to(14722.0, 2593.0, 0)
        if patrol_counter % 4 == 3:
            move_to(14730.0, 2599.0, 0)
        patrol_counter += 1
        time.sleep(2)
    else:
        packet = bytearray()
        targetID = choice(list(mobs.keys()))
        if show_attack_log:
            log('Selecting mob')
        mobToSelect = packet + struct.pack('<I',targetID)
        inject_joymax(command_inject_select, mobToSelect, True)
        time.sleep(0.5)
        if show_attack_log:
            log('Attacking Mob')
        inject_joymax(command_cast_skill, boi.skill_1 + mobToSelect, False)
        time.sleep(0.5)
        inject_joymax(command_cast_skill, boi.skill_2 + mobToSelect, False)
        time.sleep(0.5)
        inject_joymax(command_cast_skill, boi.skill_3 + mobToSelect, False)
        time.sleep(0.5)
        inject_joymax(command_cast_skill, boi.skill_4 + mobToSelect, False)
        time.sleep(0.5)

def partyMembersInBOI():
    ptMembers = get_party()
    countMemberInBOI = 0
    for member in ptMembers:
        if (ptMembers[member]['x'] < 15000 and 
            ptMembers[member]['x'] > 14300 and 
            ptMembers[member]['y'] < 2700 and 
            ptMembers[member]['y'] > 2500):

            countMemberInBOI += 1

    log(str(countMemberInBOI) + ' party members are here.')
    if countMemberInBOI == len(list(ptMembers.keys())):
        return True
    else:
        return False

def hide_log(check):
    global show_log
    show_log = not check
def hide_attack_log(check):
    global show_attack_log
    show_attack_log = not check

'''
def f_debug():
    ptMembers = get_party()
    countMemberInBOI = 0
    for member in ptMembers:
        if (ptMembers[member]['x'] < 14850 and 
            ptMembers[member]['x'] > 14600 and 
            ptMembers[member]['y'] < 2650 and 
            ptMembers[member]['y'] > 2500):

            countMemberInBOI += 1

    log(str(countMemberInBOI) + ' party members are here.')
    if countMemberInBOI == len(list(ptMembers.keys())):
        return 1
    return 0
'''