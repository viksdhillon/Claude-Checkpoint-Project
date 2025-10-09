import datetime

class Node:
    def __init__(self, node_id, query, response):
        self.id = node_id
        self.query = query
        self.response = response
        self.next = None
        self.prev = None
    
class CheckpointADT:
    def __init__(self):
        self.head = None
        self.tail = None
        self.map = {}
        self.checkpoints = {}
    
    def append(self, node_id, query, response):
        new_node = Node(node_id, query, response)
        if self.head == None:
            self.head = new_node
            self.tail = self.head
            self.tail.next = None
        else:
            self.tail.next = new_node
            self.tail.next.prev = self.tail
            self.tail = self.tail.next
            self.tail.next = None
        
        #update map with new node
        self.map[node_id] = new_node

    def delete_node_by_id(self, id):
        # pop from map
        removed_node = self.map.pop(id, None)
        if removed_node is None:
            return False
        # delete node from linked list

        if removed_node == self.head and removed_node == self.tail:
            self.head = None
            self.tail = None
        elif (removed_node == self.head):
             self.head = removed_node.next
             if self.head:
                 self.head.prev = None
        elif (removed_node == self.tail):
             self.tail = removed_node.prev
             if self.tail:
                 self.tail.next = None
        else:
            removed_node.prev.next = removed_node.next
            removed_node.next.prev = removed_node.prev
        return True
    
    # get node
    def find(self, id):
       return self.map.get(id)
    
    #get node contents
    def get(self, id):
        node = self.find(id)
        if not node:
            return None
        else:
            return (node.query, node.response)
    
    #update query and response of a node 
    def update(self, id, query, response):
        node = self.find(id)
        if not node:
            return False
        
        node.query = query
        node.response = response
        return True

     # iterate through list head to tail
    def traverse_forward(self):
        current = self.head
        while current:
            yield current
            current = current.next

    # iterate through list tail to head

    def traverse_backward(self):
        current = self.tail
        while current:
            yield current
            current = current.prev  

    # add a checkpoint into the map with metadata
    def checkpoint(self, label, description):
        if self.tail is None:
            return False
        self.checkpoints[label] = {
            "node_id": self.tail.id,
            "description": description,
            "timestamp": datetime.datetime.now()
        }
        return True
    
    # rollback to certain id
    def rollback_to(self, id):
        node = self.tail
        while node and node.id != id:
            prev = node.prev
            self.delete_node_by_id(node.id)
            node = prev
        
        if node is None:
            self.head = None
            self.tail = None
            return False
        
        self.tail = node
        self.tail.next = None
        return True
    
    # rollback to last node
    def rollback_last(self):
        if self.tail != None:
            self.delete_node_by_id(self.tail.id)
            return True
        return False
    
    #creates a new list up to and including the id provided which can be used to anaylze new paths
    def branch_from(self, id):
        new_list = CheckpointADT()
        node = self.head
        while node and node.id <= id:
            new_list.append(node.id, node.query, node.response)
            node = node.next
        return new_list
    

    


        





    

        

        
        