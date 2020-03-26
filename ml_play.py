"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)

def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # Self_defined variable

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            old_ball_0 = scene_info.ball[0]
            old_ball_1 = scene_info.ball[1]
            old_ball_x_speed = -7
            counter = 0
            ball_served = True

        # platform adjastment starts when the Y gap between platform and ball is 300
        # elif (old_ball_0 >= scene_info.ball[0]):
        # elif old_ball_1 <= scene_info.ball[1] or \
        #     scene_info.platform[1] - scene_info.ball[1] <= 120:
        elif (scene_info.ball[1] - old_ball_1) > 0 or \
             scene_info.platform[1] - scene_info.ball[1] <= 120 or \
             (scene_info.ball[0] - old_ball_0) != old_ball_x_speed:

            # print("boolean:\n")
            # print(  scene_info.ball_speed[1] == -7, " " \
            #       , scene_info.platform[1] - scene_info.ball[1] <= 120, " " \
            #       , scene_info.ball_speed[1] != old_ball_x_speed, "\n")

            # calculate the where center should be through reflection theorem
            if (scene_info.ball[0] - old_ball_0) >= 0:
                center_should_be_ori = scene_info.ball[0] + (scene_info.platform[1] - scene_info.ball[1])
                if center_should_be_ori > 200:
                    center_should_be_ori = 400 - center_should_be_ori
                center_trim = center_should_be_ori - (center_should_be_ori % 10) 
            elif (scene_info.ball[0] - old_ball_0) < 0:
                center_should_be_ori = abs(scene_info.ball[0] - (scene_info.platform[1] - scene_info.ball[1]))
                center_trim = center_should_be_ori - (center_should_be_ori % 10) 
            
            # print("OLD:")
            # print("\t", center_should_be_ori, " ", center_trim, "\n")
            
            x_axis = abs(old_ball_0 - scene_info.ball[0]) != 7 and old_ball_0 != scene_info.ball[0]
            y_axis = abs(old_ball_1 - scene_info.ball[1]) != 7 and old_ball_1 != scene_info.ball[1]

            if (x_axis or y_axis):
                counter += 1
                # center_should_be_ori = abs(scene_info.ball[0] - (scene_info.platform[1] - scene_info.ball[1]))
                # center_trim = center_should_be_ori - (center_should_be_ori % 10)
                # print("!!!!CHANGE!!!!") 
                
                # print("\nNEW:")
                # print("\t", center_should_be_ori, " ", center_trim)
                
                # print(old_ball_0, " ", scene_info.ball[0], " ", scene_info.ball[0] - old_ball_0)
                # print(old_ball_1, " ", scene_info.ball[1], " ", scene_info.ball[1] - old_ball_1, "\n")
                # print("counter = ", counter)
                # print("!!!!!!!!!!!!!!FIND!!!!!!!!!!!!!!")
            # print("      estimate = ", center_should_be_ori, " ", center_trim)
            # print("    Ball speed = ", scene_info.ball_speed)
            # print("platform speed = ", scene_info.platform_speed)
            # print("          ball = ", scene_info.ball[0], " ", scene_info.ball[1])
            # print("      platform = ", scene_info.platform[0], " ", scene_info.platform[1])
            # print("----------------------------------")
            
            # print("EST  = ", center_should_be_ori, " ", center_trim)
            # print("ball = ", scene_info.ball[0], " ", scene_info.ball[1])
            # print("----------------------------------")

            old_ball_0 = scene_info.ball[0]
            old_ball_1 = scene_info.ball[1]
            old_ball_x_speed = scene_info.ball[0] - old_ball_0


            # setoff is set to be on the center of platform
            # if platform's X is not equal to the "center_should_be_ori", move it to either right and left
            if (scene_info.platform[0] > center_trim):
               comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                    
            elif (scene_info.platform[0] < center_trim):
               comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)

        # reset the platform to original position to gain more time for following moves
        elif (scene_info.platform[0] != 75):
            if (scene_info.platform[0] > 75):
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            elif (scene_info.platform[0] < 75):
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)

        else:
            # print(old_ball_0, " ", scene_info.ball[0], " ", scene_info.ball[0] - old_ball_0)
            # print(old_ball_1, " ", scene_info.ball[1], " ", scene_info.ball[1] - old_ball_1, "\n")
            
            # print("    Ball speed = ", scene_info.ball_speed)
            # print("platform speed = ", scene_info.platform_speed)
            # print("----------------------------------")
            
            # print("    Ball speed = ", scene_info.ball_speed)
            # print("platform speed = ", scene_info.platform_speed)
            # print("----------------------------------")
            old_ball_0 = scene_info.ball[0]
            old_ball_1 = scene_info.ball[1]

            comm.send_instruction(scene_info.frame, PlatformAction.NONE)
'''
'''
