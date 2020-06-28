import pickle
import os

class MLPlay:
    def __init__(self, player):
        self.player = player
        if self.player == "player1":
            self.player_no = 0
        elif self.player == "player2":
            self.player_no = 1
        elif self.player == "player3":
            self.player_no = 2
        elif self.player == "player4":
            self.player_no = 3
        self.car_vel = 0                            # speed initial
        self.car_pos = (0,0)                        # pos initial
        self.car_lane = self.car_pos[0] // 70       # lanes 0 ~ 8
        # self.DESTINATION = self.car_lane
        self.lanes = [35, 105, 175, 245, 315, 385, 455, 525, 595]  # lanes center
        self.pickle_counter = 0
        self.number = ''
        self.ID = self.player_no
        self.frame = 0

        # coin
        self.eat_coin = False
    
        # FLAG
        self.MOVE_LEFT_TAG = False
        self.MOVE_RIGHT_TAG = False
        self.THREAT = False
        self.DESTINATION = self.car_lane
        pass

    def update(self, scene_info):
        """
        9 grid relative position
        |    |    |    |
        |  1 |  2 |  3 |
        |    |  5 |    |
        |  4 |  c |  6 |
        |    |    |    |
        |  7 |  8 |  9 |
        |    |    |    |       
        """


        def check_grid_coin():
            coin_grid_function = set()
            for coin in scene_info['coins']:
                for lane in range(9):
                    if (coin[0] // 70 == lane) and coin[1] <= self.car_pos[1]:
                        coin_grid_function.add(lane)
                        break
            return coin_grid_function

        def check_grid():
            grid_coin = check_grid_coin()           # collect coin information
            grid = set()
            speed_ahead = 100
            # if self.car_pos[0] <= 65: # left bound
            if self.car_pos[0] <= 65: # left bound
                grid.add(1)
                grid.add(4)
                grid.add(7)
            # elif self.car_pos[0] >= 565: # right bound
            elif self.car_pos[0] >= 565: # right bound
                grid.add(3)
                grid.add(6)
                grid.add(9)

            # print('----------------------------')
            for car in scene_info["cars_info"]:
                if car["id"] != self.player_no:
                    x = self.car_pos[0] - car["pos"][0] # x relative position 
                    y = self.car_pos[1] - car["pos"][1] # y relative position
                    # print('-----------')
                    # print('get grid\n')
                    # print(x, y)

                    if x <= 35 and x >= -35 :      
                        if y > 0 and y < 200:
                            grid.add(2)
                            # print("\ncause 2:")
                            # print(car, end='\n\n')
                            if y < 150:
                                speed_ahead = car["velocity"]
                                grid.add(5) 
                        elif y < 0 and y > -200:
                            grid.add(8)
                    if x >= -75 and x < -35 :
                        if y > 80 and y < 200:
                            grid.add(3)
                        elif y < -80 and y > -200:
                            grid.add(9)
                        elif y <= 80 and y >= -80:
                            grid.add(6)
                    if x <= 75 and x > 35:
                        # print("left side")
                        # print(y > 80 and y < 200, y < -80 and y > -200, y <= 80 and y >= -80)
                        if y > 80 and y < 200:
                            grid.add(1)
                        elif y < -80 and y > -200:
                            grid.add(7)
                        elif y <= 80 and y >= -80:
                            grid.add(4)
            
            # print('-------------')
            # print('Before')
            # print(grid)
            # prevent from being hit by other cars
            if 2 not in grid:
                if 3 in grid or 6 in grid or 9 in grid \
                    or 1 in grid or 4 in grid or 7 in grid:
                    for car in scene_info["cars_info"]:
                        if car["id"] != self.player_no:
                            x = self.car_pos[0] - car["pos"][0] # x relative position
                            y = self.car_pos[1] - car["pos"][1] # y relative position

                            if abs(x) <= 60 and abs(y) <= 95:
                                grid.add(2)
                                grid.add(5)
            #                     # speed_ahead = self.car_vel - 0.1
                                
            #                     if self.car_lane <= 1 or self.car_lane >= 7:
            #                         self.THREAT = True

            #                     # print('|||||||||||||||||')
            #                     # print('------AVOID------')
            #                     # # print('-----------')
            #                     # print(grid)
            #                     # print(self.car_pos)
            #                     # print("LEFT_FLAG", self.MOVE_LEFT_TAG)
            #                     # print("RIGHT_FLAG", self.MOVE_RIGHT_TAG)
            #                     # print("DESTINATION", self.DESTINATION)
            #                     # print("car_lane   ", self.car_lane)
            #                     # print("player number", self.player_no)
            else:
                self.THREAT = False
            

            
            # log_file = '/Users/jjjjjacckk/Desktop/MLGame/games/RacingCar/log/grid.pickle'
            # log_file = '/Users/jjjjjacckk/Desktop/MLGame/games/RacingCar/log/' + '10' + '/grid'
            # seq = ['1.pickle', '2.pickle', '3.pickle', '4.pickle']

            # if os.path.getsize(log_file + seq[self.player_no]) > 0:
            #     try:
            #         with open(log_file + seq[self.player_no], 'rb+') as f:
            #             target = pickle.load(f)
            #         # print(target)

            #     except EOFError:
            #         with open(log_file + seq[self.player_no], 'rb+') as f:
            #             print(f)
            #             print(os.path.getsize(f))
            #             print(os.path.getsize(log_file))
            #             os.abort()
            # else:
            #     print("file empty")
            #     os.abort()

            # with open(log_file + seq[self.player_no], 'wb') as f:
            #     temp = []
            #     for element in grid:
            #         temp.append(element)
            #     # print(temp)
            #     target.append(temp)
            #     # print(target)
            #     pickle.dump(target, f)

            return move(grid = grid, grid_coin = grid_coin, speed_ahead = speed_ahead)
            
        def move(grid, grid_coin, speed_ahead): 
        #     if self.player_no == 1:
        #         print('-----------')
        #         print(grid)
        #         print(grid_coin)
        #         print(self.car_pos)
        #         print('CAR_NO\t\t', self.ID)
        #         print("LEFT_FLAG\t", self.MOVE_LEFT_TAG)
        #         print("RIGHT_FLAG\t", self.MOVE_RIGHT_TAG)
        #         print("DESTINATION\t", self.DESTINATION)
        #         print("car_lane\t", self.car_lane)
        #         print('EAT_COIN\t', self.eat_coin)
                # print("player number\t", self.player_no)
                # print('THREAT\t\t', self.THREAT)
                # print('Frame', self.frame)
                # print("-----\ncoin poistion")
                # print(scene_info['coins'])
                # print('-----------')
            if len(grid) == 0:
                # return ["SPEED", "MOVE_RIGHT"]
                # if self.car_lane != self.DESTINATION and self.DESTINATION != 0:
                # print("grid = 0")
                if self.DESTINATION == self.car_lane:
                    self.MOVE_LEFT_TAG = False
                    self.MOVE_RIGHT_TAG = False

                # # back to lane center
                # if self.car_pos[0] > self.lanes[self.car_lane] + 3:
                #         print("LEFT1")
                #         self.frame += 1
                #         return ["SPEED", "MOVE_LEFT"]
                # elif self.car_pos[0] < self.lanes[self.car_lane] - 3:
                #     print("1")
                #     self.frame += 1
                #     return ["SPEED", "MOVE_RIGHT"]
                if scene_info['frame'] <= 15:
                    self.DESTINATION = self.car_lane

                if (self.MOVE_LEFT_TAG or self.car_lane > self.DESTINATION):
                    self.frame += 1
                    return ["SPEED", "MOVE_LEFT"]
                elif (self.MOVE_RIGHT_TAG or self.car_lane < self.DESTINATION):
                    self.frame += 1
                    return ["SPEED", "MOVE_RIGHT"]
                elif self.car_pos[0] > self.lanes[self.car_lane] + 3:
                        print("LEFT1")
                        self.frame += 1
                        return ["SPEED", "MOVE_LEFT"]
                elif self.car_pos[0] < self.lanes[self.car_lane] - 3:
                    print("1")
                    self.frame += 1
                    return ["SPEED", "MOVE_RIGHT"]
                else:
                    if len(grid_coin) != 0:
                        # print('------- COIN -------')
                        # dominate by coin position
                        if self.car_lane in grid_coin:
                            self.eat_coin = True
                            self.DESTINATION = self.car_lane
                            self.MOVE_LEFT_TAG = False
                            self.MOVE_RIGHT_TAG = False
                            # print('coin speed (1)')
                            return ['SPEED']

                        if (self.car_lane - 1) >= 0 and (self.car_lane - 1) in grid_coin:
                            self.eat_coin = True
                            self.MOVE_LEFT_TAG  = True
                            self.MOVE_RIGHT_TAG = False
                            self.DESTINATION = self.car_lane - 1
                            # print('coin move left (1)')
                            return ["SPEED", "MOVE_LEFT"]

                        if (self.car_lane + 1) <= 8 and (self.car_lane + 1) in grid_coin:
                            self.eat_coin = True
                            self.MOVE_LEFT_TAG  = False
                            self.MOVE_RIGHT_TAG = True
                            self.DESTINATION = self.car_lane + 1
                            # print('coin move right (1)')

                            self.frame += 1
                            return ["SPEED", "MOVE_RIGHT"]

                    # print('SPEED0')
                    self.frame += 1
                    return ["SPEED"]
            else:
                # print('ELSE')
                if (self.car_lane == 8) \
                    or ((3 in grid) and (6 in grid) and (9 in grid)) \
                    or 6 in grid:
                    # print("ENABLE RIGHT")
                    self.MOVE_RIGHT_TAG = False
                if (self.car_lane == 0) \
                    or ((1 in grid) and (4 in grid) and (7 in grid)) \
                    or 4 in grid:
                    # print("ENABLE LEFT")
                    self.MOVE_LEFT_TAG = False

                # print('---------')
                if (2 not in grid): # Check forward 
                    # prevent from chase coin without noticing
                    # if self.eat_coin:
                    #     if self.MOVE_LEFT_TAG and ((4 in grid or 1 in grid)):
                    #         print('/////// eat coin modify ///////')
                    #         self.DESTINATION = self.car_lane
                    #         self.MOVE_LEFT_TAG = False
                    #         self.eat_coin = False
                    #     elif self.MOVE_RIGHT_TAG or (6 in grid or 3 in grid):
                    #         print('/////// eat coin modify ///////')
                    #         self.DESTINATION = self.car_lane
                    #         self.MOVE_RIGHT_TAG = False
                    #         self.eat_coin = False
                    
                    # Back to lane center
                    if (self.MOVE_LEFT_TAG or self.car_lane > self.DESTINATION):
                        self.frame += 1
                        return ["SPEED", "MOVE_LEFT"]
                    elif (self.MOVE_RIGHT_TAG or self.car_lane < self.DESTINATION):
                        self.frame += 1
                        return ["SPEED", "MOVE_RIGHT"]
                    elif self.car_pos[0] > self.lanes[self.car_lane] + 3:
                        # print("LEFT1")
                        self.frame += 1
                        return ["SPEED", "MOVE_LEFT"]
                    elif self.car_pos[0] < self.lanes[self.car_lane] - 3:
                        # print("1")
                        self.frame += 1
                        return ["SPEED", "MOVE_RIGHT"]
                    else:
                        if self.DESTINATION == self.car_lane:
                            self.MOVE_LEFT_TAG = False
                            self.MOVE_RIGHT_TAG = False
                        # print('SPEED1')

                        if len(grid_coin) != 0:
                            # print('------- COIN -------')
                            # dominate by coin position
                            if self.car_lane in grid_coin:
                                self.eat_coin = True
                                self.DESTINATION = self.car_lane
                                self.MOVE_LEFT_TAG = False
                                self.MOVE_RIGHT_TAG = False
                                # print('coin speed (2)')
                                return ['SPEED']

                            if ((self.car_lane - 1) >= 0 and (self.car_lane - 1) in grid_coin) and (\
                                (1 not in grid and 4 not in grid) or \
                                (4 not in grid and 7 not in grid)):
                                self.eat_coin = True
                                self.MOVE_LEFT_TAG  = True
                                self.MOVE_RIGHT_TAG = False
                                self.DESTINATION = self.car_lane - 1
                                # print('coin move left (2)')
                                return ["SPEED", "MOVE_LEFT"]

                            if ((self.car_lane + 1) <= 8 and (self.car_lane + 1) in grid_coin) and (\
                                (3 not in grid and 6 not in grid) or \
                                (6 not in grid and 9 not in grid)):
                                self.eat_coin = True
                                self.MOVE_LEFT_TAG  = False
                                self.MOVE_RIGHT_TAG = True
                                self.DESTINATION = self.car_lane + 1
                                # print('coin move right (2)')

                                self.frame += 1
                                return ["SPEED", "MOVE_RIGHT"]


                        self.frame += 1
                        return ["SPEED"]
                else:
                    if self.eat_coin :
                        self.DESTINATION = self.car_lane
                        self.MOVE_LEFT_TAG = False
                        self.MOVE_RIGHT_TAG = False
                        self.eat_coin = False
                    if (5 in grid): # NEED to BRAKE
                        # if self.THREAT:
                        #     if self.car_lane == 7:
                        #         self.MOVE_RIGHT_TAG = True
                        #         self.MOVE_LEFT_TAG  = False
                        #         self.DESTINATION    = self.car_lane + 1
                        # self.frame += 1        
                        # return ['BRAKE', 'MOVE_RIGHT']
                        #     elif self.car_lane == 8:
                        #         self.MOVE_RIGHT_TAG = False
                        #         self.MOVE_LEFT_TAG  = False
                        #         self.DESTINATION    = self.car_lane
                        # self.frame += 1        
                        # return ['BRAKE']
                        #     elif self.car_lane == 1:
                        #         self.MOVE_RIGHT_TAG = False
                        #         self.MOVE_LEFT_TAG  = True
                        #         self.DESTINATION    = self.car_lane - 1
                        # self.frame += 1        
                        # return ['BRAKE', 'MOVE_LEFT']
                        #     elif self.car_lane == 8:
                        #         self.MOVE_RIGHT_TAG = False
                        #         self.MOVE_LEFT_TAG  = False
                        #         self.DESTINATION    = self.car_lane
                        # self.frame += 1        
                        # return ['BRAKE']
                        #     else:
                        # self.frame += 1        
                        # return ['SPEED']

                        if self.MOVE_LEFT_TAG:
                            # self.MOVE_LEFT_TAG  = True
                            # self.MOVE_RIGHT_TAG = False
                            self.DESTINATION = self.car_lane - 1
                            # print('TAG_LEFT')
                            if self.car_vel < speed_ahead:
                                self.frame += 1
                                return ["SPEED", "MOVE_LEFT"]
                            else:
                                self.frame += 1
                                return ["BRAKE", "MOVE_LEFT"]
                        elif self.MOVE_RIGHT_TAG:
                            # self.MOVE_LEFT_TAG  = False
                            # self.MOVE_RIGHT_TAG = True
                            self.DESTINATION = self.car_lane + 1
                            # print('TAG_RIGHT')
                            if self.car_vel < speed_ahead:
                                self.frame += 1
                                return ["SPEED", "MOVE_RIGHT"]
                            else:
                                self.frame += 1
                                return ["BRAKE", "MOVE_RIGHT"]
                        # elif (4 not in grid) and (7 not in grid) and (6 not in grid) and (9 not in grid):
                        #     # dominate by coin position
                        #     if (self.car_lane + 1) <= 8 and (self.car_lane + 1) in grid_coin:
                        #         self.MOVE_LEFT_TAG  = False
                        #         self.MOVE_RIGHT_TAG = True
                        #         self.DESTINATION = self.car_lane + 1
                        #         print("2")

                        #         # self.frame += 1
                        #         # return ["MOVE_RIGHT"]
                        #         if self.car_vel < speed_ahead:
                        #             self.frame += 1
                        #             return ["SPEED", "MOVE_RIGHT"]
                        #         else:
                        #             self.frame += 1
                        #             return ["BRAKE", "MOVE_RIGHT"]
                        #     elif (self.car_lane - 1) >= 0 and (self.car_lane - 1) in grid_coin:
                        #         self.MOVE_LEFT_TAG  = True
                        #         self.MOVE_RIGHT_TAG = False
                        #         self.DESTINATION = self.car_lane - 1
                        #         print("LEFT2")
                        #         if self.car_vel < speed_ahead:
                        #             self.frame += 1
                        #             return ["SPEED", "MOVE_LEFT"]
                        #         else:
                        #             self.frame += 1
                        #             return ["BRAKE", "MOVE_LEFT"]

                        
                        elif (4 not in grid) and (7 not in grid): # turn left 
                            self.MOVE_LEFT_TAG  = True
                            self.MOVE_RIGHT_TAG = False
                            self.DESTINATION = self.car_lane - 1
                            # print("LEFT2")
                            if self.car_vel < speed_ahead:
                                self.frame += 1
                                return ["SPEED", "MOVE_LEFT"]
                            else:
                                self.frame += 1
                                return ["BRAKE", "MOVE_LEFT"]
                        elif (6 not in grid) and (9 not in grid): # turn right
                            self.MOVE_LEFT_TAG  = False
                            self.MOVE_RIGHT_TAG = True
                            self.DESTINATION = self.car_lane + 1
                            # print("2")

                            # self.frame += 1
                            # return ["MOVE_RIGHT"]
                            if self.car_vel < speed_ahead:
                                self.frame += 1
                                return ["SPEED", "MOVE_RIGHT"]
                            else:
                                self.frame += 1
                                return ["BRAKE", "MOVE_RIGHT"]
                        else :
                            self.MOVE_LEFT_TAG  = False
                            self.MOVE_RIGHT_TAG = False
                            self.DESTINATION = self.car_lane
                            # print("BRAKE")
                            if self.car_vel < speed_ahead:  # BRAKE
                                # print('SPEED2')
                                self.frame += 1
                                return ["SPEED"]
                            else:
                                # print("BRAKE2")
                                self.frame += 1
                                return ["BRAKE"]

                    if (self.car_pos[0] > 600) or self.MOVE_LEFT_TAG:
                        self.MOVE_LEFT_TAG  = True
                        self.MOVE_RIGHT_TAG = False
                        self.DESTINATION = self.car_lane - 1
                        # print("LEFT3")
                        self.frame += 1
                        return ["SPEED", "MOVE_LEFT"]
                    elif (self.car_pos[0] < 60) or self.MOVE_RIGHT_TAG:
                        self.MOVE_LEFT_TAG  = False
                        self.MOVE_RIGHT_TAG = True
                        self.DESTINATION = self.car_lane + 1
                        # print("3")
                        self.frame += 1
                        return ["SPEED", "MOVE_RIGHT"]

                    elif ((1 not in grid) and (4 not in grid) and (7 not in grid)) or self.MOVE_LEFT_TAG: # turn left 
                        self.MOVE_LEFT_TAG  = True
                        self.MOVE_RIGHT_TAG = False
                        self.DESTINATION = self.car_lane - 1
                        # print("LEFT4")
                        self.frame += 1
                        return ["SPEED", "MOVE_LEFT"]
                    elif ((3 not in grid) and (6 not in grid) and (9 not in grid)) or self.MOVE_RIGHT_TAG: # turn right
                        self.MOVE_LEFT_TAG  = False
                        self.MOVE_RIGHT_TAG = True
                        self.DESTINATION = self.car_lane + 1
                        # print("4")
                        self.frame += 1
                        return ["SPEED", "MOVE_RIGHT"]

                    elif ((1 not in grid) and (4 not in grid)) or self.MOVE_LEFT_TAG: # turn left 
                        self.MOVE_LEFT_TAG  = True
                        self.MOVE_RIGHT_TAG = False
                        self.DESTINATION = self.car_lane - 1
                        # print("LEFT5")
                        self.frame += 1
                        return ["SPEED", "MOVE_LEFT"]
                    elif ((4 not in grid) and (7 not in grid)) or self.MOVE_LEFT_TAG: # turn left 
                        self.MOVE_LEFT_TAG  = True
                        self.MOVE_RIGHT_TAG = False
                        self.DESTINATION = self.car_lane - 1
                        # print("LEFT6")
                        self.frame += 1
                        return ["MOVE_LEFT"]    
                    
                    elif ((3 not in grid) and (6 not in grid)) or self.MOVE_RIGHT_TAG: # turn right
                        self.MOVE_LEFT_TAG  = False
                        self.MOVE_RIGHT_TAG = True
                        self.DESTINATION = self.car_lane + 1
                        # print("5")
                        self.frame += 1
                        return ["SPEED", "MOVE_RIGHT"]
                    elif ((6 not in grid) and (9 not in grid)) or self.MOVE_RIGHT_TAG: # turn right
                        self.MOVE_LEFT_TAG  = False
                        self.MOVE_RIGHT_TAG = True
                        self.DESTINATION = self.car_lane + 1
                        # print("6")
                        self.frame += 1
                        return ["MOVE_RIGHT"]
            
            
                    
        if len(scene_info[self.player]) != 0:
            self.car_pos = scene_info[self.player]

        for car in scene_info["cars_info"]:
            if car["id"]==self.player_no:
                self.car_vel = car["velocity"]

        if scene_info["status"] != "ALIVE":
            return "RESET"

        self.car_lane = self.car_pos[0] // 70
        # print((self.car_pos[0] > self.lanes[0] + 2), not self.isInit)
        # if (self.car_pos[0] < self.lanes[8] - 2) and not self.isInit:
        #     print("||||||||||||||||||||||||")
        #     return ["SPEED", "MOVE_RIGHT"]
        # if self.car_lane == 8 and self.car_pos != (0,0):
        #     self.isInit = True

        return check_grid()

    def reset(self):
        """
        Reset the status
        """
        pass