#!/usr/bin/env python3
import math
import copy

class State:
    stateName: str  # the string for this state name

    def __init__(self, stateName="State"):
        """
        Initialize a State object.
        """
        self.stateName = stateName

    def printState(self):
        """
        Print the state name.
        """
        print("State: " + self.stateName)

class Unassigned(State):
    def __init__(self, stateName="Unassigned"):
        """
        Initialize an Unassigned State object.
        """
        State.__init__(self, stateName=stateName)

class Assigned(State):
    def __init__(self, stateName="Assigned"):
        """
        Initialize an Assigned State object.
        """
        State.__init__(self, stateName=stateName)

class Completed(State):
    def __init__(self, stateName="Completed"):
        """
        Initialize a Completed State object.
        """
        State.__init__(self, stateName=stateName)

class Homing(State):
    def __init__(self, stateName="Homing"):
        """
        Initialize a Homing State object.
        """
        State.__init__(self, stateName=stateName)

class End(State):
    def __init__(self, stateName="End"):
        """
        Initialize an End State object.
        """
        State.__init__(self, stateName=stateName)

class AgentFSMExp:
    agentIdx: int  # the index for this agent
    distanceThreshold: float  # when distance between A and B < this number, we say A and B have same position
    StatesPool: dict  # a dictionary for all included State objects
    numTargetTotal: int  # the number of targets in total
    targetIdxNow: int  # the target index that is currently assigned to the agent
    """
    targetSetTotal: 2D list, a set of targets positions (in Qualisys coordinates) in total, [[x0,y0,z0], [x1,y1,z1], [x2,y2,z2], ...]
    The execution order is target 0 -> target 1 -> target 2 -> ...
    """
    targetSetTotal: list
    targetSetToDo: list  # a 2D list for a set of targets positions (in Qualisys coordinates) to do
    """
    targetSetOrder: a 1D list for the execution order of targets
    Example: targetSetOrder = [0, 3, 1, 2] means the T0 -> T3 -> T1 -> T2
    """
    targetSetOrder: list

    def __init__(self, agentIdx=0, distanceThreshold=0.1):
        """
        Initialize a Agent Finite State Machine object.

        Input:
            agentIdx: int, an integer for the agent index
            distanceThreshold: float, when distance between A and B < distanceThreshold, we say A and B have same position
        """
        self.agentIdx = agentIdx
        self.distanceThreshold = distanceThreshold
        self.StatesPool = {"Unassigned": Unassigned(),
                           "Assigned": Assigned(),
                           "Completed": Completed(),
                           "Homing": Homing(),
                           "End": End()}
        self.StateNow = self.StatesPool["Unassigned"]
    
    def initFSM(self, targetSetTotal: list, targetSetOrder=None):
        """
        Initialize the Agent Finite State Machine by a set of targets positions that need to be done.

        Input:
            targetSetTotal: 2D list, a set of targets positions (in Qualisys coordinates) that need to be done,
                [[x0,y0,z0], [x1,y1,z1], [x2,y2,z2], ...]. The execution order is target 0 -> target 1 -> target 2 -> ...
            targetSetOrder: 1D list, the execution order of targets. If empty, [0, 1, 2, 3, ...]
                Example: targetSetOrder = [0, 3, 1, 2] means the T0 -> T3 -> T1 -> T2
        """
        self.StateNow = self.StatesPool["Unassigned"]
        self.targetSetTotal = copy.deepcopy(targetSetTotal)
        self.targetSetToDo = copy.deepcopy(targetSetTotal)
        self.targetSetOrder = copy.deepcopy(targetSetOrder)
        self.numTargetTotal = len(targetSetTotal)
        self.targetIdxNow = -1

    def transition(self, agentPositionNow: list, targetSetTotal: list, homePosition: list, targetSetOrder=None):
        """
        Make state transition based on the current agent position and target set.
        NOTE: this function ignores the distance in height axis.

        Input:
            agentPositionNow: 1D list, current agent position (in Qualisys coordinates), [x0,y0,z0]
            targetSetTotal: 2D list, a set of targets positions (in Qualisys coordinates) in total,
                [[x0,y0,z0], [x1,y1,z1], [x2,y2,z2], ...]. The execution order is target 0 -> target 1 -> target 2 -> ...
            homePosition: 1D list, home position (in Qualisys coordinates), [x0,y0,z0]
            targetSetOrder: 1D list, the execution order of targets. If empty, [0, 1, 2, 3, ...]
                Example: targetSetOrder = [0, 3, 1, 2] means the T0 -> T3 -> T1 -> T2

        Output:
            stateName: str, the state name after the transition
            targetSetToDoOutput: a 2D list, a set of targets positions to do, [[x0,y0,z0], [x1,y1,z1], [x2,y2,z2], ...]
        """
        # when the state is "Homing", do nothing here.
        # otherwise, check whether targetSetTotal is equal to the previous one (i.e., self.targetSetTotal)
        # if not equal, initialize FSM
        if self.StateNow.stateName != "Homing":
            if targetSetTotal != self.targetSetTotal:
                print("Target set or task allocation changed, initialized FSM.")
                self.initFSM(targetSetTotal, targetSetOrder)
            else:
                # when targets are the same, but the execution order changed, update targetSetOrder
                if targetSetOrder != self.targetSetOrder:
                    self.targetSetOrder = copy.deepcopy(targetSetOrder)

        # compute the distance between the current agent position and current target position
        if self.targetIdxNow > -1:
            if targetSetOrder:
                # if targetSetOrder is not empty, follow the exact order
                targetIdx = self.targetSetOrder[self.targetIdxNow]
                targetPositionNow = self.targetSetTotal[targetIdx]
            else:
                # if targetSetOrder is empty, [0, 1, 2, 3, ...]
                targetPositionNow = self.targetSetTotal[self.targetIdxNow]

            distance = math.sqrt((agentPositionNow[0]-targetPositionNow[0])**2 + (agentPositionNow[1]-targetPositionNow[1])**2)
        else:
            # initialize the distance as a large number at the beginning
            distance = 1E9

        # states transitions
        if self.StateNow.stateName == "Unassigned":
            if self.targetIdxNow < self.numTargetTotal - 1:
                self.targetIdxNow += 1
                stateName = "Assigned"
            else:
                stateName = "Homing"
        elif self.StateNow.stateName == "End":
            # if State == End, keep it
            stateName = self.StateNow.stateName
        elif self.StateNow.stateName == "Assigned":
            if distance > self.distanceThreshold:
                stateName = self.StateNow.stateName
                # don't change the assigned target index
            else:
                stateName = "Completed"
        elif self.StateNow.stateName == "Completed":
            # if completed, delete this target from to-do list
            if self.targetSetToDo:
                if targetSetOrder:
                    # if targetSetOrder is not empty, deleted the completed task by order
                    targetIdx = self.targetSetOrder[self.targetIdxNow]
                    del self.targetSetToDo[targetIdx]
                else:
                    # if targetSetOrder is empty, deleted the completed task by default order
                    del self.targetSetToDo[0]
            # if completed and the to-do list is empty, do nothing
            stateName = "Unassigned"
        elif self.StateNow.stateName == "Homing":
            # if the arrives at home, change to "End"
            # otherwise, keep it "Homing"
            distance = math.sqrt((agentPositionNow[0]-homePosition[0])**2 + (agentPositionNow[1]-homePosition[1])**2)
            if distance > self.distanceThreshold:
                stateName = self.StateNow.stateName
            else:
                stateName = "End"
        else:
            Exception("AgentFSM only supports 5 states: Unassigned, Assigned, Completed, Homing, End!")

        # update the state
        self.StateNow = self.StatesPool[stateName]

        if self.StateNow.stateName == "Homing":
            targetSetToDoOutput = [homePosition]
        else:
            targetSetToDoOutput = copy.deepcopy(self.targetSetToDo)

        return stateName, targetSetToDoOutput
