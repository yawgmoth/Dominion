from base import Card, ACTION, TREASURE, VICTORY, CURSE, ATTACK, REACTION


class Wharf(Card):
    price = 5
    type = ACTION 
    name = "Wharf"
    
    def play(self, player):
        player.buys += 1
        player.draw_card()
        player.draw_card()
        self.expired = False
        self.restored = False

    def perform_cleanup(self):
        if self.expired: return True
        
        return False
        
    # must be idempotent
    def start_turn(self, player):
        if self.restored: 
            self.restored = False
            return
        if not self.expired:
            player.buys += 1
            player.draw_card()
            player.draw_card()
            self.expired = True

    @classmethod
    def from_state(cls, state):
        result = cls()
        result.expired = state["expired"]
        result.restored = True
        return result
    
    def get_state(self):
        return {"expired": self.expired}
        
class DGRC(Card):
    price = 9
    type = ACTION 
    name = "DGRC"
    
    def play(self, player):       
        player.draw_card()
        player.draw_card()
        player.actions += 2
