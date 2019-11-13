import Reader
import Process
import Memory
import bcolors
import Resources
import sys
import Queues
    
class Dispatcher():
  def __init__(self, processes, disk, memory, resources):
    
    # Lista ordenada de processos agendados por tempo de inicialização e prioridade
    self.processesByInitTime = sorted(processes, key = lambda x: (x.initTime, x.priority))
    
    # Define o tempo inicial como o tempo do primeiro processo agendado
    self.time = self.processesByInitTime[0].initTime if len(self.processesByInitTime) > 0 else 0
    
    # Mantém variações de tempo
    self.timeVariation = 0
    
    # Instancia a fila de prontos
    self.readyQueue = Queues.ReadyQueue()
    
    # Salva elementos como variaveis internas
    self.memory = memory
    self.disk = disk
    self.resources = resources
    
    # Define um processo na CPU
    self.currentProcess = None
    
    # Tempo de CPU restante ao processo executando na CPU
    self.cpuTime = 0
    
  # Mostra informações de um processo em execução
  def printInfo(self, process):
    if process is None: return
    print("dispatcher =>\n\tPID: {0}\n\toffset: {1}\n\tblocks: {2}\n\tpriority: {3}\n\ttime: {4}\n\tprinters: {5}\n\tscanners: {6}\n\tmodems: {7}\n\tdrivers: {8}\n\tcurrentTime: {9}\n\tage: {10}".format(process.pid, process.memOfst, process.memBlks, process.priority, process.cpuTime, process.printer, process.scanner, process.modem, process.sata, self.time, process.age))
  
  # Atualiza o processo que está na CPU
  def setCurrentProcess(self, process):
    if process is None: 
      self.currentProcess = process
      return
      
    self.cpuTime = process.cpuTime
    self.currentProcess = process
    self.printInfo(self.currentProcess)
    print("process {0} =>\nP{0} STARTED".format(self.currentProcess.pid))
  
  # Para cada recurso, se ele estiver disponível, o aloca para o processo que estiver em sua fila
  def allocResources(self):
    for resource in self.resources:
        self.resources[resource].alloc(self)
  
  # Lida com o processo atual caso ele acabe ou não tenha mais tempo de CPU
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
  
  # Núcleo do programa, simula um quantum
  def run(self):
    
    # Envelhecemos os processos na fila de prontos
    self.readyQueue.getOlder(self.timeVariation)
    
    # Lida com o processo atual, retirando se ele acabou e desalocando seus recursos
    self.handleCurrentProcess()
    
    # Aloca recursos aos processos que estão aguardando na fila
    self.allocResources()
    
    # Adiciona processos que foram agendados para agora a lista de prontos
    self.addProcessesToReadyQueue()
    
    # Selecionamos um candidato a novo processo em execução
    processCandidate = self.readyQueue.chooseProcessToRun()
    
    # Atualiza o processo atual se não houver nenhum
    if self.currentProcess is None: 
      self.setCurrentProcess(processCandidate)
      
      # Retira o candidado da fila de prontos
      self.readyQueue.pop()
    
    # Processo de maior prioridade pode preemptar
    elif processCandidate is not None and processCandidate.priority < self.currentProcess.priority:
      self.readyQueue.add(self.currentProcess)
      print("P{0} return SIGINT".format(self.currentProcess.pid))
      self.setCurrentProcess(processCandidate)
      
      # Retira o candidado da fila de prontos
      self.readyQueue.pop()
    
    # Trata caso não haja um processo
    if self.currentProcess is None:
      
      # Não há processo na fila de prontos mas há processos a serem adicionados nela (futuramente)
      if len(self.processesByInitTime) > 0:
        # Pulamos para o tempo onde o processo é colocado na fila de prontos
        candidateTime = self.getNextTime()
        
        # Se não há processos nos agendados com tempo maior que o atual é pq nenhum deles conseguiu memória e o programa acaba
        if candidateTime == -1:
          print("GAME OVER: Não há mais memória, no entanto ainda há processos não colocados na fila de prontos. Não há como continuar.")
          return False
          
        # Atualiza o tempo
        self.timeVariation = candidateTime - self.time
        self.time = candidateTime
        
        # Tenta adicionar os processos a fila de prontos
        self.addProcessesToReadyQueue()
        return True
        
      # Programa acaba
      else:
        print("GAME OVER: Não há mais o que processar")
        return False
    
    # Executa uma operação do processo
    else:
      self.currentProcess.exec(self.disk)
    
    # Atualiza os tempos
    self.time = self.time + 1
    self.cpuTime = self.cpuTime - 1
    self.timeVariation = 1
    return True
  
  # Obtém o próximo tempo de simulação
  def getNextTime(self):
    # O próximo tempo é o primeiro tempo de processo agendado maior que o tempo atual
    for process in self.processesByInitTime:
      if process.initTime > self.time:
        return process.initTime
    
    # Se todos os tempos de processos agendados são menores é pq foram processos que não conseguiram memória e não há nada que se possa fazer
    return -1
  
  # Adiciona processos da fila de agendados para a fila de prontos, alocando recursos necessários
  def addProcessesToReadyQueue(self):
    processToRemove = []
    
    for process in self.processesByInitTime:
    
      # Se é hora de adicionar o processo a fila de prontos
      if self.time >= process.initTime:
        
        # Pula o processo se não tiver memória
        if not self.memory.allocBlocks(process):
          print(bcolors.WARNING + "WARNING" + bcolors.ENDC + ": t={1}: Processo P{0} não foi colocado na fila de prontos por falta de memória, será colocado em outra oportunidade".format(process.pid, self.time))
          continue
        
        # Se o processo consegue os recursos ele é adicionado a fila de prontos, allocResources adiciona automaticamente o processo a fila do recurso caso não consiga algum
        if process.allocResources(self.resources) is True:
          self.readyQueue.add(process)
          
        # Se o processo não consegue os recursos emite uma mensagem
        else:
          print(bcolors.WARNING + "WARNING" + bcolors.ENDC + ": t={1}: Processo P{0} não foi colocado na fila de prontos pois não conseguiu todos os recursos necessários".format(process.pid, self.time))
        
        processToRemove.append(process)
    
    # Remove os processos que foram para a fila de prontos ou para alguma fila de bloqueio da fila de agendados
    for process in processToRemove: self.processesByInitTime.remove(process)
  
  # Adiciona processo a lista de prontos se ele tem todos os recursos de que precisa para executar 
  def signalAvaliable(self, process):
    if process.doIhaveAllTheResourcesIneed(self.resources):
      self.readyQueue.add(process)

def main():
  # Instancia os processos com base no arquivo lido
  processes = Reader.readProcesses(sys.argv[1])
  
  # Instancia um disco com base no arquivo
  disk = Reader.readFiles(sys.argv[2], processes)
  
  # Instancia uma memória
  memory = Memory.Memory()
  
  # Define os recursos
  resources = {
    "scanner": Resources.Resource("scanner"),
    "printer1": Resources.Resource("printer1"),
    "printer2": Resources.Resource("printer2"),
    "modem": Resources.Resource("modem"),
    "sata1": Resources.Resource("sata1"),
    "sata2": Resources.Resource("sata2")
  }

  # Instancia o dispachante passando processos, disco, memória e recursos de I/O
  dispatcher = Dispatcher(processes, disk, memory, resources)
  
  # Executa quantum a quantum
  while(dispatcher.run()): pass
  
if __name__ == "__main__":
  main()
