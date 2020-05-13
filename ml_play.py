"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm
import random
import pickle

def ml_loop(side: str):
    """
    The main loop for the machine learning process
    The `side` parameter can be used for switch the code for either of both sides,
    so you can write the code for both sides in the same script. Such as:
    ```python
    if side == "1P":
        ml_loop_for_1P()
    else:
        ml_loop_for_2P()
    ```
    @param side The side which this script is executed for. Either "1P" or "2P".
    """

    p1 = []
    p2 = []

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False
    is_hit_side = False
    is_hit_btm = False
    counter = 1

    def get_hit_bottom_pred():
        frame = ( 260 - scene_info['ball'][1] ) // scene_info["ball_speed"][1] # 幾個frame以後會需要接  # frame means how many frames before catch the ball
        pred = scene_info["ball"][0]+(scene_info["ball_speed"][0]*frame)  # 預測最終位置 # pred means predict ball landing site 
        bound = pred // 200 # Determine if it is beyond the boundary
        if (bound > 0): # pred > 200 # fix landing position # 超出右邊界
            if (bound%2 == 0) :
                pred = pred - bound*200                    
            else :
                pred = 200 - (pred - 200*bound)
        elif (bound < 0) : # pred < 0 # 超出左邊界
            if (bound%2 ==1) :
                pred = abs(pred - (bound+1) *200) 
            else :
                pred = pred + (abs(bound)*200)

        if bound % 2 == 1:
            new_ball_speed = [scene_info['ball_speed'][0] * -1, scene_info['ball_speed'][1] * -1]
        else:
            new_ball_speed = [scene_info['ball_speed'][0], scene_info['ball_speed'][1] * -1]

        return [pred, frame, new_ball_speed]

    def get_hit_pred(floor):
        x = (floor - scene_info['ball'][1]) // scene_info['ball_speed'][1] # 幾個frame以後會需要接  # x means how many frames before catch the ball
        pred = scene_info['ball'][0] + (scene_info['ball_speed'][0] * x)  # 預測最終位置 # pred means predict ball landing site 
        bound = pred // 200 # Determine if it is beyond the boundary
        if (bound > 0): # pred > 200 # fix landing position # 超出右邊界
            if (bound % 2 == 0) :
                pred = pred - bound*200                    
            else :
                pred = 200 - (pred - 200*bound)
        elif (bound < 0) : # pred < 0 # 超出左邊界
            if (bound % 2 == 1) :
                pred = abs(pred - (bound+1) *200) 
            else :
                pred = pred + (abs(bound)*200) 
            
        # new_fix_speed
        new_fix_speed = [scene_info['ball_speed'][0] * -1, scene_info['ball_speed'][1]]
        return [pred, x, new_fix_speed]

    def check_hit_the_blocker_side(set_260, set_240, blocker_x, hit_side:str, blocker_speed_x):
        if (blocker_x == set_260[0]): 
            # print("HIT!!!")
            is_hit_side = True
            return [set_260[0], 260, set_260[2]]
        elif (blocker_x == set_240[0]):
            # print("HIT!!!")
            is_hit_side = True
            return [set_240[0], 240, set_240[2]]
        elif set_260[0] <= set_240[0] and hit_side == 'HIT_RIGHT': 
            # hit the blocker on the RIGHT
            blocker_260 = (blocker_x + 30) + blocker_speed_x * set_260[1]
            blocker_240 = (blocker_x + 30) + blocker_speed_x * set_240[1]
            
            if blocker_240 >= 200:
                blocker_240 = (400 - blocker_240) 
            else:
                blocker_240 = blocker_240
            
            if blocker_260 >= 200:
                blocker_260 = (400 - blocker_260)
            else:
                blocker_260 = blocker_260

            if set_260[0] <= blocker_260 and blocker_260 <= set_240[0]:
                # print("HIT!!!")
                is_hit_side = True
                return [blocker_260, 240 + (set_240[0] - blocker_260), set_260[2]]
            elif set_260[0] <= blocker_240 and blocker_240 <= set_240[0]:
                # print("HIT!!!")
                is_hit_side = True
                return [blocker_240, 240 + (set_240[0] - blocker_260), set_240[2]]
            else:
                return [-1, -1]

        elif set_260[0] >= set_240[0] and hit_side == 'HIT_LEFT':
            # hit the blocker on the LEFT
            blocker_260 = abs((blocker_x) + blocker_speed_x * set_260[1])
            blocker_240 = abs((blocker_x) + blocker_speed_x * set_240[1])
            
            if set_240[0] <= blocker_260 and blocker_260 <= set_260[0]:
                # print("HIT!!!")
                is_hit_side = True
                return [blocker_260, 240 + (blocker_260 - set_240[0]), set_260[2]]
            elif set_240[0] <= blocker_240 and blocker_240 <= set_260[0]:
                # print("HIT!!!")
                is_hit_side = True
                return [blocker_240, 240 + (blocker_240 - set_240[0]), set_240[2]]
            else:
                return [-1, -1]
        return [-1, -1]

    def check_hit_the_blocker_bottom(set_bottom, blocker_x, blocker_speed_x):
        # set_bottom = [pred, frame, ball_speed_x, ball_speed_y]
        blocker_base = blocker_x + blocker_speed_x * set_bottom[1]
        if scene_info['ball'][1] - 260 >= 0:
            if blocker_base <= set_bottom[0] and (blocker_base + 30) >= set_bottom[0]:
                print('-----------------------------------')
                print(blocker_base, set_bottom[0], blocker_base + 30)
                print("HIT!!", set_bottom[0], 260, set_bottom[2])
                is_hit_btm = True
                return [set_bottom[0], 260, set_bottom[2]]

        return [-1, -1]

    def ml_loop_for_hit_bottom(fix_bottom_x:int, fix_bottom_y:int, fix_speed:list):
        x = ( scene_info["platform_1P"][1] - fix_bottom_y - 5 ) // fix_speed[1] # 幾個frame以後會需要接  # x means how many frames before catch the ball
        pred = fix_bottom_x+(fix_speed[0]*x)                                    # 預測最終位置 # pred means predict ball landing site 
        bound = pred // 200                                                     # Determine if it is beyond the boundary
        if (bound > 0):                                                         # pred > 200 # fix landing position # 超出右邊界
            if (bound%2 == 0) :
                pred = pred - bound*200                    
            else :
                pred = 200 - (pred - 200*bound)
        elif (bound < 0) : # pred < 0 # 超出左邊界
            if (bound%2 ==1) :
                pred = abs(pred - (bound+1) *200) 
            else :
                pred = pred + (abs(bound)*200) 
        return move_to(player = '1P',pred = pred)
        
    def ml_loop_for_hit_brick(fix_side_x:int, fix_side_y:int, fix_speed:list): 
        if scene_info["ball_speed"][1] > 0 :                                                # 球正在向下 # ball goes down
            x = ( scene_info["platform_1P"][1] - fix_side_y - 5 ) // fix_speed[1] # 幾個frame以後會需要接  # x means how many frames before catch the ball
            pred = fix_side_x+(fix_speed[0]*x)                                    # 預測最終位置 # pred means predict ball landing site 
            bound = pred // 200                                                             # Determine if it is beyond the boundary
            if (bound > 0):                                                                 # pred > 200 # fix landing position # 超出右邊界
                if (bound%2 == 0) :
                    pred = pred - bound*200                    
                else :
                    pred = 200 - (pred - 200*bound)
            elif (bound < 0) : # pred < 0 # 超出左邊界
                if (bound%2 ==1) :
                    pred = abs(pred - (bound+1) *200) 
                else :
                    pred = pred + (abs(bound)*200) 
            return move_to(player = '1P',pred = pred)
        else : # 球正在向上 # ball goes up
            return move_to(player = '1P',pred = 85)

    def move_to(player, pred) : #move platform to predicted position to catch ball 
        if player == '1P':
            if scene_info["platform_1P"][0]+20  > (pred-3) and scene_info["platform_1P"][0]+20 < (pred+3): return 0 # NONE
            elif scene_info["platform_1P"][0]+20 <= (pred-3) : return 1 # goes right
            else : return 2 # goes left
        else :
            if scene_info["platform_2P"][0]+20  > (pred-3) and scene_info["platform_2P"][0]+20 < (pred+3): return 0 # NONE
            elif scene_info["platform_2P"][0]+20 <= (pred-3) : return 1 # goes right
            else : return 2 # goes left

    def ml_loop_for_1P(): 
        if scene_info["ball_speed"][1] > 0 : # 球正在向下 # ball goes down
            x = ( scene_info["platform_1P"][1] - scene_info["ball"][1] - 5 ) // scene_info["ball_speed"][1] # 幾個frame以後會需要接  # x means how many frames before catch the ball
            pred = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x)  # 預測最終位置 # pred means predict ball landing site 
            bound = pred // 200 # Determine if it is beyond the boundary
            if (bound > 0): # pred > 200 # fix landing position # 超出右邊界
                if (bound%2 == 0) :
                    pred = pred - bound*200                    
                else :
                    pred = 200 - (pred - 200*bound)
            elif (bound < 0) : # pred < 0 # 超出左邊界
                if (bound%2 ==1) :
                    pred = abs(pred - (bound+1) *200) 
                else :
                    pred = pred + (abs(bound)*200) 

            # return pred
            # print("pred = ", pred)
            p1.append([scene_info['frame'], pred])
            return move_to(player = '1P',pred = pred)
        else : # 球正在向上 # ball goes up
            # print("pred = ", 85)
            p1.append([scene_info['frame'], 85])
            return move_to(player = '1P',pred = 85)
            # return 100

    def ml_loop_for_2P():  # as same as 1P
        if scene_info["ball_speed"][1] > 0 :
            # return 100
            # print("pred = ", 100)
            p2.append([scene_info['frame'], 85])
            return move_to(player = '2P',pred = 85)
        elif scene_info["ball_speed"][1] < 0: 
            x = ( scene_info["platform_2P"][1]+30-scene_info["ball"][1] ) // (scene_info["ball_speed"][1]) 
            pred = scene_info["ball"][0]+((scene_info["ball_speed"][0])*x) 
            bound = pred // 200 
            if (bound > 0):
                if (bound%2 == 0):
                    pred = pred - bound*200 
                else :
                    pred = 200 - (pred - 200*bound)
            elif (bound < 0) :
                if bound%2 ==1:
                    pred = abs(pred - (bound+1) *200)
                else :
                    pred = pred + (abs(bound)*200)
            # return pred
            # print("pred = ", pred)
            p2.append([scene_info['frame'], pred])
            return move_to(player = '2P',pred = pred)

    # 2. Inform the game process that ml process is ready
    comm.ml_ready()
    scene_info = comm.recv_from_game()
    old_ball = scene_info["ball"]
    vector = [7, 7]
    reflect = False
    
    

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False

            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information

        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
            # comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
            comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_RIGHT"})
            ball_served = True
        else:
            if side == "1P":
                command = ml_loop_for_1P()
            else:
                command = ml_loop_for_2P()
                
            '''if side == "1P":
                if scene_info['ball_speed'][1] < 0 and scene_info['ball'][1] >= 260:
                    set_bottom = get_hit_bottom_pred()  # check hit bottom
                    fix_bottom = check_hit_the_blocker_bottom(set_bottom, scene_info['blocker'][0], scene_info['blocker_speed'][0])

                    if fix_bottom != [-1, -1]:
                        ml_loop_for_hit_bottom(fix_bottom[0], fix_bottom[1], fix_bottom[2])
                    else:
                        command = ml_loop_for_1P()
                else:
                    command = ml_loop_for_1P()'''
            '''if scene_info['ball_speed'][1] > 0:
                    if not is_hit_side:
                        # check hit side
                        if scene_info['ball_speed'][0] > 0:
                            # deal hit blocker with right 
                            hit_side = 'HIT_RIGHT'
                        else:
                            # deal hit blocker with left 
                            hit_side = 'HIT_LEFT'

                        set_240 = get_hit_pred(240)         
                        set_260 = get_hit_pred(260)
                        fix_side = check_hit_the_blocker_side(set_260, set_240, scene_info['blocker'][0], hit_side, scene_info['blocker_speed'][0])
                else:
                    fix_side = [-1, -1]

                if fix_side != [-1, -1]:
                    print("HIT SIDE", counter)
                    ml_loop_for_hit_brick(fix_side[0], fix_side[1], fix_side[2])
                else:'''
                
            '''elif fix_bottom != [-1, -1]:
                    print("pred HALF", fix_bottom)
                    ml_loop_for_hit_bottom(fix_bottom[0], fix_bottom[1], fix_bottom[2])'''
                # command = ml_loop_for_1P()
            


            if command == 0:
                comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
            elif command == 1:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            else :
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})

            '''if is_hit_btm:
                print(scene_info)
            
            if scene_info['ball'][1] < 260 and is_hit_btm:
                print("IN")
                counter += 1
                is_hit_btm = False'''

            
            
            # print(p1[counter], p2[counter])
    
            # record pred
            '''with open('/Users/jjjjjacckk/Desktop/p1.pickle', 'wb') as f:
                pickle.dump(p1, f)
            
            with open('/Users/jjjjjacckk/Desktop/p2.pickle', 'wb') as f:
                pickle.dump(p2, f)'''