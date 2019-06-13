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
        self.surveillance = False
        self.surveil_counter = 0
        self.start = 1
        self.just_fired = False
        self.gap_found = 0
        
    def update(self,scan_distaces,previous_distance):
        self.scan_distaces = scan_distaces
        #if self.explore is False:
        self.previous_distance = previous_distance
        # else:
        #     self.wait_count = 1
        print('Scan distances:')
        print('          {} ({})'.format(self.scan_distaces[self.directions['Front']],self.previous_distance[self.directions['Front']]))
        print('{}({})       o             {}({})'.format(self.scan_distaces[self.directions['Left']],self.previous_distance[self.directions['Left']],self.scan_distaces[self.directions['Right']],self.previous_distance[self.directions['Right']]))
        print('          {}({})'.format(self.scan_distaces[self.directions['Back']],self.previous_distance[self.directions['Back']]))
        
        #print('Previous distance',self.previous_distance)
        
    def ActionFire(self):
        if api.identify_target() is True: 
            self.final_action = self.actions['Fire']
            self.just_explored = False
            print('Target identified --- Fire')
            self.just_fired = True
            return 1
        else:
            if self.just_fired is True: 
                print('On Alert..Just fired.')
                min_val = 30
                min_direction = -1
                for direction,value in enumerate(self.scan_distaces):
                    if value < min_val and direction != 0:
                        min_val = value
                        min_direction = direction
                print(min_direction)
                if min_direction == -1:
                    self.just_fired = False
                    return 0 
                
                if min_direction == 1:
                    self.final_action = self.actions['Left']
                elif min_direction == 2: 
                    self.final_action = self.actions['LookBack']
                elif min_direction == 3:
                    self.final_action = self.actions['Right']
                self.just_fired = False
                return 1
        return 0
    
    def ActionLeft(self):
        if self.scan_distaces[self.directions['Front']] <= 1:
            if self.scan_distaces[self.directions['Left']] - self.scan_distaces[self.directions['Right']] > 0:
                self.final_action = self.actions['Left']
                self.just_explored = True
                print('Action Left: left > right, front <= 1; Turn Left')
                return 1
            else:
                return 0
        else:
            return 0
            
    def ActionRight(self):
        if self.scan_distaces[self.directions['Front']] <= 1:
            if self.scan_distaces[self.directions['Left']] - self.scan_distaces[self.directions['Right']] < 0:
                self.final_action = self.actions['Right']
                self.just_explored = True
                print('Action Right: left < right, front <= 1; Turn Right')
                return 1
            else:
                return 0
        else:
            return 0
                
    def ActionForwards(self):
        if self.scan_distaces[self.directions['Front']] > 1:
            self.final_action = self.actions['Forward']
            self.just_explored = False
            print('Action Forward: Front > 1; Go Forwards')
            return 1 
        else:
            return 0
            
    def ActionBackwards(self):
        self.final_action = self.actions['Back']
        self.just_explored = False
        print('Action Backwards: Go Backward')
    
    def ActionExplore(self):
        if self.just_explored is True: 
            print('Action Explore: just explored...so skipping')
            return  0
        
        if self.surveillance is True: 
            print('Action Explore: Surveillance....')
            hreturn = 0
            if self.scan_distaces[self.directions['Front']]> 8:
                self.final_action = self.actions['Forward']
                print('Action Explore: Go Straight')
                self.surveil_counter += 1 
                return 1
            else: 
                difference = [self.previous_distance[self.directions['Left']] - self.scan_distaces[self.directions['Left']], self.previous_distance[self.directions['Right']] - self.scan_distaces[self.directions['Right']]]
                min_val = 100
                min_direction = -1
                
                print('Distance change [Left, Right] : ', difference)
                for direction,value in enumerate(difference):
                    if value != 0 and value < min_val:
                        min_val = value
                        min_direction = direction
                print('Minimum direction : ',min_direction)
                if min_direction == 0:
                    self.final_action = self.actions['Left']
                    print('Action Explore: Turn Left')
                    self.surveil_counter += 1 
                    return 1
                elif min_direction == 1:
                    self.final_action = self.actions['Right']
                    print('Action Explore: Turn Right')
                    self.surveil_counter += 1 
                    return 1
                else: 
                    self.surveil_counter = 0
                    self.surveillance = False
                    print('Ending surveillance')
            
            if self.surveil_counter> 3: 
                self.surveil_counter = 0
                self.surveillance = False
                print('Ending surveillance')
            
            self.surveil_counter += 1 
            
        
        if self.previous_distance is not None: 
            print('Check Threat :',self.check_threat)
            if self.check_threat is False:
                difference = [previous_distance - scan_distaces for previous_distance,scan_distaces in zip(self.previous_distance,self.scan_distaces)]
                
                diff_sides = []
                diff_back = -1
                for i in range(len(difference)):
                    if i%2 != 0:
                        diff_sides.append(difference[i])
                    if i==2:
                        diff_back = difference[i]
                        
                print('Distance change [Left, Right]',diff_sides)
                
                min_direction = -1
                max_value = 30
                for i,side in enumerate(diff_sides):
                    if side<max_value and side != 0:
                        min_direction = i
                        #max_value = side
                print('Minimum direction ',min_direction)
                self.gap_found = max([abs(side) for side in diff_sides])
                print('Gap found = ',self.gap_found)
                if min_direction != -1:
                    #if diff_sides[min_direction] > -3 and diff_sides[min_direction] != 0: #or diff_sides[min_direction] > -2: # a shortening of distance has took place or # a slight enlargement has happened...found a corridor?
                    if diff_sides[min_direction] != 0:
                        
                        if min_direction == 0:
                            self.final_action = self.actions['Left']
                            print('Action Explore : Turn Left')
                            self.previous_explore_turn = self.final_action
                            self.check_threat = True
                            if self.scan_distaces[self.directions['Front']]<3:
                                self.check_threat = False
                                self.just_explored = True
                            
                            self.check_threat_distance = self.scan_distaces[self.directions['Left']]
                            print('Updated check threat is {} with check threat distance = {}'.format(self.check_threat,self.check_threat_distance))
                            if self.gap_found > 8:
                                # go to surveillance mode
                                self.surveillance = True
                                self.just_explored = False
                            self.gap_found = 0
                            return 1
                        else:
                            # if self.check_threat is False:
                            self.final_action = self.actions['Right']
                            self.previous_explore_turn = self.final_action
                            self.check_threat = True
                            if self.scan_distaces[self.directions['Front']]<3:
                                self.check_threat = False
                                self.just_explored = True
                            self.check_threat_distance = self.scan_distaces[self.directions['Right']]
                            print('Updated check threat :',self.check_threat)
                            print('Updated check threat is {} with check threat distance = {}'.format(self.check_threat,self.check_threat_distance))
                            print('Action Explore : Turn Right')
                            if self.gap_found > 8:
                                # go to surveillance mode
                                self.surveillance = True
                                self.just_explored = False
                            self.gap_found = 0
                            return 1
                print('Difference Back ',diff_back)  
                if diff_back == 0: # back side distance has not changed... this means an enemy is following
                    print('Persuming Followed...')
                    self.final_action = self.actions['LookBack']
                    self.previous_explore_turn = self.final_action
                    self.check_threat_distance = self.scan_distaces[self.directions['Back']]
                    self.check_threat = True
                    print('Action Explore: Turn Back')
                    return 1
                
                return 0
                
            else:
                print('Check threat distance is {} and front distance is {}'.format(self.check_threat_distance,self.scan_distaces[self.directions['Front']]))
                if self.check_threat_distance != self.scan_distaces[self.directions['Front']]:
                    self.final_action = self.actions['Forward']
                    self.check_threat = False
                    self.surveillance = True
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
                    self.final_action = self.actions['Left']
                    print('exp check threat:turn left')    
                    self.just_explored = True
                    return 1
            #print('Explore : ',0)
            return 0
    
    
    def Coordinate(self):
        print('Coordination....')
        print('Fuel : ', api.current_fuel())
        self.final_action = self.actions['Forward']
        if self.start == 1:
            print('Start motion')
            self.start = 0
            return
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


                        
        
        
        