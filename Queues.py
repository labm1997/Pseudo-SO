queueSize = 1000
queueDepth = 4

class Queue():
  def __init__(self, maxsize=-1):
    # Armazena os dados da fila
    self.data = []
    
    # Define um tamanho máximo para a fila
    self.maxsize = maxsize
  
  # Coloca um item na fila, emite uma mensagem em caso de erro
  def put(self, item):
    if self.maxsize != -1 and len(self.data) >= self.maxsize:
      print("ERROR: Fila cheia!")
      return
    
    self.data.append(item)
  
  # Pega o item no topo da fila, retirando dela
  def get(self):
    if len(self.data) == 0: return None
    ret = self.data[0]
    self.data = self.data[1:]
    return ret
    
  # Retira o item no topo da fila
  def pop(self):
    if len(self.data) == 0: return
    self.data = self.data[1:]
  
  # Pega o item no topo da fila, sem retirar dela
  def top(self):
    if len(self.data) == 0: return None
    return self.data[0]
  
  # Retorna o número de elementos na fila
  def size(self):
    return len(self.data)
      
class ProcessQueue(Queue):
  def __init__(self, priority, maxsize=-1):
    Queue.__init__(self, maxsize=maxsize)
    
    # Fila de processos tem uma taxa de envelhecimento
    self.agingStep = 1
    
    # Valor máximo de idade para sair da fila
    self.maxAge = 10
    
    # Prioridade da fila
    self.priority = priority
    
  # Envelhece os processos na fila
  def getOlder(self):
    processToRemove = []
    
    for process in self.data:
      # Envelhece
      process.age = process.age + self.agingStep
      
      # Processo é velho demais
      if process.age >= self.maxAge:
        # Muda a prioridade
        process.priority = process.priority - 1
        
        # Zera a idade
        process.age = 0
        
        # Agenda para remover
        processToRemove.append(process)
    
    # Remove os processos da fila que são muito velhos
    for process in processToRemove: self.data.remove(process)
    
    # Retorna os processos que foram removidos
    return processToRemove
  
  # Adiciona uma lista de processos, na ordem da lista, a fila
  def addProcesses(self, processList):
    for process in processList:
      self.put(process)
    
    
class PriorityQueues():
  def __init__(self, maxsize=queueSize, depth=queueDepth):
    # Instancia quatro filas cada uma com a prioridade 0,1,2,3
    self.queues = [ProcessQueue(i, maxsize=queueSize) for i in range(queueDepth)]
    
    # Número de filas
    self.queueDepth = queueDepth
  
  # Adiciona um processo de acordo com o nível
  def put(self, process, level):
    if level >= self.queueDepth:
      print("ERROR: Impossível adicionar processo com essa prioridade")
      return
    
    self.queues[level].put(process)
  
  # Obtém o primeiro da fila não vazia mais prioritária, retirando dessa fila
  def get(self):
    for queue in self.queues:
      if queue.size() > 0: return queue.get()
      
  # Obtém o primeiro da fila não vazia mais prioritária, sem retirar dessa fila
  def top(self):
    for queue in self.queues:
      if queue.size() > 0: return queue.top()
      
  # Retira o primeiro da fila não vazia mais prioritária
  def pop(self):
    for queue in self.queues:
      if queue.size() > 0: 
        queue.pop()
        return
    
  # Envelhece os elementos de todas as filas exceto a de tempo real
  def getOlder(self):
    for idxAnt,queue in enumerate(self.queues[1:]):
      processToRemove = queue.getOlder()
      
      # Adiciona os velhos a fila de maior prioridade
      self.queues[idxAnt].addProcesses(processToRemove)

class ReadyQueue():
  def __init__(self):
    self.queue = PriorityQueues()
  
  # Retorna o processo mais prioritário
  def chooseProcessToRun(self):
    return self.queue.top()
  
  # Adiciona um processo a fila de prioridades com base na prioridade do processo
  def add(self, process):
    self.queue.put(process, process.priority)
    
  def pop(self):
    self.queue.pop()
    
  # Envelhece os processos
  def getOlder(self):
    self.queue.getOlder()
  
  def print(self):
    for queue in self.queue.queues:
      for process in queue.data:
        print(process.relPrior)
