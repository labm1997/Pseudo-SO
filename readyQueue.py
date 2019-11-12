import Reader
import Process
import Memory
import bcolors
import Resources
import sys

queueSize = 1000
queueDepth = 4

class Queue():
  def __init__(self, maxsize=-1):
    self.data = []
    self.maxsize = maxsize
  
  def put(self, item):
    if self.maxsize != -1 and len(self.data) >= self.maxsize:
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
      
class ProcessQueue(Queue):
  def __init__(self, priority, maxsize=-1):
    Queue.__init__(self, maxsize=maxsize)
    self.agingStep = 1
    self.maxAge = 10
    self.priority = priority
    
  def getOlder(self):
    processToRemove = []
    for process in self.data:
      process.age = process.age + self.agingStep
      if process.age >= self.maxAge:
        process.priority = process.priority - 1
        process.age = 0
        processToRemove.append(process)
        self.data.remove(process)
        
    return processToRemove
  
  def addProcesses(self, processList):
    for process in processList:
      self.put(process)
    
    
class PriorityQueues():
  def __init__(self, maxsize=queueSize, depth=queueDepth):
    self.queues = [ProcessQueue(i, maxsize=queueSize) for i in range(queueDepth)]
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
      
  def getOlder(self):
    for idxAnt,queue in enumerate(self.queues[1:]):
      processToRemove = queue.getOlder()
      self.queues[idxAnt].addProcesses(processToRemove)

class ReadyQueue():
  def __init__(self):
    self.queue = PriorityQueues()
  
  def chooseProcessToRun(self):
    #print("TODO: Implementar FIFO com prioridade")
    return self.queue.get()
  
  def add(self, process):
    #print("TODO: Implementar adicionar na fila")
    self.queue.put(process, process.priority)
    
  def getOlder(self):
    self.queue.getOlder()
    
  def print(self):
    for queue in self.queue.queues:
      for process in queue.data:
        print(process.relPrior)
    
