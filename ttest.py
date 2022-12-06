import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_excel('final_results.xlsx')

df_new = df[df['Pacman Agent'] == 'ExpectimaxAgent']
expectimax = df_new['Average Score'].tolist()
print('Expectimax: ',expectimax)
df_new = df[df['Pacman Agent'] == 'MinimaxAgent']
minimax = df_new['Average Score'].tolist()
print('Minimax: ',minimax)
df_new = df[df['Pacman Agent'] == 'MCTSAgent']
mcts = df_new['Average Score'].tolist()
print('MCTS: ',sum(mcts)/len(mcts))


threshold = 0.05
pval = []
stat,p = stats.ttest_ind(a=minimax, b=expectimax, equal_var=False)
print('p values for minimax and expectimax = ',p, p < threshold)
pval.append(p)
stat,p = stats.ttest_ind(a=mcts, b=expectimax, equal_var=False)
print('p values for mcts and expectimax = ',p, p < threshold)
pval.append(p)
stat,p = stats.ttest_ind(a=mcts, b=minimax, equal_var=False)
print('p values for mcts and minimax = ',p, p < threshold)
pval.append(p)

print(pval)


agents = ['minimax-expectimax','montecarlo-expectimax','montecarlo-minimax']
fig = plt.figure(figsize = (5, 3))
plt.bar(agents, pval, color ='red',width = 0.1)
plt.xlabel("agents")
plt.ylabel("P-Values")
plt.title("P-values of T-tests on agents")
plt.savefig('figures/pvalues.png')
plt.show()



def generatePlot(minmaxAvg,expectimaxAvg,mctsAvg,agentList,layoutList,ylabel,title,figureName):
  x = np.arange(len(agentList))  
  figure, plot = plt.subplots()

  plot.set_ylabel(ylabel)
  plot.set_title(title,loc="left")
  plot.set_xticks(x)
  plot.set_xticklabels(agentList)
  plot.tick_params(axis='both', which='major', labelsize=8)


  barWidth = 0.3
  barSet1 = plot.bar(x - barWidth, minmaxAvg, barWidth,label=layoutList[0], color='orange')
  barSet2 = plot.bar(x, expectimaxAvg, barWidth,label=layoutList[1], color='yellow')
  barSet3 = plot.bar(x + barWidth, mctsAvg,barWidth, label=layoutList[2], color='blue')

  def setPlot(results):
      for res in results:
          plot.annotate('{}'.format(res.get_height()),
                      xy=(res.get_x() + res.get_width() / 2, res.get_height()),
                      xytext=(0, 4), 
                      ha='center', va='bottom',
                      textcoords="offset points",
                      fontsize=8)

  setPlot(barSet1)
  setPlot(barSet2)
  setPlot(barSet3)

  plot.legend(bbox_to_anchor=(1.2, 1.4))
  plt.savefig('figures/'+figureName+'.png')
  plt.show()
  
  

## Score Comparision
df_new = df[df['Pacman Agent'] == 'ExpectimaxAgent']
expectimax = df_new['Average Score'].tolist()

df_new = df[df['Pacman Agent'] == 'MinimaxAgent']
minimax = df_new['Average Score'].tolist()

df_new = df[df['Pacman Agent'] == 'MCTSAgent']
mcts = df_new['Average Score'].tolist()

minmaxAvg = sum(minimax)/len(minimax)
expectimaxAvg = sum(expectimax)/len(expectimax)
mctsAvg = sum(mcts)/len(mcts)
agentList = ["Minimax/Expectimax/MCTS Agents"]
layoutList = ["Minimax","Expectimax","MC Tree Search"]
ylabel = 'Average Scores'
title = 'Agents Score Comparision'
generatePlot(minmaxAvg,expectimaxAvg,mctsAvg,agentList,layoutList,ylabel,title,"Scores")


##Win rate comparision

df_new = df[df['Pacman Agent'] == 'ExpectimaxAgent']
expectimax = len(df_new['Win Rate'].tolist())
expectimaxWin = (df_new[df_new['Record']=='Win'])
expectMaxWinAvg = (len(expectimaxWin)/expectimax)*100

df_new = df[df['Pacman Agent'] == 'MinimaxAgent']
minimax = len(df_new['Win Rate'].tolist())
minimaxWin = (df_new[df_new['Record']=='Win'])
miniMaxWinAvg = (len(minimaxWin)/minimax)*100

df_new = df[df['Pacman Agent'] == 'MCTSAgent']
mcts = len(df_new['Win Rate'].tolist())
mctsWin = df_new['Win Rate'].tolist()
mctsWinAvg = sum(mctsWin)/len(mctsWin)*100

agentList = ["Minimax/Expectimax/MCTS Agents"]
layoutList = ["Minimax","Expectimax","MC Tree Search"]
ylabel ='Win Percentage'
title ='Win Percentage Comparision'
generatePlot(miniMaxWinAvg,expectMaxWinAvg,mctsWinAvg,agentList,layoutList,ylabel,title,"WinRate")

##Average steps comparision
df_new = df[df['Pacman Agent'] == 'ExpectimaxAgent']
expectimaxMoves = df_new['Average Number of Moves'].tolist()
expectimaxMovesAvg = sum(expectimaxMoves)/len(expectimaxMoves)

df_new = df[df['Pacman Agent'] == 'MinimaxAgent']
minimaxMoves = df_new['Average Number of Moves'].tolist()
minimaxMovesAvg = sum(minimaxMoves)/len(minimaxMoves)

df_new = df[df['Pacman Agent'] == 'MCTSAgent']
mctsMoves = df_new['Average Number of Moves'].tolist()
mctsMovesAvg = sum(mctsMoves)/len(mctsMoves)

agentList = ["Minimax/Expectimax/MCTS Agents"]
layoutList = ["Minimax","Expectimax","MC Tree Search"]
ylabel ='Number of Moves'
title ='Number of Moves Comparision'
generatePlot(minimaxMovesAvg,expectimaxMovesAvg,mctsMovesAvg,agentList,layoutList,ylabel,title,"MovesCount")

