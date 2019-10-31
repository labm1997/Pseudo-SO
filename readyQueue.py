from queue import Queue
import Reader

queueSize = 1000

class RealTimeQueue(Queue):
  def __init__(self):
    Queue.__init__(self, maxsize=queueSize)
    
class UserQueue():
  def __init__(self):
    self.queues = [Queue(maxsize=queueSize) for i in range(3)]
  
  def put(self, process):
    if process.priority in [1,2,3]:
      print("ERROR: Impossível adicionar processo com essa prioridade")
      return
    
    self.queues[process.priority-1].put(process)

class ReadyQueue():
  def __init__(self):
    self.realTimeQueue = RealTimeQueue()
    self.userQueue = UserQueue()
  
  def chooseProcessToRun(self):
    print("TODO: Implementar FIFO com prioridade")
    pass
  
  def add(self, process):
    print("TODO: Implementar adicionar na fila")
    if process.priority == 0:
      self.realTimeQueue.put(process)
    else:
      self.userQueue.put(process)
    
class Dispatcher():
  def __init__(self, processes):
    self.processesByInitTime = sorted(processes, key = lambda x: x.initTime)
    self.readyQueue = ReadyQueue()
    self.time = 0
  
  def run(self):
    self.addProcessesToReadyQueue()
    process = self.readyQueue.chooseProcessToRun()
    process.exec()
    self.time = self.time + 1
  
  def addProcessToReadyQueue(self):
    for process in self.processesByInitTime:
      if process.initTime >= self.time:
        self.readyQueue.add(process)
        self.processesByInitTime.remove(process)
        
    
processes = Reader.readProcesses("process.txt")
disk = Reader.readFiles("files.txt", processes)

ReadyQueue()
dispatcher = Dispatcher(processes)