class Dispatcher():
  def __init__(self, processes, disk, memory, resources):
    self.processesByInitTime = sorted(processes, key = lambda x: x.initTime)
    self.readyQueue = ReadyQueue()
    self.memory = memory
    self.time = self.processesByInitTime[0].initTime if len(self.processesByInitTime) > 0 else 0
    self.disk = disk
    self.currentProcess = None
    self.cpuTime = 0
    self.resources = resources
    
  def printInfo(self, process):
    if process is None: return
    print("dispatcher =>\n\tPID: {0}\n\toffset: {1}\n\tblocks: {2}\n\tpriority: {3}\n\ttime: {4}\n\tprinters: {5}\n\tscanners: {6}\n\tmodems: {7}\n\tdrivers: {8}\n\tcurrentTime: {9}\n\tage: {10}".format(process.pid, process.memOfst, process.memBlks, process.priority, process.cpuTime, process.printer, process.scanner, process.modem, process.sata, self.time, process.age))
  
  def setCurrentProcess(self, process):
    if process is None: 
      self.currentProcess = process
      return
      
    self.cpuTime = process.cpuTime
    self.currentProcess = process
    self.printInfo(self.currentProcess)
    print("process {0} =>\nP{0} STARTED".format(self.currentProcess.pid))
  
  def allocResources(self):
    for resource in self.resources:
        self.resources[resource].alloc(self)
  
  def handleCurrentProcess(self):
    if self.currentProcess is not None:
      
      # Processo acabou
      if not self.currentProcess.hasWorkToDo():
        print("O processo {0} acabou".format(self.currentProcess.pid))
        print("P{0} return SIGINT".format(self.currentProcess.pid))
        self.memory.freeBlocks(self.currentProcess)
        self.currentProcess.deallocResources(self.resources)
        self.setCurrentProcess(None)
        
      # Tempo de CPU acabou
      elif self.cpuTime == 0:
        # Emite erro
        print(("P{0} instruction {1} - " + bcolors.FAIL + "FALHA" + bcolors.ENDC).format(self.currentProcess.pid, self.currentProcess.pc))
        print("O processo {0} esgotou seu tempo de CPU!".format(self.currentProcess.pid))
        #self.readyQueue.add(self.currentProcess)
          
        print("P{0} return SIGINT".format(self.currentProcess.pid))
        self.memory.freeBlocks(self.currentProcess)
        self.currentProcess.deallocResources(self.resources)
        self.setCurrentProcess(None)
  
  def run(self):
    
    # Envelhecemos os processos na fila de prontos
    self.readyQueue.getOlder()
    
    # Lida com o processo atual, retirando se ele acabou e desalocando seus recursos
    self.handleCurrentProcess()
    
    # Aloca recursos aos processos que estão aguardando na fila
    self.allocResources()
    
    # Adiciona processos que foram agendados para agora a lista de prontos
    self.addProcessesToReadyQueue()
    
    # Selecionamos um candidato a novo processo em execução
    processCandidate = self.readyQueue.chooseProcessToRun()
    
    # Atualiza o processo atual se não houver nenhum
    if self.currentProcess is None: self.setCurrentProcess(processCandidate)
    
    # Processo de maior prioridade pode preemptar
    elif processCandidate is not None and processCandidate.priority < self.currentProcess.priority:
      self.readyQueue.add(self.currentProcess)
      print("P{0} return SIGINT".format(self.currentProcess.pid))
      self.setCurrentProcess(processCandidate)
    
    # Processo candidato volta a fila de prontos
    elif processCandidate is not None:
      self.readyQueue.add(processCandidate)
    
    # Trata caso não haja um processo
    if self.currentProcess is None:
      
      # Não há processo na fila de prontos mas há processos a serem adicionados nela (futuramente)
      if len(self.processesByInitTime) > 0:
        # Pulamos para o tempo onde o processo é colocado na fila de prontos
        self.time = self.getNextTime()
        
        # Tenta inserir processos na fila de prontos com base no novo tempo, se não conseguir inserir é pq faltou memória
        if self.time == -1:
          print("GAME OVER: Não há mais memória, no entanto ainda há processos não colocados na fila de prontos. Não há como continuar.")
          return False
        
        self.addProcessesToReadyQueue()
        return True
      else:
        print("GAME OVER: Não há mais o que processar")
        return False
    
    # Executa uma operação do processo
    else:
      self.currentProcess.exec(self.disk)
    
    # Atualiza os tempos
    self.time = self.time + 1
    self.cpuTime = self.cpuTime - 1
    return True
    
  def getNextTime(self):
    for process in self.processesByInitTime:
      if process.initTime > self.time:
        return process.initTime
        
    return -1
  
  def addProcessesToReadyQueue(self):
    nProcessInserted = 0
    for process in self.processesByInitTime:
      if self.time >= process.initTime:
        if not self.memory.allocBlocks(process):
          print(bcolors.WARNING + "WARNING" + bcolors.ENDC + ": t={1}: Processo P{0} não foi colocado na fila de prontos por falta de memória, será colocado em outra oportunidade".format(process.pid, self.time))
          continue
        if process.allocResources(self.resources) is True:
          self.readyQueue.add(process)
        else:
          print(bcolors.WARNING + "WARNING" + bcolors.ENDC + ": t={1}: Processo P{0} não foi colocado na fila de prontos pois não conseguiu todos os recursos necessários".format(process.pid, self.time))
        self.processesByInitTime.remove(process)
        nProcessInserted = nProcessInserted + 1
    return nProcessInserted
    
  def signalAvaliable(self, process):
    if process.doIhaveAllTheResourcesIneed(self.resources):
      self.readyQueue.add(process)

def main():
  processes = Reader.readProcesses(sys.argv[1])
  disk = Reader.readFiles(sys.argv[2], processes)
  memory = Memory.Memory()
  resources = {
    "scanner": Resources.Resource("scanner"),
    "printer1": Resources.Resource("printer1"),
    "printer2": Resources.Resource("printer2"),
    "modem": Resources.Resource("modem"),
    "sata1": Resources.Resource("sata1"),
    "sata2": Resources.Resource("sata2")
  }

  dispatcher = Dispatcher(processes, disk, memory, resources)

  while(dispatcher.run()): pass
  
if __name__ == "__main__":
  main()
