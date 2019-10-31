import Reader
import Process

queueSize = 1000
queueDepth = 4

class Queue():
  def __init__(self, maxsize=-1):
    self.data = []
    self.maxsize = maxsize
  
  def put(self, item):
    if len(self.data) >= self.maxsize:
      print("ERROR: Fila cheia!")
      return
    
    self.data.append(item)
  
  def get(self):
    if len(self.data) == 0: return None
    ret = self.data[0]
    self.data = self.data[1:]
    return ret
  
  def top(self):
    if len(self.data) == 0: return None
    return self.data[0]
    
  def size(self):
    return len(self.data)
    
class PriorityQueues():
  def __init__(self, maxsize=queueSize, depth=queueDepth):
    self.queues = [Queue(maxsize=queueSize) for i in range(queueDepth)]
    self.queueDepth = queueDepth
  
  def put(self, process, level):
    if level >= self.queueDepth:
      print("ERROR: Impossível adicionar processo com essa prioridade")
      return
    
    self.queues[level].put(process)
  
  def get(self):
    for queue in self.queues:
      if queue.size() > 0: return queue.get()
      
  def top(self):
    for queue in self.queues:
      if queue.size() > 0: return queue.top()

class ReadyQueue():
  def __init__(self):
    self.queue = PriorityQueues()
  
  def chooseProcessToRun(self):
    #print("TODO: Implementar FIFO com prioridade")
    return self.queue.get()
  
  def add(self, process):
    #print("TODO: Implementar adicionar na fila")
    self.queue.put(process, process.priority)
    
class Dispatcher():
  def __init__(self, processes, disk):
    self.processesByInitTime = sorted(processes, key = lambda x: x.initTime)
    self.readyQueue = ReadyQueue()
    self.time = 0
    self.disk = disk
    self.currentProcess = None
    self.cpuTime = 0
    
  def printInfo(self, process):
    if process is None: return
    print("dispatcher =>\n\tPID: {0}\n\toffset: {1}\n\tblocks: {2}\n\tpriority: {3}\n\ttime: {4}\n\tprinters: {5}\n\tscanners: {6}\n\tmodems: {7}\n\tdrivers: {8}".format(process.pid, 0, process.memBlks, process.priority, process.initTime+1, process.printer, process.scanner, process.modem, process.sata))
  
  def setCurrentProcess(self, process):
    if process is None: 
      self.currentProcess = process
      return
    
    self.cpuTime = process.cpuTime
    self.currentProcess = process
    self.printInfo(self.currentProcess)
    print("process {0} =>\nP{0} STARTED".format(self.currentProcess.pid))
    
  
  def run(self):
    self.addProcessesToReadyQueue()
    
    # Selecionamos um candidato a novo processo em execução
    processCandidate = self.readyQueue.chooseProcessToRun()
    
    # Atualiza o processo atual se não houver nenhum
    if self.currentProcess is None:
      self.setCurrentProcess(processCandidate)
    
    # Tempo de CPU acabou
    elif self.cpuTime == 0:
      # Se ainda tinha o que processar emite erro
      if self.currentProcess.hasWorkToDo():
        print("P{0} instruction {1} - FALHA".format(self.currentProcess.pid, self.currentProcess.pc))
        print("O processo {0} esgotou seu tempo de CPU!".format(self.currentProcess.pid))
      self.setCurrentProcess(processCandidate)
    
    # Processo de tempo real pode preemptar
    elif type(self.currentProcess) != Process.RealTimeProcess and type(processCandidate) == Process.RealTimeProcess:
      self.readyQueue.add(self.currentProcess)
      self.setCurrentProcess(processCandidate)
    
    # Processo candidato volta a fila de prontos
    elif processCandidate is not None:
      self.readyQueue.add(processCandidate)
    
    # Executa uma instrução do processo
    if self.currentProcess is None: 
      #print("Sem processo na fila de prontos! t = {0}".format(self.time))
      if len(self.processesByInitTime) > 0: self.time = self.processesByInitTime[0].initTime
      else:
        return False
        print("GAME OVER: Não há mais o que processar")
    else:
      self.currentProcess.exec(self.disk)
    
    self.time = self.time + 1
    self.cpuTime = self.cpuTime - 1
    return True
  
  def addProcessesToReadyQueue(self):
    for process in self.processesByInitTime:
      if self.time >= process.initTime:
        self.readyQueue.add(process)
        self.processesByInitTime.remove(process)
        
    
processes = Reader.readProcesses("process.txt")
disk = Reader.readFiles("files.txt", processes)

ReadyQueue()
dispatcher = Dispatcher(processes, disk)

while(dispatcher.run()): pass
