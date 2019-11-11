import math
import Disk
import Process
import bcolors

def readProcesses(fileName):
  processes = []
  with open(fileName) as f:
    lines = f.readlines()
    for pid,line in enumerate(lines):
      splittedLine = line[:-1].split(',')
      priority = int(splittedLine[1])
      if priority == 0:
        processes.append(Process.RealTimeProcess(pid, *[int(x) for x in splittedLine]))
      else:
        processes.append(Process.UserProcess(pid, *[int(x) for x in splittedLine]))
  return processes
  
def readFiles(fileName, processes):
  with open(fileName) as f:
    lines = f.readlines()
    nBlocks = int(lines[0])
    nFiles = int(lines[1])
    files = {}
    
    for line in lines[2:nFiles+2]:
      fields = line.split(",")
      fileName = fields[0]
      files[fileName] = Disk.File(fileName, int(fields[1]), int(fields[2]), None)
    
    for line in lines[nFiles+2:]:
      fields = line.replace(' ', '').split(',')
      pid = int(fields[0])
      if pid >= len(processes):
        print(bcolors.WARNING + "WARNING" + bcolors.ENDC + ": Operação de arquivo em processo inexistente (PID = {0})".format(pid))
        continue
      
      # Operação de criar arquivo
      if int(fields[1]) == 0:
        processes[pid].addFileOp(int(fields[4]), Process.CreateFileOperation(processes[pid], fields[2], int(fields[3])))
      elif int(fields[1]) == 1:
        processes[pid].addFileOp(int(fields[3]), Process.DeleteFileOperation(processes[pid], fields[2]))
    
    return Disk.FileSystem(nBlocks, files)
  
  return None
