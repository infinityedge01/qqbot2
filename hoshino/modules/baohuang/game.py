import os
import asyncio
import datetime
import random
import copy

tile_list = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2', '鬼', '保', '王', '皇']
reversed_tile_list = ['皇', '王', '保', '鬼', '2', 'A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3']
tile_order = {'3':3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K' : 13, 'A' : 14, '2': 15, '鬼': 16, '保': 16, '王': 17, '皇' : 17}

HUANGDI = 0x0001
BAOZI = 0x0010
DUBAO = 0x0011
GEMINGDANG = 0x0100
UNKNOWN = 0x0000



class Player:
    def __init__(self, group_id: int, qqid: int, last_player_id: int, next_player_id: int, table_id: int):
        self.group_id = group_id
        self.qqid = qqid
        self.last_player_id = last_player_id
        self.next_player_id = next_player_id
        self.tiles = dict(zip(tile_list, [0] * len(tile_list)))
        self.identity = UNKNOWN
        self.open_identity = UNKNOWN
        self.order = 0
        self.point = 0
        self.mutiple = 1
        self.table_id = table_id


    def get_tiles(self) -> dict:
        return copy.deepcopy(self.tiles)

    def get_tile_count(self) -> int:
        ret = 0
        for tile in tile_list:
            ret += self.tiles[tile]
        return ret
        
    def add_tile(self, tile: str) -> bool:
        if not tile in tile_list:
            return False
        self.tiles[tile] += 1
        return True
    
    def set_identity(self, identity: int) -> None:
        self.identity = identity
    
    def get_identity(self) -> int:
        return self.identity
    
    def set_open_identity(self, open_identity: int) -> None:
        self.open_identity = open_identity

    def get_open_identity(self) -> int:
        return self.open_identity
    
    def set_order(self, order: int) -> None:
        self.order = order
    
    def get_order(self) -> int:
        return self.order
    
    def double_multiply(self) -> None:
        self.mutiple *= 2
    
    def discard_tiles(self, tile_list: list) -> bool:
        tile_set = set(tile_list)
        for tile in tile_set:
            if tile_list.count(tile) > self.tiles[tile]:
                return False
        for tile in tile_set:
            self.tiles[tile] -= tile_list.count(tile)
        return True

class Table:
    def __init__(self, group_id: int, player_id: list):
        self.group_id = group_id
        self.player_id = player_id
        self.players = {}
        self.rangwei2 = 0 #当前让位所需2
        self.game_period = 0 #0 发牌 #1 抢独 #2 登基 #3 明保 #4 造反 #5 开始游戏 #6 结束游戏
        self.mutiple = 1
        self.zaofan_player = []
        self.win_player = []
        self.qipai_player = []
        self.jiefeng = 0
        self.baohuang_win = []
        self.gemingdang_win = []
        self.huangdi_id = 0
        self.baozi_id = 0
        for i in range(5):
            pre = (i + 4) % 5
            nxt = (i + 1) % 5
            self.players[player_id[i]] = Player(group_id, player_id[i], player_id[pre], player_id[nxt], i)
        
        deck = []
        for i in range(3, 13):
            for _j in range(16): deck.append(tile_list[i])
        for _j in range(3): deck.append('鬼')
        for _j in range(3): deck.append('王')
        deck.append('保')
        deck.append('皇')

        random.shuffle(deck)

        for i in range(len(deck)):
            self.players[self.player_id[i % 5]].add_tile(deck[i])
            if deck[i] == '皇': self.huangdi_id = self.player_id[i % 5]
            if deck[i] == '保': self.baozi_id = self.player_id[i % 5]
            

    #进入抢独阶段
    def qiangdu_begin(self):
        self.game_period = 1

    def qiangdu(self, qiangdu_id: int) -> bool:
        if self.game_period != 1:
            return False
        self.mutiple *= 4
        for player in self.player_id:
            if player == qiangdu_id:
                self.players[player].set_identity(DUBAO)
                self.players[player].set_open_identity(DUBAO)
            else:
                self.players[player].set_identity(GEMINGDANG)
                self.players[player].set_open_identity(GEMINGDANG)
            self.players[player].tiles['鬼'] += self.players[player].tiles['保']
            self.players[player].tiles['保'] = 0
            self.players[player].tiles['王'] += self.players[player].tiles['皇']
            self.players[player].tiles['皇'] = 0
        self.huangdi_id = qiangdu_id
        self.baozi_id = qiangdu_id
        return True

    def dengji_begin(self) -> bool:
        if self.game_period != 1:
            return False
        self.game_period = 2
        return True

    def dengji(self) -> bool:
        if self.game_period != 2:
            return False
        self.players[self.huangdi_id].set_identity(HUANGDI)
        self.players[self.huangdi_id].set_open_identity(HUANGDI)
        return True
    
    def rangwei(self) -> int:
        if self.game_period != 2:
            return -1
        if self.players[self.huangdi_id].tiles['2'] < self.rangwei2:
            return -2
        self.players[self.huangdi_id].tiles['皇'] = 0
        self.players[self.huangdi_id].tiles['2'] -= self.rangwei2
        pre = self.players[self.huangdi_id].last_player_id
        self.players[pre].tiles['皇'] = 1
        self.players[pre].tiles['2'] += self.rangwei2
        self.huangdi_id = pre
        self.rangwei2 += 1
        return 0

    def mingbao_begin(self) -> bool:
        if self.game_period != 2:
            return False
        self.game_period = 3
        return True

    def mingbao(self) -> int:
        if self.game_period != 3:
            return -1
        self.mutiple *= 2
        for player in self.player_id:
            if player != self.huangdi_id and player != self.baozi_id:
                self.players[player].set_identity(GEMINGDANG)
                self.players[player].set_open_identity(GEMINGDANG)
        if self.baozi_id == self.huangdi_id:
            self.players[self.baozi_id].set_identity(DUBAO)
            self.players[self.baozi_id].set_open_identity(DUBAO)
            return 2
        else:
            self.players[self.baozi_id].set_identity(BAOZI)
            self.players[self.baozi_id].set_open_identity(BAOZI)
            return 1
    
    def anbao(self) -> int:
        if self.game_period != 3:
            return -1
        for player in self.player_id:
            if player != self.huangdi_id and player != self.baozi_id:
                self.players[player].set_identity(GEMINGDANG)
        if self.baozi_id == self.huangdi_id:
            self.players[self.baozi_id].set_identity(DUBAO)
            return 2
        else:
            self.players[self.baozi_id].set_identity(BAOZI)
            return 1
    
    def zaofan_begin(self) -> bool:
        if self.game_period != 3:
            return False
        self.game_period = 4
        return True

    def zaofan(self, zaofan_id: int) -> int:
        if self.game_period != 4:
            return -1
        if zaofan_id == self.huangdi_id or zaofan_id == self.baozi_id:
            return -2
        if zaofan_id in self.zaofan_player:
            return -3
        self.players[zaofan_id].set_identity(GEMINGDANG)
        self.players[zaofan_id].set_open_identity(GEMINGDANG)
        self.players[zaofan_id].double_multiply()
        self.zaofan_player.append(zaofan_id)
        return len(self.zaofan_player)

    def zaofan_success(self) -> int:
        if self.game_period != 4:
            return -1
        if len(self.zaofan_player) < 2:
            return -2
        self.mutiple *= 2
        for player in self.player_id:
            if player != self.huangdi_id and player != self.baozi_id:
                self.players[player].set_identity(GEMINGDANG)
                self.players[player].set_open_identity(GEMINGDANG)
        if self.baozi_id == self.huangdi_id:
            self.players[self.baozi_id].set_identity(DUBAO)
            self.players[self.baozi_id].set_open_identity(DUBAO)
            return 2
        else:
            self.players[self.baozi_id].set_identity(BAOZI)
            self.players[self.baozi_id].set_open_identity(BAOZI)
            return 1

    def game_begin(self) -> bool:
        if self.game_period != 1 and self.game_period != 3 and self.game_period != 4:
            return False
        self.game_period = 5
        self.on_table = [[], [], [], [], []]
        self.last_tile = []
        self.last_discard = self.huangdi_id
        self.current_discard = self.huangdi_id
        return True

    def get_next_player(self) -> int:
        ret = self.players[self.current_discard].next_player_id
        while self.players[ret].get_order() > 0:
            ret = self.players[ret].next_player_id
        return ret

    def get_next_player2(self, player_id: int) -> int:
        ret = self.players[player_id].next_player_id
        while self.players[ret].get_order() > 0:
            ret = self.players[ret].next_player_id
        return ret

    def discard_tile(self, tiles: str) -> tuple:
        tiles = tiles.upper()
        lst_tiles = []
        while tiles != "":
            flag = True
            for tile in tile_list:
                if tile == '10':
                    if tiles[-2:] == '10':
                        flag = False
                        lst_tiles.append('10')
                        tiles = tiles[:-2]
                        break
                else:
                    if tiles[-1:] == tile:
                        flag = False
                        lst_tiles.append(tile)
                        tiles = tiles[:-1]
                        break
                
            if flag:
                return (-1, [])
        lst_tiles = sorted(lst_tiles, key= lambda x: tile_order[x], reverse=True)
        if len(lst_tiles) == 0:
            return (-1, [])
        if len(lst_tiles) > 1:
            for i in range(len(lst_tiles) - 1, 0, -1):
                if tile_order[lst_tiles[i - 1]] > 15:
                    break
                if tile_order[lst_tiles[i - 1]] != tile_order[lst_tiles[i]] :
                    return (-2, [])
        is_first_tile = False
        if self.last_discard == self.current_discard:
            is_first_tile = True
        if len(self.win_player) >= 1:
            if self.get_next_player2(self.win_player[-1]) == self.current_discard and self.jiefeng == 1:
                is_first_tile = True
        
        if not is_first_tile:
            if len(self.last_tile) != len(lst_tiles):
                return (-3, [])
            for i in range(len(lst_tiles)):
                if tile_order[self.last_tile[i]] >= tile_order[lst_tiles[i]]:
                    return (-3, [])
        if lst_tiles[-1] == '6' and self.players[self.current_discard].tiles['6'] != self.players[self.current_discard].get_tile_count(): 
            return (-4, [])
        is_success = self.players[self.current_discard].discard_tiles(lst_tiles)
        if not is_success:
            return (-5, [])
        self.jiefeng = 0
        self.last_tile = lst_tiles
        self.on_table[self.players[self.current_discard].table_id] = lst_tiles
        self.last_discard = self.current_discard
        if '保' in lst_tiles:
            for player in self.player_id:
                if player != self.huangdi_id and player != self.baozi_id:
                    self.players[player].set_identity(GEMINGDANG)
                    self.players[player].set_open_identity(GEMINGDANG)
            if self.baozi_id == self.huangdi_id:
                self.players[self.baozi_id].set_identity(DUBAO)
                self.players[self.baozi_id].set_open_identity(DUBAO)
            else:
                self.players[self.baozi_id].set_identity(BAOZI)
                self.players[self.baozi_id].set_open_identity(BAOZI)
            return (2, lst_tiles)
        return (1, lst_tiles)

    def pass_tile(self) -> bool:
        is_first_tile = False
        if self.last_discard == self.current_discard:
            is_first_tile = True
        if len(self.win_player) >= 1:
            if self.get_next_player2(self.win_player[-1]) == self.current_discard and self.jiefeng == 1:
                is_first_tile = True
        if is_first_tile:
            return False
        if len(self.win_player) >= 1:
            if self.get_next_player2(self.win_player[-1]) == self.current_discard and self.jiefeng == 2:
                self.jiefeng = 1
        self.on_table[self.players[self.current_discard].table_id] = []
        return True
    
    def paole(self, paole_id: int) -> bool:
        if self.players[paole_id].get_tile_count() != 0:
            return False
        self.win_player.append(paole_id)
        self.jiefeng = 2
        self.players[paole_id].set_order(len(self.win_player))
        if paole_id == self.huangdi_id or paole_id == self.baozi_id:
            self.baohuang_win.append(paole_id)
        else:
            self.gemingdang_win.append(paole_id)
        return True

    def qipai(self, qipai_id: int) -> bool:
        if self.current_discard == qipai_id or self.last_discard == qipai_id:
            return False
        if self.players[qipai_id].get_order() != 0:
            return False
        self.qipai_player.append(qipai_id)
        self.players[qipai_id].set_order(6 - len(self.qipai_player))
        return True

    def is_game_end(self) -> bool:
        if len(self.win_player) + len(self.qipai_player) >= 4:
            return True
        if self.mutiple == 4:
            if len(self.baohuang_win) >= 1 or len(self.gemingdang_win) >= 1:
                return True
            else: return False
        if self.huangdi_id == self.baozi_id:
            if len(self.baohuang_win) >= 1 or len(self.gemingdang_win) >= 2:
                return True
            else: return False
        if len(self.baohuang_win) == 2 or len(self.gemingdang_win) == 3:
            return True
        else: return False

    def game_end(self) -> bool:
        # if not self.is_game_end(): return False
        cnt = 0
        for player in self.player_id:
            if player != self.huangdi_id and player != self.baozi_id:
                self.players[player].set_identity(GEMINGDANG)
                self.players[player].set_open_identity(GEMINGDANG)
        if self.baozi_id == self.huangdi_id:
            self.players[self.baozi_id].set_identity(DUBAO)
            self.players[self.baozi_id].set_open_identity(DUBAO)
        else:
            self.players[self.baozi_id].set_identity(BAOZI)
            self.players[self.baozi_id].set_open_identity(BAOZI)
        while cnt < 5:
            cnt += 1
            if self.players[self.current_discard].get_order() == 0:
                self.win_player.append(self.current_discard)
                self.players[self.current_discard].set_order(len(self.win_player))
            self.current_discard = self.players[self.current_discard].next_player_id
        self.game_period = 6
        return True