import api
class Actions:
    def __init__(self,scan_distances,directions,actions):
        self.scan_distances = scan_distances
        self.directions = directions
        self.previous_distance = None
        self.actions = actions 
        self.final_action = 0
        self.just_explored = False
        self.wait_count = 0
        self.previous_explore_turn = self.actions['Forward']
        self.check_threat = False
        self.check_threat_distance = -1
        
    def update(self,scan_distaces,previous_distance):
        self.scan_distaces = scan_distaces
        #if self.explore is False:
        self.previous_distance = previous_distance
        # else:
        #     self.wait_count = 1
        print('Scan distance',self.scan_distaces)
        print('Previous distance',self.previous_distance)
        
    def ActionFire(self):
        if api.identify_target() is True: 
            self.final_action = self.actions['Fire']
            self.just_explored = False
            print('Fire')
            return 1
        else:
            print('Fire : ',0)
            return 0
    
    def ActionLeft(self):
        if self.scan_distaces[self.directions['Front']] <= 1:
            if self.scan_distaces[self.directions['Left']] - self.scan_distaces[self.directions['Right']] > 0:
                self.final_action = self.actions['Left']
                self.just_explored = True
                print('Turn Left')
                return 1
            else:
                print('Left : ',0)
                return 0
        else:
            print('Left : ',0)
            return 0
            
    def ActionRight(self):
        if self.scan_distaces[self.directions['Front']] <= 1:
            if self.scan_distaces[self.directions['Left']] - self.scan_distaces[self.directions['Right']] < 0:
                self.final_action = self.actions['Right']
                self.just_explored = True
                print('Turn Right')
                return 1
            else:
                print('Right : ',0)
                return 0
        else:
            print('Right : ',0)
            return 0
                
    def ActionForwards(self):
        if self.scan_distaces[self.directions['Front']] > 1:
            print(self.scan_distaces)
            self.final_action = self.actions['Forward']
            self.just_explored = False
            print('Go Forward')
            return 1 
        else:
            print('Forward : ',0)
            return 0
            
    def ActionBackwards(self):
        self.final_action = self.actions['Back']
        self.just_explored = False
        print('Go Backward')
    
    def ActionExplore(self):
        if self.just_explored is True: 
            print('just explored...so skipping')
            return  0

        if self.previous_distance is not None: 
            if self.check_threat is False:    
                difference = [previous_distance - scan_distaces for previous_distance,scan_distaces in zip(self.previous_distance,self.scan_distaces)]
                diff_sides = []
                diff_back = -1
                for i in range(len(difference)):
                    if i%2 != 0:
                        diff_sides.append(difference[i])
                    if i==2:
                        diff_back = difference[i]
                        
                print(diff_sides)
                min_direction = 0
                max_value = 30
                for i,side in enumerate(diff_sides):
                    if side<max_value and side > 0:
                        min_direction = i
                print('min direction ',min_direction) 
                print('diff_sides[min_direction] = ',diff_sides[min_direction])
                if diff_sides[min_direction] > -2 and diff_sides[min_direction] != 0: #or diff_sides[min_direction] > -2: # a shortening of distance has took place or # a slight enlargement has happened...found a corridor?
                    if min_direction == 0:
                        self.final_action = self.actions['Left']
                        print('exp:turn left')
                        self.previous_explore_turn = self.final_action
                        self.check_threat = True
                        self.check_threat_distance = self.scan_distaces[self.directions['Left']]
                        return 1
                    else:
                        # if self.check_threat is False:
                        self.final_action = self.actions['Right']
                        self.previous_explore_turn = self.final_action
                        self.check_threat = True
                        self.check_threat_distance = self.scan_distaces[self.directions['Right']]
                        print('exp:turn right')
                        return 1
                        
                if diff_back == 0: # back side distance has not changed... this means an enemy is following
                    self.final_action = self.actions['LookBack']
                    self.previous_explore_turn = self.final_action
                    self.check_threat_distance = self.scan_distaces[self.directions['Back']]
                    self.check_threat = True
                    print('exp: turn back')
                    return 1
            else:
                print('Threat check = ',self.check_threat)
                if self.check_threat_distance != self.scan_distaces[self.directions['Front']]:
                    self.final_action = self.actions['Forward']
                    self.check_threat = False
                    return 1
                if self.previous_explore_turn == self.actions['LookBack']:
                    self.final_action = self.actions['LookBack']
                    print('exp check threat:look back')    
                    self.check_threat = False
                    return 1
                if self.previous_explore_turn == self.actions['Left']:
                    self.check_threat = False
                    self.final_action = self.actions['Right']
                    print('exp check threat:turn right')    
                    self.just_explored = True
                    return 1
                elif self.previous_explore_turn == self.actions['Right']:
                    self.check_threat = False
                    self.final_action = self.actions['Right']
                    print('exp check threat:turn right')    
                    self.just_explored = True
                    return 1
            print('Explore : ',0)
            return 0
    
    
    def Coordinate(self):
        print('Coordination....')
        self.final_action = self.actions['Forward']
        hreturn = self.ActionFire()
        if hreturn == 0: # nothing happened
            hreturn = self.ActionExplore()
            if hreturn == 0: # nothing happened
                if self.just_explored is False:
                    hreturn =  self.ActionLeft()
            if hreturn == 0: # nothing happened
                if self.just_explored is False:
                    hreturn =  self.ActionRight()
            if hreturn == 0: #nothing happened
                hreturn = self.ActionForwards()
            if hreturn == 0: #nothing happened
                self.ActionBackwards()
                    
                           
class Solution:
    def __init__(self):
        # If you need initialization code, you can write it here!
        # Do not remove.
        self.directions = {'Front':0,'Left':1,'Back':2,'Right':3}
        self.opt_action = {'Forward':0,'Left':1,'Back':2,'Right':3,'Fire':4,'LookBack':5}
        self.scan_distances= [-1,-1,-1,-1]
        self.previous_distances = None
        self.actions = Actions(self.scan_distances,self.directions,self.opt_action)

    def update(self):
        """
        Executes a single step of the tank's programming. The tank can only 
        move, turn, or fire its cannon once per turn. Between each update, the 
        tank's engine remains running and consumes 1 fuel. This function will be 
        called repeatedly until there are no more targets left on the grid, or 
        the tank runs out of fuel.
        """
        # Todo: Write your code here!
        # scan the lidars
        # set previous distance to current distance
        self.scan()
        if self.previous_distances is None: 
            self.previous_distances = self.scan_distances[:]
        
        self.actions.update(self.scan_distances,self.previous_distances)
        self.actions.Coordinate()
        
        self.execute()
        self.previous_distances = self.scan_distances[:]
        
    def execute(self):
        if self.actions.final_action == self.opt_action['Forward']:
            api.move_forward()
        elif self.actions.final_action == self.opt_action['Left']:
            api.turn_left()
        elif self.actions.final_action == self.opt_action['Right']:    
            api.turn_right()
        elif self.actions.final_action == self.opt_action['Back']:    
            api.move_backward()
        elif self.actions.final_action == self.opt_action['Fire']:    
            api.fire_cannon()
        elif self.actions.final_action == self.opt_action['LookBack']:
            api.turn_left()
        
    def scan(self):
        self.scan_distances[self.directions['Front']] = api.lidar_front()
        self.scan_distances[self.directions['Left']] = api.lidar_left()
        self.scan_distances[self.directions['Back']] = api.lidar_back()
        self.scan_distances[self.directions['Right']] = api.lidar_right()
        print('*******************************************************')


                        
        
        
        