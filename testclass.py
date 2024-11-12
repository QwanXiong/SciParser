
class testclass:
    def __init__(self):
        print("CLASS INITIALIZED")
        self.var = 0
    def pr(self):
        print('TESTING CLASS')
        self.var = self.var+1
        print(self.var)



newtestclass = testclass()
