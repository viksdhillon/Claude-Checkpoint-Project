
class Node:
    def __init__(self,message, count):
        self.message = message
        self.position = count
        self.next = None
    
class LinkedList:
    def __init__(self):
        self.front = None
        self.back = None
        self.count = 0

    def append(self, message):
        if not self.front and not self.back:
            self.front = Node(message, self.count)
            self.back = self.front
            self.front.next = self.back
            self.count += 1
        elif not self.back:
            self.back = Node(message, self.count)
            self.front.next = self.back
            self.count +=1
        else:
            curr = Node(message, self.count)
            self.back.next = curr
            self.back = self.back.next
            self.count += 1

    def __str__(self):
        curr = self.front
        retString = ""
        while curr.next:
            retString += f"{curr.position}: {curr.message},   "
            curr = curr.next
        retString += f"{self.back.position}: {self.back.message}"
        return retString

    def find(self, message):
        curr = self.front
        while curr.next:
            if message in curr.message:
                return curr.position
            curr = curr.next

        if message in self.back:
            return self.back.position
        else:
            return "No prompt exists"
# test harness

if __name__ == "__main__":
    ll = LinkedList()
    ll.append("first")
    ll.append("second")
    ll.append("third")
    ll.append("4")
    ll.append("5")
    ll.append("6")
    ll.append("7")
    ll.append("8")
    ll.append("9")
    print("Linked list contents:")
    print(ll)
    print(ll.find("sec"))
        


