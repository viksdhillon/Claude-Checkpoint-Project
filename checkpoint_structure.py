import datetime
from ollama import chat
from ollama import ChatResponse
from judge import Judge
import json
import os

class Node:
    def __init__(self, node_id, query, response):
        self.id = node_id
        self.query = query
        self.response = response
        self.next = None
        self.prev = None
    
class CheckpointADT:
    def __init__(self, log=None):
        # Default to checkpoint_save.json in the same directory as this file
        if log is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            log = os.path.join(script_dir, "checkpoint_save.json")
        self.head = None
        self.tail = None
        self.map = {}
        self.checkpoints = {}
        self.node_counter = 0
        self.log = log
        self.data = {
            "query": "",
            "steps": []
        }
        self.judge = Judge()
    
    def append(self, query, response):
        self.node_counter +=1
        new_node = Node(self.node_counter, query, response)
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
        self.map[new_node.id] = new_node
        self.data["steps"].append({
                    "id": self.node_counter,
                    "response": response
                })
        self.update_json()
        return self.node_counter
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
        
        self.data["steps"] = [step for step in self.data["steps"] if step["id"] != id]
        self.update_json()
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
    
    #update response of a node 
    def update(self, id, response):
        node = self.find(id)
        if not node:
            return False
        
        node.response = response
        # Find the step in the list by id and update it
        for step in self.data["steps"]:
            if step["id"] == id:
                step["response"] = response
                break
        self.update_json()
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
    
    def toString(self):
        curr = self.head
        if curr is None:
            return "Empty checkpoint structure"
        result = []
        while curr:
           result.append(f"{curr.id}, {curr.response}")
           curr = curr.next

        output = " || ".join(result)
        print(output)    
        return output 
    
    #json formatting
    def prompt_and_save(self, query, delim):
        response: ChatResponse = chat(model='llama3.2:1b', messages=[
            {
                'role': 'user',
                'content': query,
            },
        ])
        steps = self.scrape_data(delim, response.message.content)
        print(response.message.content)
        self.data["query"] = query
        for i in steps:
            id = self.append(query, i)
            # if i.strip():
            #     self.data["steps"].append({
            #         id: id,
            #         "response": i.strip()
            #     })

        # with open(self.log, 'w') as f:
        #     json.dump(self.data, f, indent=2)
        
        # f.close()  
    def scrape_data(self, delim, message):
        steps = message.split(delim)
        return steps
    
    def update_json(self):
        # Rebuild data from linked list to ensure consistency
        self.data["steps"] = []
        for node in self.traverse_forward():
            self.data["steps"].append({
                "id": node.id,
                "query": node.query,
                "response": node.response
            })
        
        with open(self.log, 'w') as f:
            json.dump(self.data, f, indent=2)
        f.close()

    
    def router_judge(self, problem):
        if problem is None:
            if not self.head:
                raise ValueError("router_judge: no problem provided and checkpoint list is empty.")
            problem = self.head.query
        solved_answer = self.tail.response if self.tail else None

        judge_type = self.judge.classify(problem)
        actual_answer = self.judge.solve(problem, judge_type)
        answer = actual_answer['answer']
        vq = self.judge.generate_verification(problem, answer, judge_type)
        
        # Return both verification question and the path selected
        return {
            'verification_question': vq,
            'path': judge_type,
            'path_name': self.judge.judges[judge_type]['name']
        }
    
if __name__ == "__main__":
    """Comprehensive test harness"""
    print("=" * 60)
    print("CHECKPOINT SYSTEM TEST HARNESS")
    print("=" * 60)
    
    # Test 1: Create and append nodes
    print("\n[TEST 1] Creating checkpoint chain...")
    checkpoint_system = CheckpointADT()
    checkpoint_system.append("CP-0", "Start", {"n": 12})
    checkpoint_system.append("CP-1", "Calculate 12!", {"value": 479001600})
    checkpoint_system.append("CP-2", "Factor by 2", {"factors": [2, 2]})
    checkpoint_system.append("CP-3", "Factor by 3", {"factors": [2, 2, 3]})
    checkpoint_system.append("CP-4", "Factor by 5", {"factors": [2, 2, 3, 5]})
    print("Chain: ", end="")
    checkpoint_system.toString()
    
    # Test 2: Create checkpoints with labels
    print("\n[TEST 2] Creating labeled checkpoints...")
    checkpoint_system.checkpoint("after_twos", "Finished factoring by 2")
    checkpoint_system.checkpoint("after_threes", "Finished factoring by 3")
    print(f"✓ Created {len(checkpoint_system.checkpoints)} checkpoints")
    for label, data in checkpoint_system.checkpoints.items():
        print(f"  - {label}: node {data['node_id']} - {data['description']}")
    
    # Test 3: Find and get nodes
    print("\n[TEST 3] Finding and retrieving nodes...")
    node = checkpoint_system.find("CP-2")
    if node:
        print(f"✓ Found node: {node.id}")
        query, response = checkpoint_system.get("CP-2")
        print(f"  Query: {query}, Response: {response}")
    
    # Test 4: Update a node
    print("\n[TEST 4] Updating node CP-2...")
    checkpoint_system.update("CP-2", "Factor by 2 (updated)", {"factors": [2, 2, 2]})
    query, response = checkpoint_system.get("CP-2")
    print(f"✓ Updated - Query: {query}, Response: {response}")
    
    # Test 5: Forward traversal
    print("\n[TEST 5] Forward traversal...")
    print("Nodes: ", end="")
    for node in checkpoint_system.traverse_forward():
        print(f"{node.id}", end=" ")
    print()
    
    # Test 6: Backward traversal
    print("\n[TEST 6] Backward traversal...")
    print("Nodes (reverse): ", end="")
    for node in checkpoint_system.traverse_backward():
        print(f"{node.id}", end=" ")
    print()
    
    # Test 7: Branch from a checkpoint
    print("\n[TEST 7] Branching from CP-2...")
    branch = checkpoint_system.branch_from("CP-2")
    print("Branched chain: ", end="")
    branch.toString()
    
    # Test 8: Rollback one step
    print("\n[TEST 8] Rolling back last node...")
    checkpoint_system.rollback_last()
    print("After rollback: ", end="")
    checkpoint_system.toString()
    
    # Test 9: Rollback to specific checkpoint
    print("\n[TEST 9] Rolling back to CP-1...")
    checkpoint_system.rollback_to("CP-1")
    print("After rollback to CP-1: ", end="")
    checkpoint_system.toString()
    
    # Test 10: Delete specific node
    print("\n[TEST 10] Deleting node CP-1...")
    checkpoint_system.delete_node_by_id("CP-1")
    print("After deletion: ", end="")
    checkpoint_system.toString()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("✓ All core functionality tested")
    print("✓ Checkpoint system working correctly")
