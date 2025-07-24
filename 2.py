import numpy as np
import time
import pygame
import sys
import random
import math
import time
pygame.init()
WIDTH = 900             #視窗長
HEIGHT = 900            #視窗寬
GRID_SIZE = 300         #每個格子大小
white = (255,255,255)
screen = pygame.display.set_mode([WIDTH, HEIGHT])  #建立900*900的視窗
screen.fill(white)
pygame.display.set_caption("量子井字遊戲")
def draw_line():       #畫井字格線
    pygame.draw.line(screen, 'black', [GRID_SIZE,0],[GRID_SIZE,HEIGHT],width = 9)
    pygame.draw.line(screen, 'black', [GRID_SIZE*2,0],[GRID_SIZE*2,HEIGHT],width = 9)
    pygame.draw.line(screen, 'black', [0,GRID_SIZE*2],[WIDTH,GRID_SIZE*2],width = 9)
    pygame.draw.line(screen, 'black', [0,GRID_SIZE],[WIDTH,GRID_SIZE],width = 9)
#board -> 0:沒棋子 1:未觀測的O 2:未觀測的X 3:觀測後為O 4:觀測後為X 5:不能使用的格子
board = np.zeros([3,3,2])   
O_list = np.full([9,2,3],-1)
X_list = np.full([9,2,3],-1)
O_list_2 = np.zeros([3,3])
X_list_2 = np.zeros([3,3])
remove_list = []
big_symbol_list = []
global running
running = None
global observing_O
observing_O = None
global observing_X
observing_X = None
global chain_reaction_again
chain_reaction_again = None
#繪製OX的函式
def draw_symbol(symbol, turn_num, size, location_x, location_y):
#location(x,y): 00 10 20
#               01 11 21
#               02 12 22
    if size == 0:   #放在左邊的小棋子
        font = pygame.font.Font(None, 75)
        text = font.render(symbol + str(turn_num),True,(0,0,0))    
        text_rect = text.get_rect(center=(location_x*GRID_SIZE+1/4*GRID_SIZE,location_y*GRID_SIZE+1/2*GRID_SIZE))
        screen.blit(text,text_rect)  
    elif size == 1: #放在右邊的小棋子
        font = pygame.font.Font(None, 75)
        text = font.render(symbol + str(turn_num),True,(0,0,0))    
        text_rect = text.get_rect(center=(location_x*GRID_SIZE+3/4*GRID_SIZE,location_y*GRID_SIZE+1/2*GRID_SIZE))
        screen.blit(text,text_rect)  
    elif size == 2: #大棋子
        font = pygame.font.Font(None,300)
        text = font.render(symbol + str(turn_num),True,(0,0,0))
        text_rect = text.get_rect(center=(location_x*GRID_SIZE+1/2*GRID_SIZE,location_y*GRID_SIZE+1/2*GRID_SIZE))
        screen.blit(text,text_rect)
    pygame.display.flip()

#繪製棋子不存在的函式
def draw_none(location_x, location_y, size):
    x = location_x * GRID_SIZE
    y = location_y * GRID_SIZE

    if size == 0:   # 左邊的小棋子
        pygame.draw.rect(screen, white, (x+10, y+10, GRID_SIZE // 2-15, GRID_SIZE-30))
    elif size == 1: # 右邊的小棋子
        pygame.draw.rect(screen, white, (x+10 + GRID_SIZE // 2, y+10, GRID_SIZE // 2-15, GRID_SIZE-30))
    
    pygame.display.flip()




#判斷勝負的函式
def check_winner(symbol_num):       #symbol: O -> 3, X -> 4
    for i in range(3):
        if all(board[i][j][0]==symbol_num for j in range(3)):
            return True
        if all(board[j][i][0]==symbol_num for j in range(3)):
            return True
    for i in range(3):
        if all(board[i][j][1]==symbol_num for j in range(3)):
            return True
        if all(board[j][i][1]==symbol_num for j in range(3)):
            return True
    if all(board[i][i][0]==symbol_num for i in range(3)) or all(board[i][i][1]==symbol_num for i in range(3)):
        return True
    if all(board[i][2-i][0]==symbol_num for i in range(3)) or all(board[i][2-i][1]==symbol_num for i in range(3)):
        return True
    return False

#判斷格子是否用完的函式
def check_draw():
    if 0 not in board:
        if 1 not in board and 2 not in board:
            return 0    #格子用完了
        else:
            return 1    #只能觀測
    else:
        return 2        #繼續進行

#觀測後續的連鎖函式 
#因同格棋子存在導致此棋子崩塌為不存在 使其糾纏態改為存在
chain_chess = []    # [location_x,location_y,size]的形式
def chain_reaction(location_x, location_y, size):   #此棋不存在
    global chain_chess
    whether_chain_reaction = True
    chain_reaction_again = False
    chain_turn_num = 0
    for i in range(len(O_list)):
        for j in range(2):
            if O_list[i][j][0] == location_x and O_list[i][j][1] == location_y and O_list[i][j][2] == size:
                chain_turn_num = i +1
                chain_symbol = "O"
                chain_target_list = O_list
                chain_list_2 = O_list_2
                chain_chess_num = j+1                
    if chain_turn_num == 0:
        for i in range(len(X_list)):
            for j in range(2):
                if X_list[i][j][0] == location_x and X_list[i][j][1] == location_y and X_list[i][j][2] == size:
                    chain_turn_num = i +1
                    chain_symbol = "X"
                    chain_target_list = X_list
                    chain_list_2 = X_list_2
                    chain_chess_num = j+1
    if chain_turn_num == 0:
        print("錯誤")
    else:
        test_turn_num,test_chess_num = 0,0
        for i in range(len(chain_target_list)):
            for j in range(2):
                if chain_target_list[i][j][0] == location_x and chain_target_list[i][j][1] == location_y and chain_target_list[i][j][2] == 1 - size:
                    test_turn_num = i +1
                    test_chess_num = j+1
                    break
        if test_turn_num == 0 and test_chess_num == 0:
            chain_list_2[location_y][location_x] = 0   
        else:
            if board[location_y][location_x][size] not in [3,4,5]:
                board[location_y][location_x][size] = 0                
        chain_other_x, chain_other_y, chain_other_size = chain_target_list[chain_turn_num - 1][2 - chain_chess_num]     #此棋的糾纏對
        chain_chess.append([chain_other_x,chain_other_y,chain_other_size])
        remove_list.extend([location_x,location_y,size])
        remove_list.extend([chain_other_x,chain_other_y,chain_other_size])
        if board[chain_other_y][chain_other_x][1 - chain_other_size] in [1,2]:  
            chain_reaction_again = True
            remove_list.extend([chain_other_x,chain_other_y,1 - chain_other_size])
            
        big_symbol_list.extend([chain_symbol,chain_turn_num,2,chain_other_x,chain_other_y])
        if chain_symbol == "O":
             board[chain_other_y][chain_other_x][0] = 3
             board[chain_other_y][chain_other_x][1] = 5
             X_list_2[chain_other_y][chain_other_x] = 0
        else:
            board[chain_other_y][chain_other_x][0] = 4
            board[chain_other_y][chain_other_x][1] = 5
            O_list_2[chain_other_y][chain_other_x] = 0
        if board[chain_other_y][chain_other_x][1 - chain_other_size] in [0,5]:
            pass
        else:
            location_x,location_y,size = chain_other_x,chain_other_y,(1 - chain_other_size)   
    if chain_reaction_again:
            if chain_chess[-1] == chain_chess[0]:   #形成完全閉環，不能再次chain_reaction否則會重複無限多次
                whether_chain_reaction = False
                chain_chess = []
            if whether_chain_reaction:
                chain_reaction(chain_other_x,chain_other_y,1-chain_other_size)
    else:
        chain_chess = []


    

    

#觀測的函式
def observe(symbol, turn_num, location_x, location_y, size, chess_num):
    global running
    global observing_O
    global observing_X
    result = random.randint(0, 1)  # 隨機決定觀測結果 (0 = 不存在, 1 = 存在)
    #該回合的糾纏棋子座標
    other_x, other_y, other_size = O_list[turn_num - 1][2 - chess_num] if symbol == "O" else X_list[turn_num - 1][2 - chess_num]
    if symbol == "O":
        symbol_list = O_list
        symbol_list_2 = O_list_2
    else:
        symbol_list = X_list
        symbol_list_2 = X_list_2

    if result == 0:  #不存在
        board[location_y][location_x][size] = 0  #移除當前棋子
        if symbol == "O":
            if board[location_y][location_x][1-size] != 1:
                O_list_2[location_y][location_x] = 0
        if symbol == "X":
            if board[location_y][location_x][1-size] != 2:
                X_list_2[location_y][location_x] = 0
        test_turn_num,test_chess_num = 0,0
        for i in range(len(symbol_list)):
            for j in range(2):
                if symbol_list[i][j][0] == location_x and symbol_list[i][j][1] == location_y and symbol_list[i][j][2] == 1 - size:
                    test_turn_num = i +1
                    test_chess_num = j+1
                    break
        if test_turn_num == 0 and test_chess_num == 0:
            if board[location_y][location_x][1 - size] == 0:
                symbol_list_2[location_y][location_x] = 0
        draw_none(location_x, location_y, size)  
        #檢查糾纏棋子的格子內是否還有其他棋子
        if board[other_y][other_x][0] != 0 or board[other_y][other_x][1] != 0:
            board[other_y][other_x][0] = 3 if symbol == "O" else 4  # 糾纏棋子變為「確定存在」
            board[other_y][other_x][1] = 5
            remove_list.extend([other_x,other_y,other_size])
            if board[other_y][other_x][1-other_size] != 0:  
                chain_reaction(other_x,other_y,1-other_size)
            chain_chess.append([other_x,other_y,1-other_size])
            big_symbol_list.extend([symbol,turn_num,2,other_x,other_y])
        for i in range(len(remove_list) // 3):
            draw_none(remove_list[3*i],remove_list[3*i+1],remove_list[3*i+2])
        for i in range(len(big_symbol_list) // 5):   
            draw_symbol(big_symbol_list[5*i],big_symbol_list[5*i+1],big_symbol_list[5*i+2],big_symbol_list[5*i+3],big_symbol_list[5*i+4])
        print("不存在")
        running = True
        if symbol == "O":
            observing_O = False
        elif symbol == "X":
            observing_X = False
        

    elif result == 1:  #存在
        remove_list.extend([location_x,location_y,size])
        chain_chess.append([location_x,location_y,size])
        observe_turn_num = 0
        if symbol == "O":
                target_list = O_list
                target_list_2 = O_list_2
        elif symbol == "X":
                target_list = X_list
                target_list_2 = X_list_2           
        for i in range(len(target_list)):
            for j in range(2):
                if target_list[i][j][0] == location_x and target_list[i][j][1] == location_y and target_list[i][j][2] == size:
                    observe_turn_num = i +1
        if observe_turn_num != 0:
            big_symbol_list.extend([symbol,observe_turn_num,2,location_x,location_y])   

        else:
            print("observe_turn_num = 0, 錯誤!")
        
        #若該格內有其他棋子，則將該棋子設為不存在
        if board[location_y][location_x][1 - size] in [1,2]:  
            chain_reaction(location_x,location_y,1-size)
            board[location_y][location_x][1] = 5 
            board[location_y][location_x][0] = 3 if symbol == "O" else 4 


        #將糾纏棋子設為不存在
        if board[other_y][other_x][1-other_size] == 0:
            board[other_y][other_x][other_size] = 0
        remove_list.extend([other_x,other_y,other_size])
        test_turn_num,test_chess_num = 0,0
        for i in range(len(target_list)):
            for j in range(2):
                if target_list[i][j][0] == other_x and target_list[i][j][1] == other_y and target_list[i][j][2] == 1 - other_size:
                    test_turn_num = i +1
                    test_chess_num = j+1
                    break
        if test_turn_num == 0 and test_chess_num == 0:
            target_list_2[location_y][location_x] = 1
            target_list_2[other_y][other_x] = 0
        for i in range(len(remove_list) // 3):
            draw_none(remove_list[3*i],remove_list[3*i+1],remove_list[3*i+2])
        for i in range(len(big_symbol_list) // 5):   
            draw_symbol(big_symbol_list[5*i],big_symbol_list[5*i+1],big_symbol_list[5*i+2],big_symbol_list[5*i+3],big_symbol_list[5*i+4])
        print("存在")
        running = True
        if symbol == "O":
            observing_O = False
        elif symbol == "X":  
            observing_X = False

#判斷是否觀測的函式
def whether_observe(symbol):
    if symbol == "O":
        for i in range(3):
            if O_list_2[0][i] == O_list_2[1][i] == O_list_2[2][i] == 1:
                print(f"請觀測"+symbol+"第"+str(i+1)+"直行")
                return True
            if O_list_2[i][0] == O_list_2[i][1] == O_list_2[i][2] == 1:
                print(f"請觀測"+symbol+"第"+str(i+1)+"橫行")
                return True
        if O_list_2[0][0] == O_list_2[1][1] == O_list_2[2][2] == 1:
            print(f"請觀測"+symbol+"左上右下斜線")
            return True
        if O_list_2[2][0] == O_list_2[1][1] == O_list_2[0][2] == 1:
            print(f"請觀測"+symbol+"右上左下斜線")
            return True
        return False
    elif symbol == "X":
        for i in range(3):
            if X_list_2[0][i] == X_list_2[1][i] == X_list_2[2][i] == 1:
                print(f"請觀測"+symbol+"第"+str(i+1)+"直行")
                return True
            if X_list_2[i][0] == X_list_2[i][1] == X_list_2[i][2] == 1:
                print(f"請觀測"+symbol+"第"+str(i+1)+"橫行")
                return True
        if X_list_2[0][0] == X_list_2[1][1] == X_list_2[2][2] == 1:
            print(f"請觀測"+symbol+"左上右下斜線")
            return True
        if X_list_2[2][0] == X_list_2[1][1] == X_list_2[0][2] == 1:
            print(f"請觀測"+symbol+"右上左下斜線")
            return True
        return False
    
            
#主迴圈
def main():
    global running
    play_turn = True  # True: O, False: X
    turn_num = 1      #回合數
    chess = 0         #每回合的第幾步棋(1或2)
    chess_num = 0   
    global observing_O, observing_X
    observing_O = False
    observing_X = False
    draw_line()
    running = True    # 遊戲是否進行

    while True:  
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # O 玩家
                if play_turn and event.type == pygame.MOUSEBUTTONDOWN and chess < 2:
                    if event.button == pygame.BUTTON_LEFT:
                        x, y = pygame.mouse.get_pos()
                        location_x, location_y = x // GRID_SIZE, y // GRID_SIZE

                        if board[location_y][location_x][0] == 0:
                            chess += 1
                            if chess == 1:
                                first_chess = (location_x, location_y)  #記錄這回合第一步棋子位置
                            board[location_y][location_x][0] = 1
                            O_list[turn_num - 1][chess - 1] = [location_x, location_y, 0]
                            O_list_2[location_y][location_x] = 1
                            draw_symbol("O", turn_num, 0, location_x, location_y)

                        elif board[location_y][location_x][0] != 0 and board[location_y][location_x][1] == 0:
                            if (location_x, location_y) == first_chess:
                                count = np.sum(board==0)
                                if count > 1:
                                    print("同回合棋子不能下在同一格")
                                else:
                                    chess += 1
                                    board[location_y][location_x][1] = 1
                                    O_list[turn_num - 1][chess - 1] = [location_x, location_y, 1]
                                    O_list_2[location_y][location_x] = 1
                                    draw_symbol("O", turn_num, 1, location_x, location_y)                                
                            else:
                                chess += 1
                                board[location_y][location_x][1] = 1
                                O_list[turn_num - 1][chess - 1] = [location_x, location_y, 1]
                                O_list_2[location_y][location_x] = 1
                                draw_symbol("O", turn_num, 1, location_x, location_y)
                        else:
                            print("這格不能下棋")

                if chess == 2 and play_turn:
                    first_chess = None
                    if check_winner(symbol_num=3):
                        if check_winner(symbol_num=4):
                            print("雙方皆連線")
                            time.sleep(2)
                            pygame.quit()
                            sys.exit()
                        else:
                            print("O玩家獲勝!")
                            time.sleep(2)
                            pygame.quit()
                            sys.exit()
                    elif check_winner(symbol_num=4):
                        if check_winner(symbol_num=3):
                            print("雙方皆連線")
                            time.sleep(2)
                            pygame.quit()
                            sys.exit()
                        else:
                            print("X玩家獲勝!")
                            time.sleep(2)
                            pygame.quit()
                            sys.exit()
                    elif check_draw() == 0:
                        print("平局!")
                        time.sleep(2)
                        pygame.quit()
                        sys.exit()
                    elif check_draw() == 1:
                        print("只能觀測!")

                    if whether_observe("O"):
                        observing_O = True
                        running = False
                        continue
                    elif whether_observe("X"):
                        observing_X = True
                        running = False
                        continue

                    play_turn = False
                    chess = 0

                # X 玩家
                elif not play_turn and event.type == pygame.MOUSEBUTTONDOWN and chess < 2:
                    if event.button == pygame.BUTTON_LEFT:
                        x, y = pygame.mouse.get_pos()
                        location_x, location_y = x // GRID_SIZE, y // GRID_SIZE

                        if board[location_y][location_x][0] == 0:
                            chess += 1
                            if chess == 1:
                                first_chess = (location_x, location_y)
                            board[location_y][location_x][0] = 2
                            X_list[turn_num - 1][chess - 1] = [location_x, location_y, 0]
                            X_list_2[location_y][location_x] = 1
                            draw_symbol("X", turn_num, 0, location_x, location_y)
                        elif board[location_y][location_x][0] != 0 and board[location_y][location_x][1] == 0:
                            if (location_x, location_y) == first_chess:
                                count = np.sum(board==0)
                                if count > 1:
                                    print("同回合棋子不能下在同一格")
                                else:
                                    chess += 1
                                    board[location_y][location_x][1] = 2
                                    X_list[turn_num - 1][chess - 1] = [location_x, location_y, 1]
                                    X_list_2[location_y][location_x] = 1
                                    draw_symbol("X", turn_num, 1, location_x, location_y)
                            else:
                                chess += 1
                                board[location_y][location_x][1] = 2
                                X_list[turn_num - 1][chess - 1] = [location_x, location_y, 1]
                                X_list_2[location_y][location_x] = 1
                                draw_symbol("X", turn_num, 1, location_x, location_y)
                        else:
                            print("這格不能下棋")

                if chess == 2 and not play_turn:
                    turn_num += 1
                    first_chess = None
                    if check_winner(symbol_num=3):
                        if check_winner(symbol_num=4):
                            print("雙方皆連線")
                            time.sleep(2)
                            pygame.quit()
                            sys.exit()
                        else:
                            print("O玩家獲勝!")
                            time.sleep(2)
                            pygame.quit()
                            sys.exit()
                    elif check_winner(symbol_num=4):
                        if check_winner(symbol_num=3):
                            print("雙方皆連線")
                            time.sleep(2)
                            pygame.quit()
                            sys.exit()
                        else:
                            print("X玩家獲勝!")
                            time.sleep(2)
                            pygame.quit()
                            sys.exit()
                    elif check_draw() == 0:
                        print("平局!")
                        time.sleep(2)
                        pygame.quit()
                        sys.exit()
                    elif check_draw() == 1:
                        print("只能觀測!")

                    if whether_observe("X"):
                        observing_X = True
                        running = False
                        continue
                    elif whether_observe("O"):
                        observing_O = True
                        running = False
                        continue

                    play_turn = True
                    chess = 0

            pygame.display.flip()

        # O觀測階段
        while observing_O:
            observe_turn_num = 0
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_RIGHT:
                    x, y = pygame.mouse.get_pos()
                    location_x, location_y = x // GRID_SIZE, y // GRID_SIZE
                    size = 0 if x % GRID_SIZE <= 150 else 1
                    found = False
                    for i in range(len(O_list)):
                        for j in range(2):
                            if O_list[i][j][0] == location_x and O_list[i][j][1] == location_y and O_list[i][j][2] == size:
                                observe_turn_num = i + 1
                                chess_num = j + 1
                                found = True
                                break       
                        if found:
                            break
                    if chess_num != 0:
                        observe("O", observe_turn_num, location_x, location_y, size, chess_num) 

                    else:
                        print("點擊錯誤非O棋子")

        # X觀測階段
        while observing_X:
            observe_turn_num = 0
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_RIGHT:
                    x, y = pygame.mouse.get_pos()
                    location_x, location_y = x // GRID_SIZE, y // GRID_SIZE
                    size = 0 if x % GRID_SIZE <= 150 else 1 
                    found = False
                    for i in range(len(X_list)):
                        for j in range(2):
                            if X_list[i][j][0] == location_x and X_list[i][j][1] == location_y and X_list[i][j][2] == size:
                                observe_turn_num = i + 1
                                chess_num = j + 1
                                found = True                               
                                break       
                        if found:
                            break
                    if chess_num != 0:
                        observe("X", observe_turn_num, location_x, location_y, size, chess_num) 
                    else:
                        print("點擊錯誤非X棋子")

        # 觀測後重啟主回合
        if observing_O or observing_X:
            observing_O = False
            observing_X = False
            running = True


main()